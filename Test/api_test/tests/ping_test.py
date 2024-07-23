import unittest
import requests
import configparser
from termcolor import colored

config = configparser.ConfigParser()
config.read('test_config.ini')
base_url = config['TEST_SETTINGS']['URL'] + ':' + config['TEST_SETTINGS']['PORT']
ping_url = config['TEST_URLS']['ping']


class PingTestCase(unittest.TestCase):
    def test_ping(self):
        response = requests.get(f'{base_url}{ping_url}')
        if response.status_code == 200:
            print(colored("/ping -> Pass", "green"), "✓")
        else:
            print(colored("/ping -> Fail", "red"), "✗")
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
