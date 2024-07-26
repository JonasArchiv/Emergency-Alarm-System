import configparser
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen

config = configparser.ConfigParser()
config.read('config.ini')

API_URL = config.get('API', 'url', fallback='http://127.0.0.1:7070')


class LoginScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.api_key_input = TextInput(hint_text='API Key', multiline=False)
        self.user_id_input = TextInput(hint_text='User ID', multiline=False)
        self.login_button = Button(text='Login', on_press=self.verify_credentials)
        self.result_label = Label()

        self.add_widget(self.api_key_input)
        self.add_widget(self.user_id_input)
        self.add_widget(self.login_button)
        self.add_widget(self.result_label)

    def verify_credentials(self, instance):
        api_key = self.api_key_input.text
        user_id = self.user_id_input.text
        headers = {'API-Key': api_key, 'User-ID': user_id}

        try:
            response = requests.post(f'{API_URL}/api/v1/apikeycheck', json={'api_key': api_key})
            if response.status_code == 200 and response.json().get('valid'):
                config['USER'] = {'api_key': api_key, 'user_id': user_id}
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                self.parent.current = 'home'
            else:
                self.result_label.text = 'Invalid API key or User ID'
        except requests.exceptions.RequestException as e:
            self.result_label.text = 'Error connecting to server'


class HomeScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.view_users_button = Button(text='View Users', on_press=self.view_users)
        self.add_user_button = Button(text='Add User', on_press=self.add_user)
        self.edit_user_button = Button(text='Edit User', on_press=self.edit_user)
        self.delete_user_button = Button(text='Delete User', on_press=self.delete_user)

        self.add_widget(self.view_users_button)
        self.add_widget(self.add_user_button)
        self.add_widget(self.edit_user_button)
        self.add_widget(self.delete_user_button)

    def view_users(self, instance):
        self.parent.current = 'view_users'

    def add_user(self, instance):
        self.parent.current = 'add_user'

    def edit_user(self, instance):
        self.parent.current = 'edit_user'

    def delete_user(self, instance):
        self.parent.current = 'delete_user'


class ViewUsersScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.result_label = Label()
        self.refresh_button = Button(text='Refresh', on_press=self.refresh_users)
        self.back_button = Button(text='Back', on_press=self.go_back)

        self.add_widget(self.refresh_button)
        self.add_widget(self.result_label)
        self.add_widget(self.back_button)

    def refresh_users(self, instance):
        api_key = config['USER']['api_key']
        user_id = config['USER']['user_id']
        headers = {'API-Key': api_key, 'User-ID': user_id}

        try:
            response = requests.get(f'{API_URL}/api/v1/spaces/1/users', headers=headers)
            if response.status_code == 200:
                users = response.json()
                users_text = "\n".join(
                    [f"ID: {user['id']}, Username: {user['username']}, Role: {user['role']}" for user in users])
                self.result_label.text = users_text
            else:
                self.result_label.text = "Failed to retrieve users"
        except requests.exceptions.RequestException as e:
            self.result_label.text = "Error connecting to server"

    def go_back(self, instance):
        self.parent.current = 'home'


class AddUserScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.prename_input = TextInput(hint_text='Prename', multiline=False)
        self.name_input = TextInput(hint_text='Name', multiline=False)
        self.username_input = TextInput(hint_text='Username', multiline=False)
        self.email_input = TextInput(hint_text='Email', multiline=False)
        self.role_spinner = Spinner(
            text='Select Role',
            values=('normal', 'space_admin', 'alarmed')
        )
        self.result_label = Label()
        self.add_button = Button(text='Add User', on_press=self.add_user)
        self.back_button = Button(text='Back', on_press=self.go_back)

        self.add_widget(self.prename_input)
        self.add_widget(self.name_input)
        self.add_widget(self.username_input)
        self.add_widget(self.email_input)
        self.add_widget(self.role_spinner)
        self.add_widget(self.result_label)
        self.add_widget(self.add_button)
        self.add_widget(self.back_button)

    def add_user(self, instance):
        prename = self.prename_input.text
        name = self.name_input.text
        username = self.username_input.text
        email = self.email_input.text
        role = self.role_spinner.text
        api_key = config['USER']['api_key']
        user_id = config['USER']['user_id']
        headers = {'API-Key': api_key, 'User-ID': user_id}

        if not prename or not name or not username or not role:
            self.result_label.text = "Prename, name, username, and role are required"
            return

        try:
            response = requests.post(f'{API_URL}/api/v1/spaces/1/users/add', json={
                'prename': prename,
                'name': name,
                'username': username,
                'email': email,
                'role': role
            }, headers=headers)

            if response.status_code == 201:
                self.result_label.text = "User added successfully"
            elif response.status_code == 403:
                self.result_label.text = "Admin privileges required"
            else:
                self.result_label.text = "Failed to add user"
        except requests.exceptions.RequestException as e:
            self.result_label.text = "Error connecting to server"

    def go_back(self, instance):
        self.parent.current = 'home'


class EditUserScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.user_id_input = TextInput(hint_text='User ID', multiline=False)
        self.prename_input = TextInput(hint_text='Prename', multiline=False)
        self.name_input = TextInput(hint_text='Name', multiline=False)
        self.username_input = TextInput(hint_text='Username', multiline=False)
        self.email_input = TextInput(hint_text='Email', multiline=False)
        self.role_spinner = Spinner(
            text='Select Role',
            values=('normal', 'space_admin', 'alarmed')
        )
        self.result_label = Label()
        self.edit_button = Button(text='Edit User', on_press=self.edit_user)
        self.back_button = Button(text='Back', on_press=self.go_back)

        self.add_widget(self.user_id_input)
        self.add_widget(self.prename_input)
        self.add_widget(self.name_input)
        self.add_widget(self.username_input)
        self.add_widget(self.email_input)
        self.add_widget(self.role_spinner)
        self.add_widget(self.result_label)
        self.add_widget(self.edit_button)
        self.add_widget(self.back_button)

    def edit_user(self, instance):
        user_id = self.user_id_input.text
        prename = self.prename_input.text
        name = self.name_input.text
        username = self.username_input.text
        email = self.email_input.text
        role = self.role_spinner.text
        api_key = config['USER']['api_key']
        admin_user_id = config['USER']['user_id']
        headers = {'API-Key': api_key, 'User-ID': admin_user_id}

        try:
            response = requests.put(f'{API_URL}/api/v1/spaces/1/users/{user_id}', json={
                'prename': prename,
                'name': name,
                'username': username,
                'email': email,
                'role': role
            }, headers=headers)

            if response.status_code == 200:
                self.result_label.text = "User edited successfully"
            elif response.status_code == 403:
                self.result_label.text = "Admin privileges required"
            else:
                self.result_label.text = "Failed to edit user"
        except requests.exceptions.RequestException as e:
            self.result_label.text = "Error connecting to server"

    def go_back(self, instance):
        self.parent.current = 'home'


class DeleteUserScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.user_id_input = TextInput(hint_text='User ID', multiline=False)
        self.result_label = Label()
        self.delete_button = Button(text='Delete User', on_press=self.delete_user)
        self.back_button = Button(text='Back', on_press=self.go_back)

        self.add_widget(self.user_id_input)
        self.add_widget(self.result_label)
        self.add_widget(self.delete_button)
        self.add_widget(self.back_button)

    def delete_user(self, instance):
        user_id = self.user_id_input.text
        api_key = config['USER']['api_key']
        admin_user_id = config['USER']['user_id']
        headers = {'API-Key': api_key, 'User-ID': admin_user_id}

        try:
            response = requests.delete(f'{API_URL}/api/v1/spaces/1/users/{user_id}', headers=headers)

            if response.status_code == 200:
                self.result_label.text = "User deleted successfully"
            elif response.status_code == 403:
                self.result_label.text = "Admin privileges required"
            else:
                self.result_label.text = "Failed to delete user"
        except requests.exceptions.RequestException as e:
            self.result_label.text = "Error connecting to server"

    def go_back(self, instance):
        self.parent.current = 'home'


class SpaceAdminApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        self.login_screen = LoginScreen()
        screen0 = Screen(name='login')
        screen0.add_widget(self.login_screen)
        self.screen_manager.add_widget(screen0)

        self.home_screen = HomeScreen()
        screen1 = Screen(name='home')
        screen1.add_widget(self.home_screen)
        self.screen_manager.add_widget(screen1)

        self.view_users_screen = ViewUsersScreen()
        screen2 = Screen(name='view_users')
        screen2.add_widget(self.view_users_screen)
        self.screen_manager.add_widget(screen2)

        self.add_user_screen = AddUserScreen()
        screen3 = Screen(name='add_user')
        screen3.add_widget(self.add_user_screen)
        self.screen_manager.add_widget(screen3)

        self.edit_user_screen = EditUserScreen()
        screen4 = Screen(name='edit_user')
        screen4.add_widget(self.edit_user_screen)
        self.screen_manager.add_widget(screen4)

        self.delete_user_screen = DeleteUserScreen()
        screen5 = Screen(name='delete_user')
        screen5.add_widget(self.delete_user_screen)
        self.screen_manager.add_widget(screen5)

        return self.screen_manager


if __name__ == '__main__':
    SpaceAdminApp().run()
