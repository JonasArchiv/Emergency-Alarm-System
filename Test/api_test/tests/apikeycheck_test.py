import unittest
import requests
import configparser

config = configparser.ConfigParser()
config.read('test_config.ini')
base_url = f"{config['TEST_SETTINGS']['URL']}:{config['TEST_SETTINGS']['PORT']}"
apikeycheck_url = config['TEST_URLS']['apikeycheck']
valid_api_key = config['TEST_SETTINGS']['API_KEY']
invalid_api_key = config['TEST_SETTINGS']['API_KEY_INVALID']


class APIKeyCheckTestCase(unittest.TestCase):
    def test_apikeycheck_valid(self):
        response = requests.post(f'{base_url}{apikeycheck_url}', json={"api_key": valid_api_key})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("valid"))

    def test_apikeycheck_invalid(self):
        response = requests.post(f'{base_url}{apikeycheck_url}', json={"api_key": invalid_api_key})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json().get("valid"))


if __name__ == '__main__':
    unittest.main()
