from tkinter import ON
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

from settingview import SettingView
from multiview import Multiview
from databaseview import DatabaseView
from logview import LogView

Builder.load_file('maintabs.kv')

class MainTabs(TabbedPanel):

    multiView = ObjectProperty(None)
    settingView = ObjectProperty(None)
    databaseView = ObjectProperty(None)
    logView = ObjectProperty(None)

    tabMultiView = ObjectProperty(None)
    tabSettingView = ObjectProperty(None)
    tabDatabaseView = ObjectProperty(None)
    tabLogView = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settingView = SettingView()
        self.multiView = Multiview()
        self.databaseView = DatabaseView()
        self.logView = LogView()

        self.tabSettingView = TabbedPanelItem(content = self.settingView)
        self.add_widget(self.tabSettingView)
        self.tabMultiView = TabbedPanelItem(content = self.multiView)
        self.add_widget(self.tabMultiView)
        self.tabDatabaseView = TabbedPanelItem(content = self.databaseView)
        self.add_widget(self.tabDatabaseView)
        self.tabLogView = TabbedPanelItem(content = self.logView)
        self.add_widget(self.tabLogView)

        self.tabSettingView.bind(on_press=self.tabSettingViewPressed)
        self.tabMultiView.bind(on_press=self.refreshMultiView)
        self.tabDatabaseView.bind(on_press=self.tabDatabaseViewPressed)
        self.tabLogView.bind(on_press = self.tabLogViewPressed)

    def tabSettingViewPressed(self, tab):
        if tab.state == "down":
            # Stop the multiview
            self.multiView.stop()
    
    def refreshMultiView(self, tab):
        if tab.state == "down":
            # Refresh the device list
            self.multiView.get_server_address()
            self.multiView.get_data_from_db()
            self.multiView.start_icons()
            # Showing initLabel
            self.multiView.liveGrid.show_initlabel()
    
    def tabDatabaseViewPressed(self, tab):
        if tab.state == "down":
            # Stop the multiview
            self.multiView.stop()
            self.databaseView.get_server_address()
    
    def tabLogViewPressed(self, tab):
        if tab.state == "down":
            # Stop the multiview
            self.multiView.stop()
            self.logView.get_server_address()
            
    def stop(self):
        self.multiView.stop()