from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
import requests
import configparser


class VerifyUserScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.api_key_input = TextInput(hint_text='API Key')
        self.username_input = TextInput(hint_text='Username')
        self.result_label = Label()
        self.verify_button = Button(text='Verify', on_press=self.verify_user)

        self.add_widget(self.api_key_input)
        self.add_widget(self.username_input)
        self.add_widget(self.result_label)
        self.add_widget(self.verify_button)

    def verify_user(self, instance):
        api_key = self.api_key_input.text
        username = self.username_input.text

        if not api_key or not username:
            self.result_label.text = "API key and username are required"
            return

        config = configparser.ConfigParser()
        config.read('config.ini')
        api_url = config['API']['url']

        response = requests.post(f'{api_url}/api/v1/verify_user', json={'api_key': api_key, 'username': username})

        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                self.result_label.text = f"User '{username}' is valid. User ID: {data.get('user_id')}"
            else:
                self.result_label.text = f"User '{username}' is not valid"
        else:
            self.result_label.text = "Error verifying user"


class Allinoneapp(App):
    def build(self):
        return VerifyUserScreen()


if __name__ == '__main__':
    Allinoneapp().run()
