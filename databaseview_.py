import base64
import os
import pickle

import requests
from cv2 import imwrite
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

Builder.load_file('databaseview.kv')

class DatabaseView(BoxLayout):

    manager = ObjectProperty(None)
    databaseListLayout = ObjectProperty(None)
    faceImgTempDir = 'images/temp/face/'
    serverAddress = ''

    def on_parent(self, *args):
        if self.parent != None:
            print ('On Parent')
            self.get_and_display_face()

    def add_to_list(self, data_list): 
        # draw the new data to the face database list box object 
        self.ids.database_list_box.add_item(data_list = data_list)

    def add_new_data(self, image_folder, data_list):
        #self.add_to_database(database = self.datadict, data_list = data_list)
        self.add_to_list(image_folder = image_folder, string_data_list = data_list[0:3])

    def display_data_content(self, selected_data):
        # Display selected data in database list layout to database info box. 
        # selected_data is DatabaseItem object
        face = self.faceDict[selected_data.id]
        self.ids.database_info_box.display_data(data_content = face)

    def check_id_exist(self, new_id):
        print (f'CHECK ID: {new_id}')
        for key in self.faceDict.keys():
            if self.faceDict[key]['faceID'] == new_id:
                print (f'ID {new_id} already exist. Try new ID...')
                return True
        return False

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

    def clear_images(self, images_location = '', grid_layout = None):
        # Removing image files in temp preview directory 
        if images_location != '':
            images = os.listdir(images_location)
            for image in images:
                os.remove(os.path.join(images_location, image))
        # Clearing displayed images in image viewer grid layout
        if grid_layout:
            grid_layout.clear_widgets()
            grid_layout.nLive = 0

    def display_face(self, faceDict):
        # Clearing images in database list layout and temp directory 
        self.clear_images(images_location = self.faceImgTempDir, grid_layout = self.ids.database_list_box.databaseListLayout)
        # Start displaying face
        for id in faceDict.keys():
            id = faceDict[id]['id']
            faceID = faceDict[id]['faceID']
            firstName = faceDict[id]['firstName']
            lastName = faceDict[id]['lastName']
            faceDataStr = faceDict[id]['faceData']
            # Create db face image to temp folder, use id-faceID as file name
            filePath = f'{self.faceImgTempDir}{id}_{faceID}.png'
            if self.create_face_image(faceDataStr, file_path = filePath):
                # Face image created. Display it
                data_list = [id, faceID, firstName, lastName, filePath]
            else:
                # Face image not created. Dont display it
                data_list = [id, faceID, firstName, lastName, None]
            self.add_to_list(data_list)

    def get_face(self):
        # Get the faces from database in the server and return faceDict dictionary
        # faceDict will be dict of dict
        faceDict = {}
        try:
            # Sending request
            r = requests.get(f"{self.serverAddress}/api/face")
            # Getting and parsing response
            face_response = r.json()  # Produce list of dict
            for face in face_response:
                # Put into faceDict
                faceDict[face['id']] = face
        except Exception as e:
            print (e)
        finally:
            print ('GET face database OK')
            return faceDict

    def get_and_display_face(self):
        self.faceDict = self.get_face()
        self.display_face(self.faceDict)
    
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