import os
import io
import requests
import pickle
from cv2 import imencode
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.properties import ObjectProperty, BooleanProperty

Builder.load_file('databasecontentface.kv')

class DatabaseContentFace(FloatLayout):

    faceIDText = ObjectProperty(None)
    faceFirstNameText = ObjectProperty(None)
    faceLastNameText = ObjectProperty(None)
    faceImageLayout = ObjectProperty(None)
    btnSaveEdit = ObjectProperty(None)
    btnRemove = ObjectProperty(None)
    editMode = BooleanProperty(False)
    faceContent = []

    def get_face_obj(self, face_obj):
        # Getting face object data and store it to self properties
        self.id = face_obj.id
        self.faceID = str(face_obj.dataID)
        self.faceFirstName = face_obj.dataFirstName
        self.faceLastName = face_obj.dataLastName
        self.imgDataList = face_obj.imgDataList
       
    def fill(self, face_obj):
        # Getting object data
        self.get_face_obj(face_obj)
        # Filling widgets
        self.faceIDText.text = self.faceID
        self.faceFirstNameText.text = self.faceFirstName
        self.faceLastNameText.text = self.faceLastName
        # Displaying images
        self.clear_images()
        self.display_images(self.imgDataList)

    def clear_images(self):
        self.faceImageLayout.clear_widgets()
        
    def display_images(self, img_data_list):
        for imgData in img_data_list:
            _, faceDataBytes = imencode(".jpg", imgData)
            coreImg = CoreImage(io.BytesIO(faceDataBytes), ext = 'jpg')
            # Creating and adding image object to face image layout
            self.faceImageLayout.add_widget(
                Image(
                    texture = coreImg.texture,
                    size_hint = (None, 1)
                    )
                )

    def save_change_to_db(self):

        # '''child function to retrieve devices from server REST API. Return dict'''
        def get_face_detail(server_address, id):
            try:
                r = requests.get(f"{server_address}/api/face/{id}/")
                face = r.json()
                return face
            except Exception as e:
                print (e)
                return {}

        try:
            # User pressed "Save"
            id = self.id
            newFaceID = self.faceIDText.text
            newFaceFirstName = self.faceFirstNameText.text
            newFaceLastName = self.faceLastNameText.text
            newData = {'faceID': newFaceID, 'firstName': newFaceFirstName, 'lastName': newFaceLastName}
            serverAddress = self.get_server_address()
            r = requests.put(f"{serverAddress}/api/face/{id}/", data = newData)
            if r.status_code == 200:
                # Get the new device attribute (json) form the sever
                newFace = get_face_detail(serverAddress, id)
                # Update the current deviceitem
                self.parent.update_database_item(newFace)

        except Exception as e:
            print (f'save_change_db: {e}')

    def get_server_address(self):
        try:
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                serverAddress = pickle.load(file)
                return serverAddress
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')
            return None

    def toggle_press_callback(self, button):
        '''callback function for edit/save button'''
        if button == self.btnSaveEdit:
            if button.state == 'down':
                self.editMode = True
                button.source = 'images/databaseview/btn_save.png'
            else:
                self.editMode = False
                button.source = 'images/databaseview/btn_edit.png'
                # Trigger saving to database
                self.save_change_to_db()

    def button_press_callback(self, widget):
        if widget == self.btnRemove:
            widget.source = 'images/databaseview/btn_remove_down.png'

    def button_release_callback(self, widget):
        if widget == self.btnRemove:
            widget.source = 'images/databaseview/btn_remove.png'
    
    def __init__(self, server_address_file='data/serveraddress.p', **kwargs):
        super().__init__(**kwargs)
        # Getting the server adrress
        self.serverAddressFile = server_address_file