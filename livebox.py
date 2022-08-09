import io
import time
from functools import partial
from threading import Thread

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.behaviors.hover_behavior import HoverBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage

from audioconnection import AudioReceiver, AudioTransmitter
from mylayoutwidgets import ColorFloatLayout

from livestream import LiveStream

import websocket
import json

Builder.load_file('livebox.kv')

class LiveBox(MDFloatLayout, HoverBehavior):
    liveStream = ObjectProperty(None)
    liveActionBar = ObjectProperty(None)
    moveLeft = ObjectProperty(None)
    moveRight = ObjectProperty(None)
    moveUp = ObjectProperty(None)
    moveDown = ObjectProperty(None)
    status = StringProperty("stop")
    moveEvent = None
    # test stream url
    testUrl = "images/test.mp4"
    # Movement
    moveEnabled = True
    moveRepetitionSec = 0.3
    moveDistance = 10
    # servo parameter
    servo_center_pos = 7
    servo_max_move = 1.7
    # Audio object
    audioReceiver = None
    audioTransmitter = None

    def __init__(self, server_url = '', device_name = '', model = None, face_database = None, **kwargs):
        super().__init__(**kwargs)
        self.serverUrl = server_url
        self.deviceName = device_name
        if model and face_database:
            # Do if the AI model is set and face database exist
            self.set_live_stream (model, face_database, device_name) 
        
    def on_enter(self, *args):
        self.show_controls()

    def on_leave(self, *args):
        self.hide_controls()

    def set_live_stream (self, model, face_database, device_name):
        # Setting the live stream (Image object)
        self.liveStream.set_model_database(model, face_database)
        self.liveStream.set_device_name(device_name)

    def start_live_stream (self):
        # Start the live stream (Image object)
        ## Connect to websocket
        def on_message(wsapp, message):
            ### When frame data is received form server
            #### Create the CoreImage object
            coreImg = CoreImage(io.BytesIO(message), ext = 'jpg')
            #### Update the livestream texture with new frame
            Clock.schedule_once(partial(update_frame, coreImg), 0)
        
        def update_frame(coreImg, *largs):
            ## Update the livestream texture with new frame
            self.liveStream.texture = coreImg.texture
            self.liveStream.canvas.ask_update()

        ## Create the websocket connection to the server
        self.wsapp = websocket.WebSocketApp(f"ws://{self.serverUrl}/client/device1/", on_message=on_message)

        def run():
            # Start the websocket connection
            time.sleep(0.3) # Without this delay the websocket callback will not run
            self.wsapp.run_forever()

        # Re-init the texture of the liveStream object
        self.liveStream.texture = Texture.create()

        try:
            # Start the websocket connection in new thread
            self.wst = Thread(target = run)
            self.wst.daemon = True
            self.wst.start()
            # Change the status
            self.status = "play"
        except Exception as e:
            print (f'{e}: Failed starting websocket connection')
            self.wst = None
        finally:
            # Close the websocket connection
            self.wsapp.close()
    
    def stop_live_stream (self):
        try:  
            # Stopping the audio stream anyway
            self.stop_audio_in()
            self.stop_audio_out()
            # Reset the live action bar button state
            self.liveActionBar.reset()
            # Close the websocket connection
            self.wsapp.close()
            # If websocket thread exist
            if self.wst:
                self.wst.join()  
            # Change status
            self.status = "stop"
        except Exception as e:
            print ("Error to stop live stream...")
            print (e)
            self.status = "stop"

    def adjust_self_size(self, size):
        self.size = size
        self.adjust_livestream_size(size)

    def adjust_livestream_size(self, size):
        factor1 = size[0] / self.liveStream.width
        factor2 = size[1] / self.liveStream.height
        factor = min(factor1, factor2)
        target_size = ((self.liveStream.width * factor), (self.liveStream.height * factor))
        self.liveStream.size = target_size     

    def capture_image(self, file_name = ''):
        if file_name =='':
            self.liveStream.texture.save("test.png", flipped = False)

    def show_controls(self):
        self.liveActionBar.opacity  = 0.7
        self.moveLeft.opacity  = 0.7
        self.moveRight.opacity  = 0.7
        self.moveUp.opacity  = 0.7
        self.moveDown.opacity  = 0.7

    def hide_controls(self):
        self.liveActionBar.opacity  = 0
        self.moveLeft.opacity  = 0
        self.moveRight.opacity  = 0
        self.moveUp.opacity  = 0
        self.moveDown.opacity  = 0
    
    def button_touch_down(self, *args):
        if args[0].collide_point(*args[1].pos):
            if args[0] == self.moveLeft:
                # Move left
                print ('touch down left')
                if not self.moveEvent:
                    # Change button appearance
                    args[0].source = 'images/moveleft_down.png'
                    # Move once
                    self.start_move(dir = 'L', distance = self.moveDistance)
                    # Continue movement with interval if the button is still pressed
                    self.moveEvent = Clock.schedule_interval(partial(
                        self.start_move,
                        dir = 'L',
                        distance = self.moveDistance
                        ), self.moveRepetitionSec
                    )
            if args[0] == self.moveRight:
                # Move right
                print ('touch down right')
                if not self.moveEvent:
                    # Change button appearance
                    args[0].source = 'images/moveright_down.png'
                    # Move once
                    self.start_move(dir = 'R', distance = self.moveDistance)
                    # Continue movement with interval if the button is still pressed
                    self.moveEvent = Clock.schedule_interval(partial( 
                        self.start_move,
                        dir = 'R',
                        distance = self.moveDistance
                        ), self.moveRepetitionSec
                    )
            if args[0] == self.moveUp:
                # Move up
                print ('touch down up')
                if not self.moveEvent:
                    # Change button appearance
                    args[0].source = 'images/moveup_down.png'
                    # Move once
                    self.start_move(dir = 'U', distance = self.moveDistance)
                    # Continue movement with interval if the button is still pressed
                    self.moveEvent = Clock.schedule_interval(partial( 
                        self.start_move,
                        dir = 'U',
                        distance = self.moveDistance
                        ), self.moveRepetitionSec
                    )
            if args[0] == self.moveDown:
                # Move down
                print ('touch down down')
                if not self.moveEvent:
                    # Change button appearance
                    args[0].source = 'images/movedown_down.png'
                    # Move once
                    self.start_move(dir = 'D', distance = self.moveDistance)
                    # Continue movement with interval if the button is still pressed
                    self.moveEvent = Clock.schedule_interval(partial( 
                        self.start_move,
                        dir = 'D',
                        distance = self.moveDistance
                        ), self.moveRepetitionSec
                    )

    def button_touch_up(self, *args):
        if args[0].collide_point(*args[1].pos):
            print ('touch up')
            # Stop the movement / cancel the repetitive movement
            if self.moveEvent:
                self.moveEvent.cancel()
                self.moveEvent = None
                # Return the movement control buttons appearance
                self.moveLeft.source = 'images/moveleft_normal.png'
                self.moveRight.source = 'images/moveright_normal.png'
                self.moveUp.source = 'images/moveup_normal.png'
                self.moveDown.source = 'images/movedown_normal.png'
    
    def start_move(self, clock = None, dir = 'C', distance = 0):
        if dir != 'L' and dir != 'R' and dir != 'U' and dir != 'D' and dir != 'C':
            print ('Direction not valid')
            return False
        def move(dir, distance):
            data = {'op': 'mv', 'dir':dir, 'dist':distance}
            try:
                self.wsapp.send(json.dumps(data))
                return True
            except Exception as e:
                print (f'{e}: Error sending move command to server')
                return False
        # Start the move thread
        Thread(target = partial(move, dir ,distance)).start()
 
    def on_touch_down(self, touch):
        super().on_touch_down(touch)

        # Movements
        if self.moveEnabled:
            if self.liveStream.collide_point(*touch.pos) and not (
                self.moveLeft.collide_point(*touch.pos) or
                self.moveRight.collide_point(*touch.pos) or
                self.moveUp.collide_point(*touch.pos) or
                self.moveDown.collide_point(*touch.pos) or
                self.liveActionBar.collide_point(*touch.pos)):

                touchPos = (touch.pos[0]-self.liveStream.x, touch.pos[1]-self.liveStream.y)
                # Calculate move distance
                distance_x, distance_y = self.calculate_move_distance(touch_x = touchPos[0], touch_y = touchPos[1])

                if distance_x > 0.1:
                    # Touch is at left area
                    self.start_move(dir = 'L', distance = abs(distance_x))
                elif distance_x < -0.1:
                    # Touch is at right area
                    self.start_move(dir = 'R', distance = abs(distance_x))
                if distance_y > 0.1:
                    # Touch is at lower area
                    self.start_move(dir = 'D', distance = abs(distance_y))
                elif distance_y < -0.1:
                    # Touch is at upper area
                    self.start_move(dir = 'U', distance = abs(distance_y))

                print (f'touch pos: {touchPos}')

    def calculate_move_distance(self, touch_x=0, touch_y=0):
        distance_x = (((self.liveStream.center_x-self.liveStream.x) - touch_x)/(self.liveStream.center_x-self.liveStream.x)) * self.servo_max_move
        distance_y = (((self.liveStream.center_y-self.liveStream.y) - touch_y)/(self.liveStream.center_y-self.liveStream.y)) * self.servo_max_move
        #print (f'move distance: {distance}, center_x: {self.liveStream.center_x}, touch_x: {touch_x}')
        return distance_x, distance_y

    def start_audio_in(self):
        # Start audio_in
        audioinThread = Thread(target = self.audio_in)
        audioinThread.start()

    def audio_in(self):
        print ('audio_in')
        self.audioReceiver = AudioReceiver(self.deviceUrl, devicePort = 65001)
        self.audioReceiver.start_stream()

    def stop_audio_in(self):
        if self.audioReceiver:
            self.audioReceiver.stop_stream()
            self.audioReceiver = None

    def start_audio_out(self):
        # Start audio_out
        audiooutThread = Thread(target = self.audio_out)
        audiooutThread.start()

    def audio_out(self):
        print ('audio_out')
        self.audioTransmitter = AudioTransmitter(self.deviceUrl, devicePort = 65002)
        self.audioTransmitter.start_stream()

    def stop_audio_out(self):
        if self.audioTransmitter:
            self.audioTransmitter.stop_stream()
            self.audioTransmitter = None

    def light(self, on = False ):
        def light_on():
            data = {'op': 'lt', 'on' : on}
            try:
                self.wsapp.send(json.dumps(data))
                return True
            except Exception as e:
                print (f'{e}: Error sending light command to server')
                return False
        # Start the light thread
        Thread(target = light_on).start()