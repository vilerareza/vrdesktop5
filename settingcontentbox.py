from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from serveritem import ServerItem
from deviceitem import DeviceItem
from settingcontentserver import SettingContentServer
from settingcontentdevice import SettingContentDevice
from settingadddevice import SettingAddDevice

Builder.load_file("settingcontentbox.kv")

class SettingContentBox(BoxLayout):
    settingView = ObjectProperty(None)
    serverBox = ObjectProperty(None)
    deviceList = ObjectProperty(None)
    noSelectionLabel = ObjectProperty(None)
    noSelectionText = 'Select Server or Camera for Setting...'
    settingContentServer = SettingContentServer()
    settingContentDevice = SettingContentDevice()
    settingAddDevice = SettingAddDevice()

    def change_config(self, obj = None):
        self.clear_widgets()
        if type(obj) == DeviceItem:
            # Filling the settingContentDevice with object attribute
            self.settingContentDevice.get_device_obj(obj)
            self.add_widget(self.settingContentDevice)
        elif obj == self.deviceList:
            # Add device. Show settingAddDevice
            self.add_widget(self.settingAddDevice)
        elif type(obj) == ServerItem:
            # Server setting. Show settingContentServer
            self.settingContentServer.fill(obj)
            self.add_widget(self.settingContentServer)

    def no_selection_config(self):
        # Clearing widgets
        self.clear_widgets()
        self.add_widget(self.noSelectionLabel)

    def reinit_devices(self):
        # Reinitializing devices
        self.settingView.refresh_devices()
        self.settingView.init_devices()

    def update_deviceitem(self, new_device):
        # Update the edited device. new_device_obj is the new data for edited device
        self.settingView.update_deviceitem(new_device)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
