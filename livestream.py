import io
import threading
import time
from datetime import datetime
import uuid
from functools import partial

import numpy as np
from cv2 import imdecode, imwrite

from kivy.lang import Builder
from kivy.graphics import Color, Line
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty

Builder.load_file('livestream.kv')

class LiveStream(Image):

    manager = ObjectProperty(None)

    # Vision AI
    aiModel = None
    faceDatabase = None
    deviceName = ''

    processThisFrame = True
    t_process_frame = None
    bboxFactor = 0
    frameCount = 0
    streamSize = (1280, 720)
    faceDatabase = None
    faceDatabaseIDs = []
    faceDatabaseVectors = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nocache = BooleanProperty(True)
        self.state = "stop"
        self.device_name = ""
        self.server_address = ""
        #self.texture = Texture.create()
        # For bounding box size auto size
        self.bind(size = self.calculate_bbox_factor)
    
    def set_device_name(self, device_name):
        self.deviceName = device_name

    def set_model_database(self, model, face_database):
        self.aiModel = model
        self.faceDatabase = face_database
        if self.faceDatabase:
            self.get_id_vector(self.faceDatabase)
        print (f'LIVESTREAM faceDatabase = {len(face_database)}')

    def get_id_vector(self, db):
        # Get ID from database
        self.faceDatabaseIDs.clear()
        self.faceDatabaseVectors.clear()
        for key in db.keys():
            self.faceDatabaseIDs.append(key)
            # Face vector is at index 2
            self.faceDatabaseVectors.append(db[key][2])

    def vector_distance_to_db(self, sample_vector, db_vectors):
        # Return list of distance from sample vector to every vectors in db_vectors list
        distances = []
        for vector in db_vectors:
            # Euclidean distance
            distance = sum(np.power((sample_vector - vector), 2))
            distance = np.sqrt(distance)
            distances.append(distance)
        return distances

    def vector_distance_to_db_cosine(self, sample_vector, db_vectors):
        # Return list of distance from sample vector to every vectors in db_vectors list
        distances = []
        for vector in db_vectors:
            # Euclidean distance
            dot = np.dot(sample_vector, vector)
            norm = np.linalg.norm (sample_vector) * np.linalg.norm (vector)
            similarity = dot / norm
            distances.append(1-similarity)
        return distances

    def find_closest_distance(self, distances):
        # Find the smallest value in distance and return the value and its index
        nearest = min(distances)
        index = np.argmin(distances)
        return nearest, index

    def find_vector_id(self, vectors, db_vectors):
        # Return the value in databaseIDs property which index is the index of nearest vector in databaseVectors property
        ids = []
        nearests = []
        for vector in vectors:
            distances = self.vector_distance_to_db_cosine(vector, db_vectors)
            nearest, index = self.find_closest_distance(distances)
            id = self.faceDatabaseIDs[index]
            ids.append(id)
            nearests.append(nearest)
        return ids, nearests

    def calculate_bbox_factor(self, *args):
        factor1 = self.width / self.streamSize[0]
        factor2 = self.height / self.streamSize[1]
        self.bboxFactor = min(factor1, factor2)

    def process_detection(self, bboxes, face_ids, distances, faces, img):
        timeStamp = time.time()
        self.clear_widgets()
        self.canvas.after.clear()
        for i in range(len(bboxes)):
            if distances[i] < 0.2:
                # Display detection bounding boxes and labels
                self.display_detection(bbox = bboxes[i], first_name = self.faceDatabase[face_ids[i]][0], last_name = self.faceDatabase[face_ids[i]][1])
                # Log detection
                self.log_detection(face_id = face_ids[i], face = faces[i], frame = img, time_stamp = timeStamp, device_name = self.deviceName)

    def log_detection(self, face_id, face, frame, time_stamp, device_name):
        detectionID = f'{uuid.uuid4()}'        # Random file name
        time_stamp = [datetime.fromtimestamp(time_stamp).strftime('%d %b %Y'), datetime.fromtimestamp(time_stamp).strftime('%H:%M:%S')]
        self.manager.log_detection(face_id = face_id, detection_id = detectionID, time_stamp = time_stamp, device_name = device_name)
        imwrite(f'logs/images/faces/{detectionID}.png', face)
        imwrite(f'logs/images/frames/{detectionID}.png', frame)

    def display_detection(self, bbox, first_name, last_name):
        # Box
        xb, yb, width, height = bbox*self.bboxFactor
        with self.canvas.after:
            Color (0,0.64,0.91, 1.0)
            Line(rectangle = (self.x+xb, self.y+(self.height-yb), width, -height), width = 1.5)
        # label (first name, last name)
        labelText = (f'{first_name} {last_name}')  
        label = Label(text = (labelText), font_size = 16, font_family = "arial", halign = 'left', valign = 'middle', color = (0,0.4,1), size_hint = (None, None), size = (100, 40), x = self.x+int(xb), y = self.y+(self.height-int(yb)))
        self.add_widget(label)

    # Video Frame Event Function
    def _on_video_frame(self, *largs):
        pass
        # super()._on_video_frame(*largs)
        # # Adjust size according to texture size ?????
        # if self.aiModel:
        #     if self.processThisFrame:
        #         data = io.BytesIO()
        #         self.texture.save(data, flipped = False, fmt = 'png')
        #         if self.t_process_frame is None:
        #             self.t_process_frame = threading.Thread(target = partial(self.process_frame, data))
        #             self.t_process_frame.start()
        #     self.frameCount +=1
        #     if self.frameCount > 20:
        #         self.frameCount =0
        #         self.clear_widgets()
        #         self.canvas.after.clear()

    def process_frame(self, data):
        pass
        # self.processThisFrame = False
        # buff = np.asarray(bytearray(data.read()))
        # img = imdecode(buff, 1)
        # # Should check if ai_model exist
        # '''Detect and extraction'''
        # bboxes, faces = self.aiModel.extract_faces(detector_type = 1, img = img)
        # '''Recognition'''
        # if np.any(faces):   # Face detected, proceed to recognition
        #     # Predict
        #     face_vectors = self.aiModel.create_face_vectors(faces)
        #     # Find ID
        #     print (f'LEN FACE_VECTORS: {len(face_vectors)}, LEN FACEDATABASEVECTORS: {len(self.faceDatabaseVectors)}')
        #     face_ids, distances = self.find_vector_id(face_vectors, self.faceDatabaseVectors)
        #     self.print_id_distance(face_ids, distances)
        #     # Display detection
        #     if min(distances) < 0.2:
        #         self.process_detection(bboxes, face_ids, distances, faces, img)
        # # Clearing flag for next process
        # self.processThisFrame = True
        # self.t_process_frame = None

    def print_id_distance(self, ids, distances):
        print (f'LEN IDS: {len(ids)}, LEN DISTANCES: {len(distances)}')
        for i in range(len(ids)):
            print (f'ID[{i}]: {ids[i]}, DISTANCE[{i}]: {distances[i]}')