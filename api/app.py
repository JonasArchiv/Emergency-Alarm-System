import configparser
from flask import Flask, request

app = Flask(__name__)


def load_config_value(section, key):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config[section][key]


@app.route('/ping', methods=['GET'])
def ping():
    response = {
        "status": "online",
        "version": load_config_value('DEFAULT', 'version'),
        "react": "pong",
    }
    return response, 200


if __name__ == '__main__':
    app.run(port=load_config_value('DEFAULT', 'port'))
