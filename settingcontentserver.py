from threading import Thread
import time
import requests
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock

Builder.load_file("settingcontentserver.kv")

class SettingContentServer(FloatLayout):
    editMode = False
    serverObj = None
    titleLabelText = 'Server Setting'
    titleLabel = ObjectProperty(None)
    serverAddressLabel = ObjectProperty(None)
    serverAddressText = ObjectProperty(None)
    btnSaveEdit = ObjectProperty(None)
    #btnTest = ObjectProperty(None)
    testLabel = ObjectProperty(None)
    testImage = ObjectProperty(None)
    myParent = ObjectProperty(None)

    serverAddressFile = 'data/serveraddress.p'

    def toggle_press_callback(self, button):
        '''callback function for edit/save button'''
        if button == self.btnSaveEdit:
            if button.state == 'down':
                self.editMode = True
                button.source = 'images/settingview/btn_save_server.png'
                self.serverAddressText.disabled = False
            else:
                self.editMode = False
                # Test the connection to the server
                self.test_server(self.serverAddressText.text)
                button.source = 'images/settingview/btn_edit_server.png'
                self.serverAddressText.disabled = True
                '''Storing server address'''
                self.save_server_addr(self.serverAddressText.text)
                # Refresh the devices
                self.parent.reinit_devices()

    # def button_press_callback(self, button):
    #     if button == self.btnTest:
    #         button.source = 'images/settingview/btn_test_down.png'

    # def button_release_callback(self, button):
    #     if button == self.btnTest:
    #         button.source = 'images/settingview/btn_test_normal.png'
    #         self.test_server(self.serverAddressText.text)

    def save_server_addr(self, server_address = ''):
        if self.serverObj:
            self.serverObj.update_server_addr(server_address)

    def fill(self, server_obj):
        if server_obj:
            # Getting the server object
            self.serverObj = server_obj
            # Updating the text with serverObj server address property
            self.serverAddressText.text = server_obj.serverAddress

    def update_server_obj(self, new_server_address):
        self.serverObj.serverAddress = new_server_address

    # def test_server(self, server_address):
    #     try:
    #         r = requests.get(f'{server_address}/servercheck/')
    #         if r.status_code == 200 and r.text == 'ServerOk!':
    #             self.testLabel.text = 'Server OK'
    #             self.testImage.opacity = 1
    #             self.testImage.source = 'images/settingview/server_ok.png'
    #         else:
    #             self.testLabel.text = 'Server Not Found'
    #             self.testImage.opacity = 1
    #             self.testImage.source = 'images/settingview/server_fail.png'
    #     except Exception as e:
    #         self.testLabel.text = 'Server Not Found'
    #         self.testImage.opacity = 1
    #         self.testImage.source = 'images/settingview/server_fail.png'
    #         print (f'test_server failed :{e}')
    
    def on_parent(self, *args):
        self.testLabel.text = ''
        self.testImage.opacity = 0
        

    # def test_server(self, server_address):
    #     # Start the status checker thread

    #     def callback_ok(*args):
    #         self.testLabel.text = 'Server Connected'
    #         self.testImage.opacity = 1
    #         self.testImage.source = 'images/settingview/server_ok.png'
        
    #     def callback_fail(*args):
    #         self.testLabel.text = 'Server Not Found'
    #         self.testImage.opacity = 1
    #         self.testImage.source = 'images/settingview/server_fail.png'

    #     try:
    #         r = requests.get(f'{server_address}/servercheck/', timeout = 5)
    #         if r.status_code == 200 and r.text == 'ServerOk!':
    #             callback_ok()
    #         else:
    #             callback_fail()
    #     except Exception as e:
    #         callback_fail()
    #         print (f'test_server failed :{e}')

    def test_server(self, server_address):
        # Start the status checker thread

        def callback_ok(*args):
            self.testLabel.text = 'Server OK'
            self.testImage.opacity = 1
            self.testImage.source = 'images/settingview/server_ok.png'
        
        def callback_fail(*args):
            self.testLabel.text = 'Server Not Found'
            self.testImage.opacity = 1
            self.testImage.source = 'images/settingview/server_fail.png'

        def check():
            try:
                r = requests.get(f'{server_address}/servercheck/', timeout = 5)
                if r.status_code == 200 and r.text == 'ServerOk!':
                    Clock.schedule_once(callback_ok, 0)
                else:
                    Clock.schedule_once(callback_fail, 0)
            except Exception as e:
                Clock.schedule_once(callback_fail, 0)
                print (f'test_server failed :{e}')

        t = Thread(target = check)
        t.daemon = True
        t.start()


