@app.route('/ping', methods=['GET'])
def ping():
    response = OrderedDict([
        ("status", "online"),
        ("version", load_config_value('DEFAULT', 'version')),
        ("easter egg", "pong"),
    ])
    return response, 200