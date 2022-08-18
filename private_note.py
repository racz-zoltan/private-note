# Copyright (c) 2022 Rácz Zoltán


import kivy
kivy.require('2.0.0')
import kivymd

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.toast import toast
from kivy.resources import resource_add_path

import sys, os
import pyotp
import hashlib
from Crypto.Cipher import AES


maxSize = Window.system_size


desiredSize = (maxSize[0]*0.4, maxSize[1]*0.8)
Window.size = desiredSize


Window.left = maxSize[0]*0.3
Window.top = maxSize[1]*0.1




iteration_number = 100000
salt = b'U\x96\xcb\x80"\x15$\xcb\xf4\x1f\x04\xd0\x10\xd9\x0c\x16\xfe\x04.\xda<%D\x92\xe9\xf8\xc2\xeeL\xc4F\x90'
totp_base = "7SAGMTE5DCGVKRIOJXL6DPA2MRYCOBRY"

filename = 'private_note.bin'

privatenote_isExist = os.path.exists(filename)




class MainViewWindow(Screen):
	pass


class OTPWindow(Screen):
    password_mask = StringProperty("•")



class WindowManager(ScreenManager):
    ScreenManager(transition=FadeTransition())
    pass




class PrivateNote(MDApp):

        def build(self):
            self.theme_cls.material_style = "M3"
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "DeepPurple"
            return Builder.load_file('private_note.kv')




        def on_start(self):
            self.root.current = "one-time-password"
            self.root.transition.direction = "up"

            if not privatenote_isExist:
                self.create_note_at_start()



        def deactivate(self):
                self.root.current = "one-time-password"
                self.root.transition.direction = "down"



        def release_one_time_pass(self):

            otp_start = self.root.ids.otplogin.ids.onetimepass.text

            totp = pyotp.TOTP(totp_base)

            if otp_start == str(totp.now()):
                self.root.current = "mainview"
                self.root.transition.direction = "up"
                self.root.ids.otplogin.ids.onetimepass.text = ""

            else:
                self.root.ids.otplogin.ids.onetimepass.text = ""
                self.toast_incorrect_totp()



        def create_note_at_start(self):

            private_note = ' '

            bytenotes = bytes(private_note, 'utf-8')

            key = hashlib.pbkdf2_hmac(
            'sha256',
            totp_base.encode('utf-8'),
            salt,
            iteration_number, 
            dklen=16 
            )

            cipher = AES.new(key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(bytenotes)

            file_out = open(filename, "wb")
            [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
            file_out.close()



        def reveal_private_text(self):

            key = hashlib.pbkdf2_hmac(
            'sha256',
            totp_base.encode('utf-8'),
            salt,
            iteration_number, 
            dklen=16 
            )


            file_in = open(filename, "rb")
            nonce, tag, ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]


            cipher = AES.new(key, AES.MODE_EAX, nonce)
            decrypted_key = cipher.decrypt_and_verify(ciphertext, tag)
            revealed_text = decrypted_key.decode('UTF-8')

            self.root.ids.mainview.ids.privatenotes.text = revealed_text

            self.root.ids.mainview.ids.privatenotesbar.left_action_items = [["content-save-outline", lambda x: self.save_private_text(), "Save note", "Save note"]]




        def save_private_text(self):

            private_text_to_save = self.root.ids.mainview.ids.privatenotes.text

            bytetext = bytes(private_text_to_save, 'utf-8')

            key = hashlib.pbkdf2_hmac(
            'sha256',
            totp_base.encode('utf-8'),
            salt,
            iteration_number, 
            dklen=16 
            )

            cipher = AES.new(key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(bytetext)

            file_out = open(filename, "wb")
            [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]
            file_out.close()

            self.root.ids.mainview.ids.privatenotes.text = ""

            self.root.ids.mainview.ids.privatenotesbar.left_action_items = [["note-edit-outline", lambda x: self.reveal_private_text(), "Open note", "Open note"]]

            self.toast_note_saved()




        def toast_incorrect_totp(self):
            toast('One Time Password is incorrect')


        def toast_note_saved(self):
            toast('Note saved')



if __name__ == '__main__':
        if hasattr(sys, '_MEIPASS'):
            resource_add_path(os.path.join(sys._MEIPASS))
        PrivateNote().run()
