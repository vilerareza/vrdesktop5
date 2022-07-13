import threading
import time
import requests
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock

Builder.load_file('deviceIcon.kv')

class DeviceIcon(FloatLayout):
    statusImage = ObjectProperty(None)
    deviceName = StringProperty("")
    deviceLabel = ObjectProperty(None)
    isEnabled = BooleanProperty(True)
    t_status_checker = None
    stop_flag = False

    def __init__(self, deviceName, **kwargs):
        super().__init__(**kwargs)
        self.deviceName = deviceName
        self.condition = threading.Condition()

    def start_status_checker(self):
        # Start the status checker thread

        def callback_ok(*args):
            # Enable the item
            self.isEnabled = True
            self.statusImage.source = "images/play.png"
            self.deviceLabel.text = "[color=cccccc]"+self.deviceName+"[/color]"
        
        def callback_fail(*args):
            # Disable the frame
            self.isEnabled = False
            self.statusImage.source = "images/unavailable.png"
            self.deviceLabel.text = "[color=777777]"+self.deviceName+"[/color]"

        def check():
            while (not self.stop_flag):
                ## if the application exit then break the loop
                time.sleep(3)
                try:
                    r = (requests.get(f"http://127.0.0.1:8000/stream/status/device1/")).json()
                    if r['stream'] == True:
                        Clock.schedule_once(callback_ok, 0)
                    else:
                        Clock.schedule_once(callback_fail, 0)
                    
                except Exception as e:
                    print (e)

        t_status_checker = threading.Thread(target = check)
        t_status_checker.daemon = True
        t_status_checker.start()

    def stop(self):
        self.stop_flag=True
