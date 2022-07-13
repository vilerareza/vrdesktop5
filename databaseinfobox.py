import os
import pickle
import base64
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image

import numpy as np
from cv2 import imwrite

Builder.load_file('databaseinfobox.kv')

class DatabaseInfoBox(BoxLayout):

    dataContent = []

    imgTempDir = 'images/temp/content/'

    def display_data(self, data_content):
        '''
        data_content is dictionary with keys: id, faceID, firstName, faceVector, faceData
        '''
        self.dataContent = data_content
        # Clearing images in grid layout and temp storage
        self.clear_images(self.imgTempDir, self.ids.data_image_grid)
        # Creating images from faceData in dataContent
        filePath = f"{self.imgTempDir}{self.dataContent['id']}_{self.dataContent['faceID']}.png"        
        self.create_face_image(face_data_str = self.dataContent['faceData'], file_path = filePath)
        # Displaying data
        self.ids.data_id_text.text = self.dataContent['faceID']
        self.ids.data_firstname_text.text = self.dataContent['firstName']
        self.ids.data_lastname_text.text = self.dataContent['lastName']
        self.draw_image_to_grid(imagePath = self.imgTempDir, gridLayout = self.ids.data_image_grid)
        
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
    
    def create_face_image(self, face_data_str, file_path):
        # Create db face image to temp folder
        try:
            # Restore numpy array image
            img = pickle.loads(base64.b64decode(face_data_str))
            # Write to file
            if (imwrite(file_path, img)):
                return True
            else:
                print ('Error when writing db face image to temp folder')
                return False
        except Exception as e:
            print (e)

    def draw_image_to_grid(self, imagePath, gridLayout):
        # Locate and adding images
        imageFiles = os.listdir(imagePath)
        if len(imageFiles)>0:
            for imageFile in imageFiles:
                gridLayout.add_widget(Image(source = os.path.join(imagePath, imageFile), size_hint = (None, 1)))

    def button_press_callback(self, widget):
        if widget == self.ids.data_delete_button:
            widget.source = "images/databaseview/database_delete_down.png"
        elif widget == self.ids.data_edit_button:
            widget.source = "images/databaseview/database_new_down.png"

    def button_release_callback(self, widget):
        if widget == self.ids.data_delete_button:
            widget.source = "images/databaseview/database_delete_normal.png"
        elif widget == self.ids.data_edit_button:
            widget.source = "images/databaseview/database_new_normal.png"