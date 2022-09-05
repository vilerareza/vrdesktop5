from kivy.properties import BooleanProperty, ObjectProperty 
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from databaselistlayout import DatabaseListLayout
from databaseitem import DatabaseItem
from databasecontentbox import DatabaseContentBox

Builder.load_file('databaselistbox.kv')

class DatabaseListBox(BoxLayout):

    databaseView = ObjectProperty(None)
    databaseContentBox = ObjectProperty(None)
    databaseListLayout = ObjectProperty(None)
    btnAdd = ObjectProperty(None)
    btnRefresh = ObjectProperty
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_item(self, data_list):
        self.databaseListLayout.add_widget(DatabaseItem(data_list = data_list))

    def button_press_callback(self, widget):
        if widget == self.btnAdd:
            widget.source = "images/databaseview/btn_add_icon_down.png"
        elif widget == self.btnRefresh:
            widget.source = "images/databaseview/btn_refresh_down.png"

    def button_release_callback(self, widget):
        if widget == self.btnAdd:
            widget.source = "images/databaseview/btn_add_icon.png"
            self.databaseContentBox.change_config(self)
        elif widget == self.btnRefresh:
            widget.source = "images/databaseview/btn_refresh.png"

    def remove_item(self):
        # Remove selected data in database list layout from database 
        # self.databaseListLayout.selectedData is DatabaseItem object
        if self.databaseListLayout.isDataSelected and self.databaseListLayout.selectedData:
            id = self.databaseListLayout.selectedData.id
            App.get_running_app().manager.mainTabs.databaseView.remove_from_db(id)
        else:
            print ('Nothing to remove. No data selected')