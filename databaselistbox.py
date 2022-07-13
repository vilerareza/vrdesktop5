from kivy.properties import BooleanProperty, ObjectProperty 
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from databaselistlayout import DatabaseListLayout
from databaseitem import DatabaseItem

Builder.load_file('databaselistbox.kv')

class DatabaseListBox(BoxLayout):

    databaseListLayout = ObjectProperty(None)
    saveFile = BooleanProperty(False)
    deleteFile = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_item(self, data_list):
        self.databaseListLayout.add_widget(DatabaseItem(data_list = data_list))

    def button_press_callback(self, widget):
        if widget == self.ids.database_delete_button:
            widget.source = "images/databaseview/database_delete_down.png"
        elif widget == self.ids.database_load_button:
            widget.source = "images/databaseview/database_load_down.png"

    def button_release_callback(self, widget):
        if widget == self.ids.database_delete_button:
            widget.source = "images/databaseview/database_delete_normal.png"
        elif widget == self.ids.database_load_button:
            widget.source = "images/databaseview/database_load_normal.png"

    def remove_item(self):
        # Remove selected data in database list layout from database 
        # self.databaseListLayout.selectedData is DatabaseItem object
        if self.databaseListLayout.isDataSelected and self.databaseListLayout.selectedData:
            id = self.databaseListLayout.selectedData.id
            App.get_running_app().manager.mainTabs.databaseView.remove_from_db(id)
        else:
            print ('Nothing to remove. No data selected')