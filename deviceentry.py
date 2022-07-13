import os
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.textfield import MDTextField

import uuid
import qrcode
import json

Builder.load_file("deviceentry.kv")

class DeviceEntry(FloatLayout):

    buttonAdd = ObjectProperty(None)
    addLabel = ObjectProperty(None)

    titleLabel = ObjectProperty()
    deviceNameText = ObjectProperty(None)
    netSSIDText = ObjectProperty(None)
    netPassword = ObjectProperty(None)
    actionButton = ObjectProperty(None)
    cancelButton = ObjectProperty(None)
    qrImage = ObjectProperty(None)

    entryMode = BooleanProperty(False)

    isNewDevice = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def entry_mode(self, widget):
        # Hiding
        self.buttonAdd.disabled = True
        self.addLabel.disabled = True
        # Displaying
        self.display_widget(self.titleLabel, self.deviceNameText, self.netSSIDText, self.netPassword,
                           self.actionButton, self.ids.action_button_label, self.cancelButton, self.ids.cancel_label, self.qrImage)
        #self.add_widget(self.cancelButton)
        #self.add_widget(self.messageLabel)

    def icon_mode(self, widget = None):
        # Hiding
        self.titleLabel.disabled = True
        self.actionButton.disabled = True
        self.ids.action_button_label.disabled = True
        self.cancelButton.disabled = True
        self.ids.cancel_label.disabled = True
        self.qrImage.disabled = True
        self.hide_text(self.deviceNameText, self.netSSIDText, self.netPassword)
        #self.messageLabel.text = ""
        # Displaying
        self.display_widget(self.buttonAdd, self.addLabel)

    def hide_text(*text_inputs):
        print ('hiding')
        for text_input in text_inputs:
            text_input.text = ""    # Clearing text anyway 
            text_input.disabled = True
            text_input.background_color = (0.8, 0.8, 0.8)   # Resetting backround color anyway

    def display_widget(*widgets):
        for widget in widgets:
            widget.disabled = False

    def on_save(self, button):
        if (str(self.deviceNameText.text) != "") and (str(self.deviceUrlText.text)!=""):
            self.isNewDevice = True

    def button_press_callback(self, widget):
        if widget == self.actionButton:
            widget.source = "images/settingview/action_button_down.png"
        elif widget == self.cancelButton:
            widget.source = "images/settingview/cancel_button_down.png"
    
    def button_release_callback(self, widget):
        if widget == self.actionButton:
            widget.source = "images/settingview/action_button_normal.png"
        elif widget == self.cancelButton:
            widget.source = "images/settingview/cancel_button_normal.png"

    def validate_entry(self, *args):
        isValid = True
        for entry in args:    
            if entry.text == '':
                isValid = False
                entry.background_color = (0.9, 0.7, 0.7)
            else:
                entry.background_color = (0.8, 0.8, 0.8)
        return isValid

    def add_new_device(self, *args):
        # Callback function for 'next' (action) button
        if self.validate_entry(*args):
            host  = self.create_host_name(prefix = 'vr')
            name = self.deviceNameText.text
            ssid = self.netSSIDText.text
            psk = self.netPassword.text
            qrDict = {'host': host, 'name':name, 'ssid':ssid, 'psk':psk}
            self.generate_qr (qrDict)
            self.isNewDevice = True
            #self.imageReviewButton.disabled = True
            #self.display_status(self.statusLabel, 'loading images...')
            #Clock.schedule_once(self.display_preview_data, 0)
    
    def generate_qr(self, dict):
        # Remove previous qr image file
        qrImageLoc  = 'images/temp/qr/'
        qrImage = os.listdir(qrImageLoc)
        for image in qrImage:
            os.remove(os.path.join(qrImageLoc, image))
        # Init QR generator
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=5,
            border=4)
        data = json.dumps(dict)
        qr.add_data(str(data))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # Saving QR image and display it
        qrFileName = f'{qrImageLoc}{str(uuid.uuid4())[0:8]}.png'
        img.save(qrFileName)
        self.qrImage.source = qrFileName
    
    def create_host_name(self, prefix):
        rand = str(uuid.uuid4())[0:8]
        hostName = f'{prefix}{rand}'
        return hostName