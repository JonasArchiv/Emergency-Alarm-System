from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import json


class NotificationApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical')
        self.notification_layout = GridLayout(cols=1, size_hint_y=None)
        self.notification_layout.bind(minimum_height=self.notification_layout.setter('height'))
        self.scroll_view = ScrollView()
        self.scroll_view.add_widget(self.notification_layout)
        self.root.add_widget(self.scroll_view)

        self.message_input = TextInput(size_hint_y=None, height=30, multiline=False)
        self.root.add_widget(self.message_input)

        send_button = Button(text='Send Notification', size_hint_y=None, height=50)
        send_button.bind(on_press=self.send_notification)
        self.root.add_widget(send_button)

        self.get_notifications()

        return self.root

    def add_notification(self, message):
        label = Label(text=message, size_hint_y=None, height=40)
        self.notification_layout.add_widget(label)

    def get_notifications(self):
        user_id = 1  # Replace with the user ID
        UrlRequest(f'http://localhost:5001/users/{user_id}/notifications', on_success=self.display_notifications)

    def display_notifications(self, request, result):
        for notification in result:
            self.add_notification(notification['message'])

    def send_notification(self, instance):
        message = self.message_input.text
        if message:
            user_id = 1  # Replace with the user ID
            UrlRequest(
                f'http://localhost:5001/notify/{user_id}',
                req_body=json.dumps({'message': message}),
                req_headers={'Content-Type': 'application/json'},
                on_success=self.on_notification_sent
            )
            self.message_input.text = ''

    def on_notification_sent(self, request, result):
        self.add_notification('Notification sent: ' + self.message_input.text)


if __name__ == '__main__':
    NotificationApp().run()
