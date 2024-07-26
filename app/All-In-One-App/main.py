import json
import requests
import configparser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.storage.jsonstore import JsonStore

config = configparser.ConfigParser()
config.read('config.ini')

API_URL = config['API']['url']

user_store = JsonStore('user_data.json')


class VerifyUserScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.api_key_input = TextInput(hint_text='API Key', multiline=False)
        self.username_input = TextInput(hint_text='Username', multiline=False)
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

        response = requests.post(f'{API_URL}/api/v1/verify_user', json={'api_key': api_key, 'username': username})

        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                user_store.put('user', api_key=api_key, username=username, user_id=data.get('user_id'))
                self.result_label.text = f"User '{username}' is valid. Redirecting to alarm page..."
                self.manager.current = 'alarm'
            else:
                self.result_label.text = f"User '{username}' is not valid"
        else:
            self.result_label.text = "Error verifying user"


class AlarmScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.level_spinner = Spinner(
            text='Select Level',
            values=('Info', 'Warning', 'Critical')
        )

        self.message_input = TextInput(hint_text='Message', multiline=True)
        self.alarm_button = Button(text='Trigger Alarm', on_press=self.trigger_alarm)
        self.result_label = Label()

        self.add_widget(self.level_spinner)
        self.add_widget(self.message_input)
        self.add_widget(self.alarm_button)
        self.add_widget(self.result_label)

    def trigger_alarm(self, instance):
        if 'user' in user_store:
            user_data = user_store.get('user')
            api_key = user_data['api_key']
            user_id = user_data['user_id']

            level_map = {'Info': 0, 'Warning': 1, 'Critical': 2}
            level = level_map.get(self.level_spinner.text, 0)

            alarm_data = {
                'api_key': api_key,
                'position': 'Location XYZ',
                'message': self.message_input.text,
                'level': level,  # Alarm level based on dropdown selection
                'user_id': user_id
            }

            response = requests.post(f'{API_URL}/api/v1/emergency', json=alarm_data)

            if response.status_code == 201:
                self.result_label.text = "Alarm triggered successfully"
            else:
                self.result_label.text = "Failed to trigger alarm"
        else:
            self.result_label.text = "User not authenticated, please verify first."


class MainApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        self.verify_user_screen = VerifyUserScreen()
        screen1 = Screen(name='verify_user')
        screen1.add_widget(self.verify_user_screen)
        self.screen_manager.add_widget(screen1)

        self.alarm_screen = AlarmScreen()
        screen2 = Screen(name='alarm')
        screen2.add_widget(self.alarm_screen)
        self.screen_manager.add_widget(screen2)

        if 'user' in user_store:
            self.screen_manager.current = 'alarm'
        else:
            self.screen_manager.current = 'verify_user'

        return self.screen_manager


if __name__ == '__main__':
    MainApp().run()
