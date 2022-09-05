import base64
import io
import os
import pickle

import requests
from cv2 import imencode
from kivy.core.image import Image as CoreImage
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from databasecontentbox import DatabaseContentBox
from databaseitem import FaceObjectWidget

Builder.load_file('databaseview.kv')

class DatabaseView(BoxLayout):

    faces = ListProperty([])
    manager = ObjectProperty(None)
    databaseListBox = ObjectProperty(None)
    databaseContentBox = ObjectProperty(None)
    serverAddress = ''

    def on_parent(self, *args):
        self.refresh()
        if self.parent != None:
            try:
                faces = self.get_faces()
                if len (faces) > 0:
                    # Faces exist in database
                    self.databaseContentBox.no_selection_config(text = 'Select Face for Info...')
                    self.show_faces(self.databaseListBox.databaseListLayout, faces)
                else:
                    # Face does no exist
                    self.databaseContentBox.no_selection_config(text = 'No Face Found, Add Face to Database...')
            except Exception as e:
                print (f'get_faces {e}')
                self.databaseContentBox.no_selection_config(text = 'Unable to Connect to Database...')


    def add_to_list(self, data_list): 
        # draw the new data to the face database list box object 
        self.ids.database_list_box.add_item(data_list = data_list)

    def add_new_data(self, image_folder, data_list):
        #self.add_to_database(database = self.datadict, data_list = data_list)
        self.add_to_list(image_folder = image_folder, string_data_list = data_list[0:3])

    # def display_data_content(self, selected_data):
    #     # Display selected data in database list layout to database info box. 
    #     # selected_data is DatabaseItem object
    #     face = self.faceDict[selected_data.id]
    #     self.ids.database_info_box.display_data(data_content = face)

    def check_id_exist(self, new_id):
        print (f'CHECK ID: {new_id}')
        for key in self.faceDict.keys():
            if self.faceDict[key]['faceID'] == new_id:
                print (f'ID {new_id} already exist. Try new ID...')
                return True
        return False

    # def create_face_image(self, face_data_str, file_path):
    #     # Create db face image to temp folder
    #     try:
    #         # Restore numpy array image
    #         img = pickle.loads(base64.b64decode(face_data_str))
    #         # Write to file
    #         if (imwrite(file_path, img)):
    #             return True
    #         else:
    #             print ('Error when writing db face image to temp folder')
    #             return False
    #     except Exception as e:
    #         print (e)

    # def clear_images(self, images_location = '', grid_layout = None):
    #     # Removing image files in temp preview directory 
    #     if images_location != '':
    #         images = os.listdir(images_location)
    #         for image in images:
    #             os.remove(os.path.join(images_location, image))
    #     # Clearing displayed images in image viewer grid layout
    #     if grid_layout:
    #         grid_layout.clear_widgets()
    #         grid_layout.nLive = 0

    # def display_face(self, face_response):
        # Clearing images in database list layout and temp directory 
        # Clearing layout
        # self.databaseListLayout.clear_widgets()
        # self.clear_images(images_location = self.faceImgTempDir, grid_layout = self.ids.database_list_box.databaseListLayout)
        # Start displaying face
        # for face in face_response:
        #     id = face['id']
        #     faceID = face['faceID']
        #     firstName = face['firstName']
        #     lastName = face['lastName']
        #     faceDataStr = face['faceData']
        #     # Processing image data
        #     faceDataNp = pickle.loads(base64.b64decode(faceDataStr))
        #     _, faceDataBytes = imencode(".jpg", faceDataNp)
        #     coreImg = CoreImage(io.BytesIO(faceDataBytes), ext = 'jpg')
        # widget.add_item(id = id, str_datalist = str_datalist, face_texture = coreImg.texture)

        #     self.add_to_list(data_list)

        # for id in faceDict.keys():
        #     id = faceDict[id]['id']
        #     faceID = faceDict[id]['faceID']
        #     firstName = faceDict[id]['firstName']
        #     lastName = faceDict[id]['lastName']
        #     faceDataStr = faceDict[id]['faceData']
        #     # Create db face image to temp folder, use id-faceID as file name
        #     filePath = f'{self.faceImgTempDir}{id}_{faceID}.png'
        #     if self.create_face_image(faceDataStr, file_path = filePath):
        #         # Face image created. Display it
        #         data_list = [id, faceID, firstName, lastName, filePath]
        #     else:
        #         # Face image not created. Dont display it
        #         data_list = [id, faceID, firstName, lastName, None]
        #     self.add_to_list(data_list)

    # def get_face(self):
    #     # Get the faces from database in the server and return faceDict dictionary
    #     # faceDict will be dict of dict
    #     # faceDict = {}
    #     try:
    #         # Sending request
    #         r = requests.get(f"{self.serverAddress}/api/face")
    #         # Getting and parsing response
    #         face_response = r.json()  # Produce list of dict
    #         # for face in face_response:
    #         #     # Put into faceDict
    #         #     faceDict[face['id']] = face
    #         return face_response
    #     except Exception as e:
    #         print (e)
    #         return None

    def get_faces(self):
        # Retrieve devices from server REST API
        #try:
        # Sending request
        r = requests.get(f"{self.serverAddress}/api/face")
        face_response = r.json()  # Produce list of dict
        for face in face_response:
            id = face['id']
            faceID = face['faceID']
            firstName = face['firstName']
            lastName = face['lastName']
            faceDataStr = face['faceData']
            faceDataNp = pickle.loads(base64.b64decode(faceDataStr))
            _, faceDataBytes = imencode(".jpg", faceDataNp)
            coreImg = CoreImage(io.BytesIO(faceDataBytes), ext = 'jpg')
            self.faces.append(
                FaceObjectWidget(
                    id = id,
                    str_datalist= [faceID, firstName, lastName],
                    img_datalist = faceDataNp,
                    face_texture = coreImg.texture)
            )
        return self.faces
        # except Exception as e:
        #     print (f'get_faces: {e}')
        #     self.databaseContentBox.no_selection_config(text = 'Unable to connect to database...')
        # finally:
        #     return self.faces

    def show_faces(self, layout, face_widget_list):
        # Populate items to a list widget
        for faceWidget in face_widget_list:
            layout.add_widget(faceWidget)

    def refresh(self):
        self.faces.clear()
        self.databaseListBox.databaseListLayout.clear_widgets()
        self.databaseContentBox.clear_widgets()

    def update_database_item(self, new_data):
        # Get current data
        for face in self.faces:
            if face.id == new_data['id']:
                # Update the device property except its hostname (not changeable)
                face.dataID = new_data['faceID']
                face.dataFirstName = new_data['firstName']
                face.dataLastName = new_data['lastName']
                self.databaseContentBox.change_config(face)

    # def get_and_display_face(self):
    #     face_response = self.get_face()
    #     if face_response:
    #         self.display_face(face_response)
    
    def remove_from_db(self, id):
        try:
            r = requests.delete(f"{self.serverAddress}/api/face/{id}/")
            response = r.status_code
            print (f'Status code: {response}')
            self.get_and_display_face()
        except Exception as e:
            print (e)

    def get_server_address(self):
        try:
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                self.serverAddress = pickle.load(file)
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')

    def __init__(self, server_address_file='data/serveraddress.p', **kwargs):
        super().__init__(**kwargs)
        # Getting the server adrress, deserialize the serveraddress.p
        self.serverAddressFile = server_address_file
