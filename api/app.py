import configparser
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)


@app.route('/api/v1/apikeycheck', methods=['POST'])
def apikey_check():
    api_key = request.json.get('api_key')
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    space = Space.query.filter_by(api_key=api_key).first()
    if space:
        return jsonify({"valid": True}), 200
    else:
        return jsonify({"valid": False}), 404


@app.route('/api/v1/ping', methods=['GET'])
def ping():
    response = {
        "status": "online",
        "build_version": config['API_V1']['build_version'],
        "react": "pong",
    }
    return jsonify(response), 200


if __name__ == '__main__':
    if config['DATABASE'].getboolean('AutoUpdate'):
        with app.app_context():
            db.create_all()
    app.run(port=int(config['DEFAULT']['port']), debug=True)
