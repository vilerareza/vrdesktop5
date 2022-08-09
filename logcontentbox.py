import io
import pickle
import base64
from dateutil.parser import isoparse
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.stacklayout import StackLayout
from kivy.uix.behaviors.compoundselection import CompoundSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.core.image import Image as CoreImage

from logfaceitem import LogFaceItem

import requests
import numpy as np
from cv2 import imencode, imdecode, rectangle

import datetime

Builder.load_file('logcontentbox.kv')

class LogContentBox(BoxLayout):

    detectionLog = None
    logFaceLayout = ObjectProperty(None)
    logFrameLayout = ObjectProperty(None)

    def display_detection_log(self, face_id):
        # Clearing layout
        self.clear_images(layouts = [self.logFaceLayout, self.logFrameLayout])
        # Get detection log form the server
        self.detectionLog = self.get_detection_log(face_id)
        # Show detection face in the logFaceLayout
        self.show_detection_face(self.logFaceLayout, self.detectionLog)

    def get_detection_log(self, face_id):
        try:
            # Sending request
            r = requests.get(f"http://127.0.0.1:8000/api/log/faceid/{face_id}/")
            # Getting and parsing response
            log_response = r.json()  # Produce list of dict
            print ('GET log OK')
            return log_response
        except Exception as e:
            print (e)
            return []

    def clear_images(self, layouts = []):
        for layout in layouts:
            layout.clear_widgets()

    def show_detection_face(self, widget, detection_log):
        '''Display detection face in the widget'''
        for log in detection_log:
            logID = log['id']
            timeStamp = isoparse(log['timeStamp'])
            faceDataStr = log['faceData']
            faceDataNp = pickle.loads(base64.b64decode(faceDataStr))
            _, faceDataBytes = imencode(".jpg", faceDataNp)
            frameID = log['frameID']
            # Bounding box property (numpy)
            bbox = pickle.loads(base64.b64decode(log['bbox']))
            coreImg = CoreImage(io.BytesIO(faceDataBytes), ext = 'jpg')
            widget.add_widget(LogFaceItem(
                log_id = logID, 
                time_stamp = timeStamp, 
                face_texture = coreImg.texture, 
                frame_id = frameID, 
                bbox = bbox
                )
            )

class LogFaceStack (FocusBehavior, CompoundSelectionBehavior, StackLayout):

    frameLayout = ObjectProperty(None)
    selectedData = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(selectedData = self.show_frame)

    def show_frame(self, *args):
        '''display corresponding frame in frameLayout'''
        if self.frameLayout:
            frameData = self.get_frame_data(self.selectedData.frameID)
            bbox = self.selectedData.bbox
            try:
                frameTexture = self.create_frame_texture(frameData, bbox)
                # Prepare image widget
                frameWidget = Image(
                    size_hint = (0.9, 0.9), 
                    pos_hint = {'center_x' : 0.5, 'center_y' : 0.5},
                    texture = frameTexture
                )
                # Show the image widget in frameLayout
                self.frameLayout.add_widget(frameWidget)
            except Exception as e:
                print (f'Cannot display frame image: {e}')

    def get_frame_data (self, frame_id):
        try:
            # Sending request for frame
            r = requests.get(f"http://127.0.0.1:8000/api/log/frame/{frame_id}/")
            frameData = r.json()['frameData']
            return frameData
        except Exception as e:
            print (e)
            return None

    def create_frame_texture(self, frame_data, bbox):
        # Creating kivy image texture from from frame string data
        faceDataBytes = base64.b64decode(frame_data)
        # Conversion to np array
        buff = np.asarray(bytearray(faceDataBytes))
        img = imdecode(buff, 1)
        # Draw bounding box
        xb, yb, widthb, heightb = bbox
        rectangle(img, (xb, yb), (xb+widthb, yb+heightb), color = (232,164,0), thickness = 3)
        # Returning bytes data
        _, img_bytes = imencode(".jpg", img)
        # Creating core image and return its texture
        coreImg = CoreImage(io.BytesIO(img_bytes.tobytes()), ext = 'jpg')
        return coreImg.texture

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if super().keyboard_on_key_down(window, keycode, text, modifiers):
            return True
        if self.select_with_key_down(window, keycode, text, modifiers):
            return True
        return False

    def keyboard_on_key_up(self, window, keycode):
        if super().keyboard_on_key_up(window, keycode):
            return True
        if self.select_with_key_up(window, keycode):
            return True
        return False

    def add_widget(self, widget):
        super().add_widget(widget)
        widget.bind(on_touch_down = self.widget_touch_down, on_touch_up = self.widget_touch_up)
    
    def widget_touch_down(self, widget, touch):
        if widget.collide_point(*touch.pos):
            self.select_with_touch(widget, touch)
    
    def widget_touch_up(self, widget, touch):
        if self.collide_point(*touch.pos) and (not (widget.collide_point(*touch.pos) or self.touch_multiselect)):
            self.deselect_node(widget)
    
    def select_node(self, node):
        node.backgroundImage.source = 'images/logview/faceitem_down.png'
        self.selectedData = node
        return super().select_node(node)
        
    def deselect_node(self, node):
        super().deselect_node(node)
        node.backgroundImage.source = 'images/logview/faceitem_normal.png'
    
    def clear_selection(self, widget=None):
        return super().clear_selection()

    def on_selected_nodes(self,grid,nodes):
        pass