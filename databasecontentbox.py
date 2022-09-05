from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from databaseitem import DatabaseItem, FaceObjectWidget
from databasecontentface import DatabaseContentFace

Builder.load_file("databasecontentbox.kv")

class DatabaseContentBox(BoxLayout):
    databaseView = ObjectProperty(None)
    databaseListBox = ObjectProperty(None)
    noSelectionLabel = ObjectProperty(None)
    databaseContentFace = DatabaseContentFace()
    #faceAdd = SettingAddDevice()

    def change_config(self, obj = None):
        print(type(obj))
        self.clear_widgets()
        if type(obj) == FaceObjectWidget:
            # Filling the databaseContentFace with face database object
            self.databaseContentFace.fill(obj)
            self.add_widget(self.databaseContentFace)
        elif obj == self.databaseListBox:
            print ('adding a face')
            # Add device. Show settingAddDevice
            # self.add_widget(self.settingAddDevice)
        # elif type(obj) == ServerItem:
        #     # Server setting. Show settingContentServer
        #     self.settingContentServer.fill(obj)
        #     self.add_widget(self.settingContentServer)

    def no_selection_config(self, text):
        # Clearing widgets
        self.clear_widgets()
        self.noSelectionLabel.text = text
        self.add_widget(self.noSelectionLabel)

    def reinit_faces(self):
        pass
        # Reinitializing devices
        # self.settingView.refresh_devices()
        # self.settingView.init_devices()

    def update_database_item(self, new_data):
        # Update the edited data.
        self.databaseView.update_database_item(new_data)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
