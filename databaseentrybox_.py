import os
import uuid
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.clock import Clock
from tkinter import Tk, filedialog

import numpy as np
from cv2 import imwrite
import requests
import json
import pickle
import base64

Builder.load_file('databaseentrybox.kv')

class DatabaseEntryBox(FloatLayout):

    newID = ''  # New ID
    newFirstName = ''   # New first name
    newLastName = ''    # New last name
    newFaceData = []    # New face data list
    newFaceVector = None # New face vector

    manager = ObjectProperty(None)
    selectedPath = ''   # Selected image folder path
    selectFolderButton = ObjectProperty(None)
    imageReviewButton = ObjectProperty(None)
    imageLocationText = ObjectProperty(None)
    statusLabel = ObjectProperty(None)
    previewImageLocation = 'images/temp/preview/'
    isDataComplete = False
    aiModel = None
    serverAddressFile = ''

    def __init__(self, server_address_file='data/serveraddress.p', **kwargs):
        super().__init__(**kwargs)
        # Getting the server adrress, deserialize the serveraddress.p
        self.serverAddressFile = server_address_file

    def button_press_callback(self, widget):
        if widget == self.selectFolderButton:
            widget.source = "images/selectfile_down.png"
        elif widget == self.imageReviewButton:
            widget.source = "images/imagereviewbutton_down.png"
        elif widget == self.ids.review_ok_button:
            widget.source = "images/image_review_ok_button_down.png"
        elif widget == self.ids.review_cancel_button:
            widget.source = "images/image_review_cancel_button_down.png"
    
    def button_release_callback(self, widget):
        if widget == self.selectFolderButton:
            widget.source = "images/selectfile.png"
        elif widget == self.imageReviewButton:
            widget.source = "images/imagereviewbutton_normal.png"
        elif widget == self.ids.review_ok_button:
            widget.source = "images/image_review_ok_button_normal.png"
        elif widget == self.ids.review_cancel_button:
            widget.source = "images/image_review_cancel_button_normal.png"
    
    def show_load_dialog(self, widget):
        root = Tk()
        root.withdraw()
        dirname = filedialog.askdirectory()
        root.destroy()
        if dirname:
            self.load_dir(dirname)

    def load_dir(self, dirname):
        # get selection
        self.ids.image_location_text.text = dirname

    def validate_entry(self, *args):
        isValid = True
        for entry in args:    
            if entry.text == '':
                isValid = False
                entry.background_color = (0.9, 0.7, 0.7)
                #entry.hint_text_color = (0.9, 0.2, 0.2)
                if entry == self.ids.new_id_text:
                    entry.hint_text = 'Enter ID...'
                elif entry == self.ids.first_name_text:
                    entry.hint_text = 'Enter first name...'
                elif entry == self.ids.last_name_text:
                    entry.hint_text = 'Enter last name...'
            else:
                entry.foreground_color = (0.2, 0.2, 0.2)
                entry.background_color = (0.8, 0.8, 0.8)
                #self.reset_hint_text(entry)

        return isValid

    def check_id_exist(self, new_id):
        # Execute function in databaseview module
        return self.manager.mainTabs.databaseView.check_id_exist(new_id)

    def get_entry(self, *args):
        isValid = True
        if self.validate_entry(*args) == True:
            if not self.check_id_exist(self.ids.new_id_text.text):   # Check for existing same ID
                self.newID = self.ids.new_id_text.text
                self.newFirstName = self.ids.first_name_text.text
                self.newLastName = self.ids.last_name_text.text
                self.selectedPath = self.ids.image_location_text.text
                return isValid
            else:
                isValid = False
                self.ids.new_id_text.background_color = (0.9, 0.7, 0.7)
                self.ids.new_id_text.text = ''
                self.ids.new_id_text.hint_text = 'ID already exist. Enter New ID'
                return isValid
        else:
            # Put error message here
            isValid = False
            print ('Some entry is not valid')
            return isValid

    def preview_data(self, *args):
        # Callback funciton for "Data Review Button"
        if self.get_entry(*args):
            self.imageReviewButton.disabled = True
            self.display_status(self.statusLabel, 'loading images...')
            Clock.schedule_once(self.display_preview_data, 0)

    def display_preview_data(self, *args):
        if not (self.aiModel):
            self.aiModel = self.create_vision_ai()
        # Clear previous data in the preview directory and clear delete list anyway
        self.clear_images(self.previewImageLocation, self.ids.review_image_grid)
        # Process the data for review
        if (os.path.isdir(self.selectedPath)):
        # Data path is valid and image file exist
            # Show string data
            self.add_text_on_widget(self.ids.review_data_label, f'{self.newID}, {self.newFirstName} {self.newLastName}')  # Printing label to image viewer box
            # Get list of face data
            self.newFaceData = self.create_face_data(self.selectedPath)
            # Create face vector
            self.newFaceVector = self.aiModel.create_mean_face_vector(self.newFaceData)
            # Show face image to preview
            if self.create_face_image_file(self.newFaceData, self.previewImageLocation) and np.any(self.newFaceVector):
                # Detection exist
                self.isDataComplete = True
                self.hide_no_face()
                self.draw_image_to_grid(imagePath = self.previewImageLocation, gridLayout = self.ids.review_image_grid)
            else:
                # Detection not exist
                self.isDataComplete = False
                self.add_text_on_widget(self.ids.review_data_label, 'Face Not Detected')  # Printing label to image viewer box
                self.display_no_face()
        else:
            print ('Unable to process. Invalid path or empty folder')
        
        self.display_status(self.statusLabel, '')
        self.imageReviewButton.disabled = False
        
    def create_vision_ai(self):
        return App.get_running_app().manager.create_vision_ai()

    def add_text_on_widget(self, widget, text):
        widget.text = text

    def create_face_data(self, files_location):
        # Create list of face data from files in files_location
        if (os.path.isdir(files_location)):
            # Data path is valid and image file exist
            imageFiles = os.listdir(files_location)
            # Detect face in every image
            faceList = []
            for imageFile in imageFiles:
                filePath = os.path.join(files_location, imageFile)
                face = self.aiModel.extract_primary_face(detector_type = 2, image_path = filePath)
                if np.any(face):
                    # Append to face list
                    faceList.append(face)
            return faceList

    def create_face_image_file(self, face_list, save_location):
        # Create image files from list of face data
        for face in face_list:
            fileName = uuid.uuid4()        # Random file name
            writePath = (f'{save_location}{fileName}.png')
            imwrite(writePath, face)
        if len(os.listdir(save_location)) > 0:
            return True
        return False

    def draw_image_to_grid(self, imagePath, gridLayout):
        # Locate and adding images
        imageFiles = os.listdir(imagePath)
        if len(imageFiles)>0:
            for imageFile in imageFiles:
                gridLayout.add_widget(Image(source = os.path.join(imagePath, imageFile), size_hint = (None, 1)))

    def clear_images(self, imagesLocation = '', gridLayout = None):
        # Removing image files in temp preview directory 
        if imagesLocation != '':
            images = os.listdir(imagesLocation)
            for image in images:
                os.remove(os.path.join(imagesLocation, image))
        # Clearing displayed images in image viewer grid layout
        if gridLayout:
            gridLayout.clear_widgets()
            gridLayout.nLive = 0

    def display_status(self, label, text,*args):
        label.text = text

    def display_no_face(self):
        self.ids.no_face_image.opacity = 1

    def hide_no_face(self):
        self.ids.no_face_image.opacity = 0

    def clear_text(self, text_widgets):
        for text_widget in text_widgets:
            text_widget.text = ''
            text_widget.background_color = (0.8, 0.8, 0.8)

    def reset_hint_text(self, entry):
        if entry == self.ids.new_id_text:
            entry.hint_text = 'New ID'
        elif entry == self.ids.first_name_text:
            entry.hint_text = 'First Name'
        elif entry == self.ids.last_name_text:
            entry.hint_text = 'Last Name'

    def reset_all_hint_text(self):
        self.ids.new_id_text.hint_text = 'New ID'
        self.ids.first_name_text.hint_text = 'First Name'
        self.ids.last_name_text.hint_text = 'Last Name'
        
    def reset_data(self):
        self.clear_images(self.previewImageLocation, self.ids.review_image_grid)
        self.clear_text([self.ids.new_id_text, self.ids.first_name_text, self.ids.last_name_text, self.ids.image_location_text])
        self.reset_all_hint_text()
        self.display_no_face()
        self.add_text_on_widget(self.ids.review_data_label, '...') 
        self.isDataComplete = False

    def get_server_address(self):
        try:
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                serverAddress = pickle.load(file)
                return serverAddress
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')
            return None

    def add_to_database(self, *args):
        # Run the function in databaseView object
        if self.isDataComplete:
            data = {'faceID' : self.newID,
                    'firstName' : self.newFirstName,
                    'lastName' : self.newLastName,
                    'faceVector' : base64.b64encode(pickle.dumps(self.newFaceVector)).decode('ascii'),
                    'faceData' : base64.b64encode(pickle.dumps(self.newFaceData[0])).decode('ascii')}
            serverAddress = self.get_server_address()
            r = requests.post(f"{serverAddress}/api/face/", json = data)
            # Show new data to the database list layout
            self.manager.mainTabs.databaseView.get_and_display_face()
            self.reset_data()
        else:
            print ('Data not complete. Not able to add to database')