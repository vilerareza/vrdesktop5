import os
import requests
import pickle
import qrcode
import uuid
import json
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

Builder.load_file("settingcontentdevice.kv")

class SettingContentDevice(FloatLayout):
    editMode = BooleanProperty(False)
    titleLabel = ObjectProperty(None)
    deviceNameLabel = ObjectProperty(None)
    deviceNameText = ObjectProperty(None)
    wifiNameLabel = ObjectProperty(None)
    wifiNameText = ObjectProperty(None)
    wifiPassLabel = ObjectProperty(None)
    wifiPassText = ObjectProperty(None)
    visionAILabel = ObjectProperty(None)
    visionAISwitch = ObjectProperty(None)
    btnSaveEdit = ObjectProperty(None)
    btnRemove = ObjectProperty(None)
    qrImage = ObjectProperty(None)

    def toggle_press_callback(self, button):
        '''callback function for edit/save button'''
        if button == self.btnSaveEdit:
            if button.state == 'down':
                self.editMode = True
                button.source = 'images/settingview/btn_save.png'
            else:
                self.editMode = False
                button.source = 'images/settingview/btn_edit.png'
                # Trigger saving to database
                self.save_device_to_db()

    def button_press_callback(self, button):
        if button == self.btnRemove:
            button.source = 'images/settingview/btn_remove_down.png'

    def button_release_callback(self, button):
        if button == self.btnRemove:
            button.source = 'images/settingview/btn_remove.png'
            self.remove_from_db()

    def get_device_obj(self, device_obj):
        if device_obj:
            self.deviceObjID = device_obj.deviceID
            self.deviceObjName = device_obj.deviceName
            self.deviceObjHostName = device_obj.hostName
            self.deviceObjWifiName = device_obj.wifiName
            self.deviceObjWifiPass = device_obj.wifiPass
            self.deviceObjVisionAI = device_obj.deviceVisionAI
            self.fill (self.deviceObjName, self.deviceObjHostName, self.deviceObjWifiName, self.deviceObjWifiPass, self.deviceObjVisionAI)

    def fill(self, device_obj_name, device_obj_host_name, device_obj_wifi_name, device_obj_wifi_pass, device_obj_visionai):
        
        def generate_qr(qr_data):
            # Remove previous qr image file (if exist)
            qrImage = os.listdir(self.qrSaveDir)
            for image in qrImage:
                os.remove(os.path.join(self.qrSaveDir, image))
            # Init QR generator
            qr = qrcode.QRCode(
                version=5,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=5,
                border=4)
            data = json.dumps(qr_data)
            qr.add_data(str(data))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            # Saving QR image and display it
            qrFileName = f'{self.qrSaveDir}{str(uuid.uuid4())[0:8]}.png'
            img.save(qrFileName)
            self.qrImage.source = qrFileName

        # Getting server address
        serverAddress = self.get_server_address()
        self.deviceNameText.text = device_obj_name
        self.wifiNameText.text = device_obj_wifi_name
        self.wifiPassText.text = device_obj_wifi_pass
        self.visionAISwitch.active = device_obj_visionai
        #qrData = {'server': serverAddress, 'host': host, 'name':deviceName, 'ssid':ssid, 'psk':psk}
        qrData = {'server': serverAddress, 'host': device_obj_host_name, 'name':device_obj_name, 'ssid':device_obj_wifi_name, 'psk':device_obj_wifi_pass}
        generate_qr(qrData)


    def save_device_to_db(self):

        '''child function to retrieve devices from server REST API. Return dict'''
        def get_device_detail(server_address, device_id):
            try:
                r = requests.get(f"{server_address}/api/device/{device_id}/")
                device = r.json()
                return device
            except Exception as e:
                print (e)
                return {}

        try:
            # User pressed "Save"
            deviceID = self.deviceObjID
            newDeviceName = self.deviceNameText.text
            newWifiName = self.wifiNameText.text
            newWifiPass = self.wifiPassText.text
            newVisionAI = self.visionAISwitch.active
            deviceData = {'deviceName': newDeviceName, 'showName': '', 'wifiName': newWifiName, 'wifiPass': newWifiPass, 'visionAI' : newVisionAI}
            serverAddress = self.get_server_address()
            r = requests.put(f"{serverAddress}/api/device/{deviceID}/", data = deviceData)
            if r.status_code == 200:
                # Get the new device attribute (json) form the sever
                newDevice = get_device_detail(serverAddress, deviceID)
                # Update the current deviceitem
                self.parent.update_deviceitem(newDevice)

        except Exception as e:
            print (f'Failure on saving to database: {e}')

    def remove_from_db(self):
        print ('remove from db')
        if self.deviceObjID:
            try:
                serverAddress = self.get_server_address()
                r = requests.delete(f"{serverAddress}/api/device/{self.deviceObjID}/")
                response = r.status_code
                print (f'Status code: {response}')
                # Refresh the device list.
                self.parent.reinit_devices()
                self.parent.no_selection_config()
            except Exception as e:
                print (e)

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
        # Getting the server adrress
        self.serverAddressFile = server_address_file
        self.qrSaveDir = qr_save_dir


