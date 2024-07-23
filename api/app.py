import configparser
import random
import string
from datetime import datetime
import requests

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prename = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(50), nullable=False)  # normal, space_admin, alarmed
    last_alert_sent = db.Column(db.DateTime, nullable=True)
    position = db.Column(db.String(120), nullable=True)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    space = db.relationship('Space', back_populates='users')
    alarms = db.relationship('Alarm', back_populates='user', lazy=True)


class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    users = db.relationship('User', back_populates='space', lazy=True)
    alarms = db.relationship('Alarm', back_populates='space', lazy=True)


class Alarm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    position = db.Column(db.String(200), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 0: info, 1: warning, 2: critical
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', back_populates='alarms')
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    space = db.relationship('Space', back_populates='alarms')


def generate_api_key():
    sections = [
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    ]
    return '-'.join(sections)


@app.route('/spaces/add', methods=['GET', 'POST'])
def add_space():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        if password != config['ADMIN']['password']:
            return jsonify({"error": "Invalid admin password"}), 403

        if not name:
            return jsonify({"error": "Space name is required"}), 400

        api_key = generate_api_key()
        new_space = Space(name=name, api_key=api_key)
        db.session.add(new_space)
        db.session.commit()

        return jsonify({"message": "Space created successfully", "api_key": api_key}), 201

    return render_template('add_space.html')


@app.route('/spaces/list', methods=['GET'])
def list_spaces():
    spaces = Space.query.all()
    space_list = [{"id": space.id, "name": space.name, "api_key": space.api_key} for space in spaces]
    return jsonify(space_list), 200


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


@app.route('/api/v1/users/add', methods=['POST'])
def add_user():
    api_key = request.json.get('api_key')
    prename = request.json.get('prename')
    name = request.json.get('name')
    username = request.json.get('username')
    email = request.json.get('email')
    role = request.json.get('role')

    if not api_key or not prename or not name or not username or not role:
        return jsonify({"error": "API key, prename, name, username, and role are required"}), 400

    space = Space.query.filter_by(api_key=api_key).first()
    if not space:
        return jsonify({"error": "Invalid API key"}), 404

    if User.query.filter_by(username=username).first() or (email and User.query.filter_by(email=email).first()):
        return jsonify({"error": "Username or email already exists"}), 409

    new_user = User(prename=prename, name=name, username=username, email=email, role=role, space_id=space.id)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201


@app.route('/api/v1/spaces/<int:space_id>/alarms', methods=['GET'])
def get_space_alarms(space_id):
    api_key = request.headers.get('API-Key')
    space = Space.query.filter_by(id=space_id, api_key=api_key).first()

    if not space:
        return jsonify({"error": "Invalid API key or space does not exist"}), 403

    alarms = Alarm.query.filter_by(space_id=space.id).all()
    alarm_list = [{"id": alarm.id, "message": alarm.message, "timestamp": alarm.timestamp, "position": alarm.position,
                   "level": alarm.level, "user_id": alarm.user_id} for alarm in alarms]
    return jsonify(alarm_list), 200


@app.route('/api/v1/spaces/<int:space_id>/users', methods=['GET'])
def get_space_users(space_id):
    api_key = request.headers.get('API-Key')
    space = Space.query.filter_by(id=space_id, api_key=api_key).first()

    if not space:
        return jsonify({"error": "Invalid API key or space does not exist"}), 403

    users = User.query.filter_by(space_id=space.id).all()
    user_list = [
        {"id": user.id, "prename": user.prename, "name": user.name, "username": user.username, "email": user.email,
         "role": user.role} for user in users]
    return jsonify(user_list), 200


@app.route('/api/v1/emergency', methods=['POST'])
def emergency_alarm():
    api_key = request.json.get('api_key')
    position = request.json.get('position')
    message = request.json.get('message')
    level = request.json.get('level')
    user_id = request.json.get('user_id')

    if not api_key or not position or not message or level is None or not user_id:
        return jsonify({"error": "API key, position, message, level, and user_id are required"}), 400

    space = Space.query.filter_by(api_key=api_key).first()
    if not space:
        return jsonify({"error": "Invalid API key"}), 403

    user = User.query.filter_by(id=user_id, space_id=space.id).first()
    if not user:
        return jsonify({"error": "Invalid user or user not associated with the space"}), 403

    new_alarm = Alarm(
        message=message,
        position=position,
        level=level,
        space_id=space.id,
        user_id=user.id
    )
    db.session.add(new_alarm)
    db.session.commit()

    notify_users(space.id, new_alarm)

    return jsonify({"message": "Emergency alarm created successfully", "alarm_id": new_alarm.id}), 201


def notify_users(space_id, alarm):
    users_to_notify = User.query.filter(
        User.space_id == space_id,
        User.role.in_(['space_admin', 'alarmed'])
    ).all()

    notification_url = config['NOTIFICATION_SERVICE']['url']

    for user in users_to_notify:
        payload = {
            "message": alarm.message,
            "position": alarm.position,
            "level": alarm.level,
            "timestamp": alarm.timestamp.isoformat()
        }

        try:
            requests.post(f"{notification_url}/{user.id}", json=payload)
        except requests.RequestException as e:
            app.logger.error(f"Failed to send notification to user {user.id}: {e}")


if __name__ == '__main__':
    if config['DATABASE'].getboolean('AutoUpdate'):
        with app.app_context():
            db.create_all()
    app.run(port=int(config['DEFAULT']['port']), debug=True)
