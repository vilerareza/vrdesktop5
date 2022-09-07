import base64
import io
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

    # def check_id_exist(self, new_id):
    #     print (f'CHECK ID: {new_id}')
    #     for key in self.faceDict.keys():
    #         if self.faceDict[key]['faceID'] == new_id:
    #             print (f'ID {new_id} already exist. Try new ID...')
    #             return True
    #     return False

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
            # Take image in index 0 only
            _, faceDataBytes = imencode(".jpg", faceDataNp[0])
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

    def update_database_item(self, new_data):
        # Get current data
        for face in self.faces:
            if face.id == new_data['id']:
                # Update the device property except its hostname (not changeable)
                face.dataID = new_data['faceID']
                face.dataFirstName = new_data['firstName']
                face.dataLastName = new_data['lastName']
                self.databaseContentBox.change_config(face)

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
