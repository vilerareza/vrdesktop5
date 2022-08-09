import requests
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from deviceentry import DeviceEntry
from deviceinfo import DeviceInfo
from deviceitem import DeviceItem
from devicelist import DeviceList
from serverbox import ServerBox
from devicelistbox import DeviceListBox

Builder.load_file("settingview.kv")

class SettingView(BoxLayout):

    leftBox = ObjectProperty(None)
    deviceInfo = ObjectProperty(None)
    serverBox = ObjectProperty(None)
    tAddress = ObjectProperty(None)
    tName = ObjectProperty(None)
    bAdd = ObjectProperty(None)
    devices = ListProperty([])
    deviceList = ObjectProperty(None)
    

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
                r = requests.post(f"http://127.0.0.1:8000/api/device/", data = requestData)
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
                
    def save_to_db(self, deviceInfo, editMode):
        print ('save to db')
        try:
            if editMode == False:
                # User pressed "Save"
                deviceID = self.deviceList.selectedDevice.deviceID
                newDeviceName = str(self.deviceInfo.deviceNameText.text)
                newVisionAI = self.deviceInfo.visionAIActivated
                deviceData = {'deviceName': newDeviceName, 'showName': '', 'visionAI' : newVisionAI}
                r = requests.put(f"http://127.0.0.1:8000/api/device/{deviceID}/", data = deviceData)
                response = r.status_code
                print (f'Status code: {response}')
                # Refresh the device list
                self.deviceList.disabled = False
                self.devices.clear()
                # Force Device info to change config
                self.deviceList.clear_selection()
                self.deviceInfo.change_config(self.deviceList, self.deviceList.isDeviceSelected, message = "Changes saved...")
                # Do something with Device List
                self.deviceList.clear_widgets()
                devices = self.get_devices()
                # Populate device list from database
                self.populate_items_to_list(self.deviceList, devices)
                self.deviceInfo.dbDeviceNames = self.get_device_name_db()
            else:
                # Disable the device list
                self.deviceList.disabled = True
                
        except Exception as e:
            print ('Failure on saving to database')
            print (e)

    def remove_from_db(self):
        print ('remove from db')
        try:
            if self.deviceList.selectedDevice: 
                deviceID = self.deviceList.selectedDevice.deviceID
                r = requests.delete(f"http://127.0.0.1:8000/api/device/{deviceID}/")
                response = r.status_code
                print (f'Status code: {response}')
                self.refresh_devices()
        except Exception as e:
            print (e)

    def get_devices(self):
        # Retrieve devices from server REST API
        try:
            r = requests.get("http://127.0.0.1:8000/api/device")
            device_response = r.json()  # Produce list of dict
            for device in device_response:
                deviceID = device['id']
                deviceName = device['deviceName']
                deviceUrl = ''
                deviceVisionAI = device['visionAI']
                imagePath = "images/not_device_selected5.png"
                self.devices.append(DeviceItem(deviceID = deviceID, deviceName = deviceName, deviceUrl = deviceUrl, deviceVisionAI = deviceVisionAI, imagePath=imagePath, size_hint = (None, None), size = (95,85)))
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
        self.deviceList.clear_widgets()
        self.get_devices()
        for device in self.devices:
            self.deviceList.add_widget(device)

    def populate_items_to_list(self, listWidget, items):
        # Populate items to a list widget
        for item in items:
            listWidget.add_widget(item)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Get devices
        devices = self.get_devices()
        # Binding on_press event of add button
        # self.deviceEntry.bind(isNewDevice = self.add_to_db)
        # Device list
        #self.deviceList.bind(selectedDevice = self.deviceInfo.display_info)
        # Populate device list from database
        self.populate_items_to_list(self.deviceList.deviceListLayout, devices)
        # # Device info
        self.deviceInfo.bind(editMode = self.save_to_db)
        #self.deviceInfo.removeButton.bind(on_press = self.deviceList.clear_selection)
        #self.deviceInfo.bind(visionAIActivated = self.deviceList.activate_neuralnet_to_selected_device)
        self.deviceInfo.dbDeviceNames = self.get_device_name_db()
        # Binding Device Info and Device List
        #self.deviceList.bind(isDeviceSelected = self.deviceInfo.change_config)
