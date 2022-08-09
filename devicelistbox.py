from kivy.properties import ObjectProperty 
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from devicelist import DeviceList

Builder.load_file('devicelistbox.kv')

class DeviceListBox(BoxLayout):
    deviceListLayout = ObjectProperty(None)
    serverBox = ObjectProperty(None)