from threading import Thread
import time
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

    def update_deviceitem(self, updated_device):
        # Get current devices
        for device in self.devices:
            if device.deviceID == updated_device['id']:
                # Update the device property except its hostname (not changeable)
                device.deviceName = updated_device['deviceName']
                device.wifiName = updated_device['wifiName']
                device.wifiPass = updated_device['wifiPass']
                device.deviceVisionAI = updated_device['visionAI']
                self.settingContentBox.change_config(device)

    def get_devices(self):
        # Retrieve devices from server REST API
        try:
            r = requests.get(f"{self.serverAddress}/api/device/")
            device_response = r.json()  # Produce list of dict
            for device in device_response:
                deviceID = device['id']
                deviceName = device['deviceName']
                hostName = device['hostName']
                wifiName = device['wifiName']
                wifiPass = device['wifiPass']
                deviceVisionAI = device['visionAI']
                self.devices.append(
                    DeviceItem(
                        deviceID = deviceID,
                        deviceName = deviceName,
                        host_name = hostName,
                        wifi_name = wifiName,
                        wifi_pass = wifiPass,
                        deviceVisionAI = deviceVisionAI
                        )
                    )
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
        # Get server address
        self.get_server_address()
        # Get devices
        devices = self.get_devices()
        # Populate the device to the device list layout
        self.populate_items_to_list(self.deviceList.deviceListLayout, devices)

    def start_server_checker(self):
        self.serverBox.serverItem.start_server_checker()

    def stop(self):
        # Stopping the server checker thread
        self.serverBox.serverItem.stop_server_checker()

    def __init__(self, server_address_file='data/serveraddress.p', **kwargs):
        super().__init__(**kwargs)
        # Getting the server adrress, deserialize the serveraddress.p
        self.serverAddressFile = server_address_file
        self.init_devices()
