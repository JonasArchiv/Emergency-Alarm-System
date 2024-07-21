import unittest
import requests
import configparser
from termcolor import colored

config = configparser.ConfigParser()
config.read('test_config.ini')
base_url = config['TEST_SETTINGS']['URL'] + ':' + config['TEST_SETTINGS']['PORT']
apikeycheck_url = config['TEST_URLS']['apikeycheck']
valid_api_key = config['TEST_SETTINGS']['API_KEY']
invalid_api_key = config['TEST_SETTINGS']['API_KEY_INVALID']


class APIKeyCheckTestCase(unittest.TestCase):
    def test_apikeycheck_valid(self):
        response = requests.post(f'{base_url}{apikeycheck_url}', json={"api_key": valid_api_key})
        if response.status_code == 200 and response.json().get("valid") is True:
            print(colored("/apikeycheck (valid key) -> Pass", "green"), "✓")
        else:
            print(colored("/apikeycheck (valid key) -> Fail", "red"), "✗")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("valid"))

    def test_apikeycheck_invalid(self):
        response = requests.post(f'{base_url}{apikeycheck_url}', json={"api_key": invalid_api_key})
        if response.status_code == 404 and response.json().get("valid") is False:
            print(colored("/apikeycheck (invalid key) -> Pass", "green"), "✓")
        else:
            print(colored("/apikeycheck (invalid key) -> Fail", "red"), "✗")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json().get("valid"))


if __name__ == '__main__':
    unittest.main()
