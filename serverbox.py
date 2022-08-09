from kivy.lang import Builder
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ToggleButtonBehavior

Builder.load_file("serverbox.kv")

class ServerBox(FloatLayout):

    serverIcon = ObjectProperty(None)
    titleLabel = ObjectProperty(None)
    deviceListLayout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def icon_press_callback(self, icon):
        if icon.state == 'down':
            icon.serverImage.source = "images/settingview/servericon_down.png"
            # Clearing the selection on device list layout
            self.deviceListLayout.clear_selection()
        else:
            icon.serverImage.source = "images/settingview/servericon_normal.png"
    
    def deselect_serverIcon(self):
        self.serverIcon.state = 'normal'