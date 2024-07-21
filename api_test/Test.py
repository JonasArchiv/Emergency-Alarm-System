import configparser

config = configparser.ConfigParser()
config.read('test_config.ini')

base_url = config['TEST_SETTINGS']['URL'] + ':' + config['TEST_SETTINGS']['PORT']
print(base_url)
