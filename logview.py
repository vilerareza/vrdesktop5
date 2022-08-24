import io
import base64
import pickle
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage

import numpy as np
from cv2 import imencode

import requests

Builder.load_file('logview.kv')

class LogView(BoxLayout):

    manager = ObjectProperty(None)
    # Server
    serverAddress = ''

    def on_parent(self, *args):
        logs_faceID = self.get_log()
        self.display_log(logs_faceID)

    def get_log(self):
        try:
            # Sending request
            r = requests.get(f"{self.serverAddress}/api/log/faceid/")
            # Getting and parsing response
            log_response = r.json()  # Produce list of dict
            print ('GET log OK')
            return log_response
        except Exception as e:
            print (e)
            return []

    def clear_layout(self, layout):
        layout.clear_widgets()

    def display_log(self, log):
        # Clearing log grid layout
        self.clear_layout(self.ids.logfaceobject_box.stackLayout)
        faceids = self.get_logs_faceids(log)
        print (f'FACEIDS: {len(faceids)}')
        for id in faceids:
            # Sending request
            r = requests.get(f"{self.serverAddress}/api/face/{id}")
            face_response = r.json()
            self.show_faceobject(self.ids.logfaceobject_box, faceobject_data=face_response)

    def show_faceobject(self, widget, faceobject_data):
        '''Display face object in the widget'''
        id = faceobject_data['id']
        str_datalist = [
            faceobject_data['faceID'], 
            faceobject_data['firstName'],
            faceobject_data['lastName']
            ]
        faceDataStr = faceobject_data['faceData']
        faceDataNp = pickle.loads(base64.b64decode(faceDataStr))
        _, faceDataBytes = imencode(".jpg", faceDataNp)
        coreImg = CoreImage(io.BytesIO(faceDataBytes), ext = 'jpg')
        widget.add_item(id = id, str_datalist = str_datalist, face_texture = coreImg.texture)

    def get_log_attributes(self, face_id):
        return self.manager.get_log_attributes(face_id)

    def get_database(self):
        # Get database from manager
        return self.manager.get_facedatabase()

    def get_logs_faceids(self, logs):
        # Get face ID from detection log
        ids = []
        for log in logs:
            id = log['objectID']
            ids.append(id)
        faceids = np.unique(ids)
        return faceids

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


    
