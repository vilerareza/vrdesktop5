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
                self.parent.settingView.save_device_to_db(self)

    def button_press_callback(self, button):
        if button == self.btnRemove:
            button.source = 'images/settingview/btn_remove_down.png'

    def button_release_callback(self, button):
        if button == self.btnRemove:
            button.source = 'images/settingview/btn_remove.png'

    def fill(self, device_obj):
        if device_obj:
            self.deviceNameText.text = device_obj.deviceName
            #wifiNameText = ObjectProperty(None)
            #wifiPassText = ObjectProperty(None)
            self.visionAISwitch.active = device_obj.deviceVisionAI

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



