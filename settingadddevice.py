import os
import requests
import pickle
import uuid
import qrcode
import json

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImg

Builder.load_file("settingadddevice.kv")

class SettingAddDevice(FloatLayout):
    
    titleLabelText = 'Add New Device'
    titleLabel = ObjectProperty(None)
    deviceNameLabel = ObjectProperty(None)
    deviceNameText = ObjectProperty(None)
    wifiNameLabel = ObjectProperty(None)
    wifiNameText = ObjectProperty(None)
    wifiPassLabel = ObjectProperty(None)
    wifiPassText = ObjectProperty(None)
    visionAILabel = ObjectProperty(None)
    visionAISwitch = ObjectProperty(None)
    btnAdd = ObjectProperty(None)
    btnCancel = ObjectProperty(None)
    qrImage = ObjectProperty(None)
    btnClose = ObjectProperty(None)

    def button_press_callback(self, button):
        if button == self.btnAdd:
            button.source = 'images/settingview/btn_add_down.png'
        elif button == self.btnCancel:
            button.source = 'images/settingview/btn_cancel_down.png'
        elif button == self.btnClose:
            button.source = 'images/settingview/btn_close_down.png'

    def button_release_callback(self, button):
        if button == self.btnAdd:
            button.source = 'images/settingview/btn_add.png'
        elif button == self.btnCancel:
            button.source = 'images/settingview/btn_cancel.png'
            self.parent.no_selection_config()
        elif button == self.btnClose:
            button.source = 'images/settingview/btn_close.png'
            self.parent.no_selection_config()

    def validate_entry(self, *args):
        isValid = True
        for entry in args:    
            if entry.text == '':
                isValid = False
                entry.background_color = (0.9, 0.7, 0.7)
            else:
                entry.background_color = (1, 1, 1)
        return isValid

    def create_host_name(self, prefix):
        rand = str(uuid.uuid4())[0:8]
        hostName = f'{prefix}{rand}'
        return hostName

    def generate_qr(self, dict):
        # Remove previous qr image file
        qrImage = os.listdir(self.qrSaveDir)
        for image in qrImage:
            os.remove(os.path.join(self.qrSaveDir, image))
        # Init QR generator
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=5,
            border=4)
        data = json.dumps(dict)
        qr.add_data(str(data))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # Saving QR image and display it
        qrFileName = f'{self.qrSaveDir}{str(uuid.uuid4())[0:8]}.png'
        img.save(qrFileName)
        self.qrImage.source = qrFileName

    def add_new_device(self, *args):
        # Callback function for add device button
        if self.validate_entry(*args):
            # Preparing data
            deviceName = self.deviceNameText.text
            hostName  = self.create_host_name(prefix = 'vr')
            wifiName = self.wifiNameText.text
            wifiPass = self.wifiPassText.text
            deviceVisionAI = self.visionAISwitch.active
            serverAddress = self.get_server_address()
            '''create device object in the server'''
            self.add_to_db(deviceName, hostName, wifiName, wifiPass, deviceVisionAI)
            '''create qr code for camera'''
            qrDict = {'server': serverAddress, 'host': hostName, 'name':deviceName, 'ssid':wifiName, 'psk':wifiPass}
            self.generate_qr (qrDict)
            # Changing buttons state
            self.btnAdd.disabled = True
            self.btnCancel.disabled = True
            self.add_widget(self.btnClose)

    def refresh(self):
        self.deviceNameText.text = ''
        self.deviceNameText.background_color = (1, 1, 1)
        self.wifiNameText.text = ''
        self.wifiNameText.background_color = (1, 1, 1)
        self.wifiPassText.text = ''
        self.wifiPassText.background_color = (1, 1, 1)
        self.visionAISwitch.active = True
        self.qrImage.source = "images/settingview/qr_empty.png"
        # Enabling the add and cancel button anyway
        self.btnAdd.disabled = False
        self.btnCancel.disabled = False
        # Hide the close button
        self.remove_widget(self.btnClose)

    def get_server_address(self):
        try:
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                serverAddress = pickle.load(file)
                return serverAddress
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')
            return None

    def on_parent(self, *args):
        self.refresh()

    def add_to_db (self, device_name, device_host_name, device_wifi_name, device_wifi_pass, device_vision_ai):
        requestData = {'deviceName': device_name, 
                        'hostName': device_host_name, 
                        'wifiName': device_wifi_name,
                        'wifiPass': device_wifi_pass,
                        'visionAI' : device_vision_ai}
        serverAddress = self.get_server_address()
        try:
            r = requests.post(f"{serverAddress}/api/device/", data = requestData)
            response = r.status_code
            print (f'Status code: {response}')
            # Response by status code
            if response == 201:
                # Refresh the device list.
                self.parent.reinit_devices()
            else:
                print (f'Name {device_name} already exist. Device not created')
        except Exception as e:
            print(e)

    def __init__(self, server_address_file='data/serveraddress.p', qr_save_dir ='images/temp/qr/', **kwargs):
        super().__init__(**kwargs)
        # Getting the server adrress
        self.serverAddressFile = server_address_file
        self.qrSaveDir = qr_save_dir
