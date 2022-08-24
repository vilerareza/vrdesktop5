import requests
import pickle
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from deviceentry import DeviceEntry
from deviceinfo import DeviceInfo
from deviceitem import DeviceItem
from devicelist import DeviceList
from serverbox import ServerBox
from devicelistbox import DeviceListBox
from settingcontentbox import SettingContentBox

Builder.load_file("settingview.kv")

class SettingView(BoxLayout):

    serverBox = ObjectProperty(None)
    devices = ListProperty([])
    deviceList = ObjectProperty(None)
    settingContentBox = ObjectProperty(None)
    serverAddress = ''
    
    def button_press_callback(self, widget):
        if widget == self.ids.device_delete_button:
            widget.source = "images/settingview/delete_device_down.png"

    def button_release_callback(self, widget):
        if widget == self.ids.device_delete_button:
            widget.source = "images/settingview/delete_device_normal.png"

    def add_to_db (self, deviceEntry, isNewDevice):
        if (isNewDevice == True): 
            deviceName = deviceEntry.deviceNameText.text
            # Device Vision AI default to False
            deviceVisionAI = False
            requestData = {'deviceName': deviceName, 'showName': '', 'visionAI' : deviceVisionAI}
            try:
                r = requests.post(f"{self.serverAddress}/api/device/", data = requestData)
                response = r.status_code
                print (f'Status code: {response}')
                # Response by status code
                if response == 201:
                    # Set device entry to icon mode
                    deviceEntry.icon_mode()
                    # Refresh the device list
                    self.refresh_devices()
                else:
                    print (f'Name {deviceName} already exist. Device not created')
            except Exception as e:
                print(e)
            finally:
                deviceEntry.isNewDevice = False
                
    def save_device_to_db(self, content_obj):
        try:
            # User pressed "Save"
            deviceID = self.deviceList.deviceListLayout.selectedDevice.deviceID
            newDeviceName = str(content_obj.deviceNameText.text)
            newWifiName = str(content_obj.wifiNameText.text)
            newWifiPass = str(content_obj.wifiPassText.text)
            newVisionAI = content_obj.visionAISwitch.active
            deviceData = {'deviceName': newDeviceName, 'showName': '', 'visionAI' : newVisionAI}
            r = requests.put(f"{self.serverAddress}/api/device/{deviceID}/", data = deviceData)
            if r.status_code == 200:
                # Get the new device attribute (json) form the sever
                newDevice = self.get_device_detail(deviceID)
                # Get current devices
                for device in self.devices:
                    if device.deviceID == newDevice['id']:
                        device.deviceName = newDevice['deviceName']
                        device.deviceVisionAI = newDevice['visionAI']
                        self.settingContentBox.change_config(device)

        except Exception as e:
            print (f'Failure on saving to database: {e}')

    def remove_from_db(self):
        print ('remove from db')
        try:
            if self.deviceList.selectedDevice: 
                deviceID = self.deviceList.selectedDevice.deviceID
                r = requests.delete(f"{self.serverAddress}/api/device/{deviceID}/")
                response = r.status_code
                print (f'Status code: {response}')
                self.refresh_devices()
        except Exception as e:
            print (e)

    def get_device_detail(self, device_id):
         # Retrieve devices from server REST API. Return dict
        try:
            r = requests.get(f"{self.serverAddress}/api/device/{device_id}/")
            device = r.json()
            print(device)
            return device
        except Exception as e:
            print (e)
            return {}

    def get_devices(self):
        # Retrieve devices from server REST API
        try:
            r = requests.get(f"{self.serverAddress}/api/device/")
            device_response = r.json()  # Produce list of dict
            for device in device_response:
                deviceID = device['id']
                deviceName = device['deviceName']
                deviceUrl = ''
                deviceVisionAI = device['visionAI']
                self.devices.append(DeviceItem(deviceID = deviceID, deviceName = deviceName, deviceUrl = deviceUrl, deviceVisionAI = deviceVisionAI))
        except Exception as e:
            print (e)
        finally:
            return self.devices

    def check_name_exist_db(self, name):
        for device in self.devices:
            if (device.deviceName == name):
                return True

    def get_device_name_db (self):
        names = []
        for device in self.devices:
            names.append(device.deviceName)
        return names

    def refresh_devices(self):
        # Refresh the device list
        self.devices.clear()
        # Clear device list widgets
        self.deviceList.deviceListLayout.clear_widgets()
        #self.get_devices()
        #for device in self.devices:
        #    self.deviceList.add_widget(device)

    def populate_items_to_list(self, listWidget, items):
        # Populate items to a list widget
        for item in items:
            listWidget.add_widget(item)

    def get_server_address(self):
        try:
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                self.serverAddress = pickle.load(file)
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')

    def init_devices(self):
        self.get_server_address()
        # Get devices
        devices = self.get_devices()
        # Populate the device to the device list layout
        self.populate_items_to_list(self.deviceList.deviceListLayout, devices)

    def __init__(self, server_address_file='data/serveraddress.p', **kwargs):
        super().__init__(**kwargs)
        # Getting the server adrress, deserialize the serveraddress.p
        self.serverAddressFile = server_address_file
        self.init_devices()
