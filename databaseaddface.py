import os
import io
import requests
import pickle
import base64
import json
from functools import partial

from cv2 import imencode
import numpy as np

from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImg
from kivy.clock import Clock
from tkinter import Tk, filedialog

Builder.load_file("databaseaddface.kv")

class DatabaseAddFace(FloatLayout):
    
    titleLabelText = 'Add New Face'
    titleLabel = ObjectProperty(None)
    faceIDText = ObjectProperty(None)
    faceFirstNameText = ObjectProperty(None)
    faceLastNameText = ObjectProperty(None)
    imgFileText = ObjectProperty(None)
    btnSelectImg = ObjectProperty(None)
    btnReview = ObjectProperty(None)
    btnCancel = ObjectProperty(None)
    btnSave = ObjectProperty(None)
    reviewImgGrid = ObjectProperty(None)
    reviewDataLabel = ObjectProperty(None)
    imgNoFace = ObjectProperty(None)

    #aiModel = None
    isDataComplete = BooleanProperty(False)

    def button_press_callback(self, button):
        if button == self.btnSelectImg:
            button.source = 'images/databaseview/selectfile_down.png'
        elif button == self.btnReview:
            button.source = 'images/databaseview/btn_review_down.png'
        elif button == self.btnCancel:
            button.source = 'images/databaseview/btn_cancel_down.png'
        elif button == self.btnSave:
            button.source = 'images/databaseview/btn_save_down.png'

    def button_release_callback(self, button):
        if button == self.btnSelectImg:
            button.source = 'images/databaseview/selectfile.png'
            self.select_img_file()
        elif button == self.btnReview:
            button.source = 'images/databaseview/btn_review.png'
        elif button == self.btnCancel:
            button.source = 'images/databaseview/btn_cancel.png'
            self.parent.no_selection_config()
        elif button == self.btnSave:
            button.source = 'images/databaseview/btn_save.png'
            self.add_to_db()

    def select_img_file(self):
        root = Tk()
        root.withdraw()
        dirname = filedialog.askdirectory()
        root.destroy()
        if dirname:
            # get selection
            self.imgFileText.text = dirname

    def refresh(self):
        self.faceIDText.text = ''
        self.faceIDText.background_color = (1, 1, 1)
        self.faceFirstNameText.text = ''
        self.faceFirstNameText.background_color = (1, 1, 1)
        self.faceLastNameText.text = ''
        self.faceLastNameText.background_color = (1, 1, 1)
        self.imgFileText.text = ''
        self.imgFileText.background_color = (1, 1, 1)
        self.reviewDataLabel.text = '...'
        self.reviewImgGrid.clear_widgets()
        self.isDataComplete = False
        self.display_no_face(True)

    def get_server_address(self):
        try:
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                serverAddress = pickle.load(file)
                return serverAddress
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')
            return None

    def on_parent(self, *args):
        self.refresh()

    def validate_entry(self, *args):
        isValid = True
        for entry in args:    
            if entry.text == '':
                isValid = False
                entry.background_color = (0.9, 0.7, 0.7)
            else:
                entry.background_color = (1, 1, 1)
        return isValid

    def check_id_exist(self, new_id):
        return False
        # Execute function in databaseview module
        # return self.manager.mainTabs.databaseView.check_id_exist(new_id)

    def get_entry(self, *args):
        isValid = True
        faceID = ''
        firstName = ''
        lastName = ''
        imgDir = ''
        if self.validate_entry(*args):
            if not self.check_id_exist(self.faceIDText.text):   # Check for existing same ID
                # Preparing data
                faceID = self.faceIDText.text
                firstName  = self.faceFirstNameText.text
                lastName = self.faceLastNameText.text
                imgDir = self.imgFileText.text
            else:
                isValid = False
                self.faceIDText.background_color = (0.9, 0.7, 0.7)
                self.faceIDText.text = ''
                self.faceIDText.hint_text = 'ID already exist. Enter New ID'
        else:
            # Put error message here
            isValid = False
            print ('Some entry is not valid')
        return isValid, faceID, firstName, lastName, imgDir

    def create_face_data(self, files_loc, ai_model):
        # Create list of face data from files in files_location
        faceList = []
        if (os.path.isdir(files_loc)):
            # Data path is valid and image file exist
            imageFiles = os.listdir(files_loc)
            # Detect face in every image
            for imageFile in imageFiles:
                filePath = os.path.join(files_loc, imageFile)
                face = ai_model.extract_primary_face(detector_type = 2, image_path = filePath)
                if np.any(face):
                    # Append to face list
                    faceList.append(face)
            return faceList

    def display_no_face(self, display = True):
        if display:
            self.imgNoFace.opacity = 1
        else:
            self.imgNoFace.opacity = 0

    def display_img(self, np_img_list):
        for img in np_img_list:
            _, faceDataBytes = imencode(".jpg", img)
            coreImg = CoreImg(io.BytesIO(faceDataBytes), ext = 'jpg')
            # Creating and adding image object to face image layout
            self.reviewImgGrid.add_widget(
                Image(
                    texture = coreImg.texture,
                    size_hint = (None, 1)
                    )
            )

    def preview_face(self, *args, **kwargs):
        # Create AI model
        aiModel = self.create_vision_ai()
        if aiModel:
            # Clear previous images
            self.reviewImgGrid.clear_widgets()
            # Process the data for review
            if (os.path.isdir(kwargs['imgDir'])):
            # Data path is valid and image file exist
                # Get list of face data
                newFaceData = self.create_face_data(kwargs['imgDir'], aiModel)
                if len(newFaceData) > 0:
                    # Face detected
                    self.newFaceData = newFaceData
                    # Create face vector
                    self.newFaceVector = aiModel.create_mean_face_vector(newFaceData)
                    # Hide no face image
                    self.display_no_face(False)
                    # Show string data
                    self.reviewDataLabel.text = f"{kwargs['faceID']}, {kwargs['firstName']} {kwargs['lastName']}"
                    # Display images
                    self.display_img(self.newFaceData)
                    self.isDataComplete = True
                else:
                    # Unable to find face
                    self.isDataComplete = False
                    self.reviewDataLabel.text = 'Face Not Detected'
                    # Show no face image
                    self.display_no_face(True)
            else:
                self.reviewDataLabel.text = 'Image File Not Valid'
                # Show no face image
                self.display_no_face(True)
        else:
            # AI model not found
            self.reviewDataLabel.text = 'AI Model Failure'

        # Enabling the review button
        self.btnReview.disabled = False

    def preview_data(self, *args):
        isValid, faceID, firstName, lastName, imgDir = self.get_entry(*args)
        if isValid:
            self.newFaceID = faceID
            self.newFirstName = firstName
            self.newLastName = lastName
            self.btnReview.disabled = True
            self.reviewDataLabel.text = 'Detecting Faces...'
            Clock.schedule_once(
                partial(
                    self.preview_face,
                    isValid=isValid,
                    faceID = faceID,
                    firstName = firstName,
                    lastName = lastName,
                    imgDir = imgDir
                    ),
                0)

    def create_vision_ai(self):
        try:
            from ai_model import AIModel
            aiModel = AIModel(recognition = True, model_location = 'model/vgg_model_loaded.h5')
            return aiModel
            print ('model created')
        except Exception as e:
            print (f'Error on activating Vision AI {e}')
            return None

    def add_to_db(self):
        # Run the function in databaseView object
        if self.isDataComplete:
            requestData = {'faceID' : self.newFaceID,
                    'firstName' : self.newFirstName,
                    'lastName' : self.newLastName,
                    'faceVector' : base64.b64encode(pickle.dumps(self.newFaceVector)).decode('ascii'),
                    'faceData' : base64.b64encode(pickle.dumps(self.newFaceData)).decode('ascii')}
            serverAddress = self.get_server_address()
            try:
                r = requests.post(f"{serverAddress}/api/face/", json = requestData)
                response = r.status_code
                print (f'Status code: {response}')
                # Response by status code
                if response == 201:
                    self.parent.request_parent_refresh()
                else:
                    pass
                    #print (f'Name {device_name} already exist. Device not created')
            except Exception as e:
                print(f'add_to_db: {e}')
        else:
            print ('Data not complete. Not able to add to database')

    def __init__(self, server_address_file='data/serveraddress.p', **kwargs):
        super().__init__(**kwargs)
        # Getting the server adrress
        self.serverAddressFile = server_address_file
