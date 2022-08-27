from threading import Thread
import time
import requests
import pickle
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

Builder.load_file("serveritem.kv")

class ServerItem(FloatLayout):
    serverImage = ObjectProperty(None)
    statusImage = ObjectProperty(None)
    serverAddressFile = ''
    serverAddress = ''
    stop_flag = False

    def __init__(self, server_address_file='data/serveraddress.p', **kwargs):
        super().__init__(**kwargs)
        try:
            self.serverAddressFile = server_address_file
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                self.serverAddress = pickle.load(file)
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')
        
        finally:
            self.start_server_checker()

    def update_server_addr(self, server_address = ''):
        # Serialize server address to file
        try:
            with open(self.serverAddressFile, 'wb') as file:
                pickle.dump(server_address, file)
                self.serverAddress = server_address
        except Exception as e:
            print (f'Saving server address failed: {e}')

    def start_server_checker(self):
        # Start the status checker thread
        self.stop_flag=False

        def callback_ok(*args):
            self.statusImage.source = 'images/settingview/statusicon_active.png'
        
        def callback_fail(*args):
            self.statusImage.source = 'images/settingview/statusicon_inactive.png'

        def check():
            while (not self.stop_flag):
                ## if the application exit then break the loop
                time.sleep(5)
                try:
                    r = requests.get(f'{self.serverAddress}/servercheck/')
                    if r.status_code == 200 and r.text == 'ServerOk!':
                        Clock.schedule_once(callback_ok, 0)
                    else:
                        Clock.schedule_once(callback_fail, 0)
                except Exception as e:
                    Clock.schedule_once(callback_fail, 0)

        # Starting the server checker thread
        t = Thread(target = check)
        t.daemon = True
        t.start()

    def stop_server_checker(self):
        self.stop_flag=True



