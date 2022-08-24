import os
import pickle
import uuid
import qrcode
import json

from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
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

    def button_press_callback(self, button):
        if button == self.btnAdd:
            button.source = 'images/settingview/btn_add_down.png'
        elif button == self.btnCancel:
            button.source = 'images/settingview/btn_cancel_down.png'

    def button_release_callback(self, button):
        if button == self.btnAdd:
            button.source = 'images/settingview/btn_add_normal.png'
        elif button == self.btnCancel:
            button.source = 'images/settingview/btn_cancel_normal.png'
            self.parent.no_selection_config()

    def validate_entry(self, *args):
        isValid = True
        for entry in args:    
            if entry.text == '':
                isValid = False
                entry.background_color = (0.9, 0.7, 0.7)
            else:
                entry.background_color = (0.8, 0.8, 0.8)
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
            host  = self.create_host_name(prefix = 'vr')
            name = self.deviceNameText.text
            ssid = self.wifiNameText.text
            psk = self.wifiNameText.text
            qrDict = {'host': host, 'name':name, 'ssid':ssid, 'psk':psk}
            self.generate_qr (qrDict)

    def fill(self, device_obj):
        if device_obj:
            self.deviceNameText.text = device_obj.deviceName
            #wifiNameText = ObjectProperty(None)
            #wifiPassText = ObjectProperty(None)
            self.visionAISwitch.active = device_obj.deviceVisionAI

    def get_server_address(self):
        try:
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                serverAddress = pickle.load(file)
                return serverAddress
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')
            return None

    def __init__(self, server_address_file='data/serveraddress.p', qr_save_dir ='images/temp/qr/', **kwargs):
        super().__init__(**kwargs)
        # Getting the server adrress, deserialize the serveraddress.p
        self.serverAddressFile = server_address_file
        self.qrSaveDir = qr_save_dir



