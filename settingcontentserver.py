import requests
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

Builder.load_file("settingcontentserver.kv")

class SettingContentServer(FloatLayout):
    
    serverObj = None
    titleLabelText = 'Server Setting'
    titleLabel = ObjectProperty(None)
    serverAddressLabel = ObjectProperty(None)
    serverAddressText = ObjectProperty(None)
    btnSave = ObjectProperty(None)
    btnTest = ObjectProperty(None)
    testLabel = ObjectProperty(None)
    testImage = ObjectProperty(None)
    myParent = ObjectProperty(None)

    serverAddressFile = 'data/serveraddress.p'

    def button_press_callback(self, button):
        if button == self.btnSave:
            button.source = 'images/settingview/btn_save_server_down.png'
        elif button == self.btnTest:
            button.source = 'images/settingview/btn_test_down.png'

    def button_release_callback(self, button):
        if button == self.btnSave:
            button.source = 'images/settingview/btn_save_server_normal.png'
            self.save_server_addr(self.serverAddressText.text)
            # Refresh the devices
            self.parent.reinit_devices()
        elif button == self.btnTest:
            button.source = 'images/settingview/btn_test_normal.png'
            self.test_server(self.serverAddressText.text)

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

    def test_server(self, server_address):
        try:
            r = requests.get(f'{server_address}/servercheck/')
            if r.status_code == 200 and r.text == 'ServerOk!':
                self.testLabel.text = 'Server OK'
                self.testImage.opacity = 1
                self.testImage.source = 'images/settingview/server_ok.png'
            else:
                self.testLabel.text = 'Server Not Found'
                self.testImage.opacity = 1
                self.testImage.source = 'images/settingview/server_fail.png'
        except Exception as e:
            self.testLabel.text = 'Server Not Found'
            self.testImage.opacity = 1
            self.testImage.source = 'images/settingview/server_fail.png'
            print (f'test_server failed :{e}')
    
    def on_parent(self, *args):
        self.testLabel.text = ''
        self.testImage.opacity = 0
        


