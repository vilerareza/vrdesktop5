import pickle
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout

Builder.load_file("serveritem.kv")

class ServerItem(FloatLayout):
    serverImage = ObjectProperty(None)
    statusImage = ObjectProperty(None)
    serverAddressFile = ''
    serverAddress = ''

    def __init__(self, server_address_file='data/serveraddress.p', **kwargs):
        super().__init__(**kwargs)
        try:
            self.serverAddressFile = server_address_file
            # Load the server address
            with open(self.serverAddressFile, 'rb') as file:
                self.serverAddress = pickle.load(file)
        except Exception as e:
            print(f'{e}: Failed loading server address: {e}')

    def update_server_addr(self, server_address = ''):
        # Serialize server address to file
        try:
            with open(self.serverAddressFile, 'wb') as file:
                pickle.dump(server_address, file)
                self.serverAddress = server_address
        except Exception as e:
            print (f'Saving server address failed: {e}')


