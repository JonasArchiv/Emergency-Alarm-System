import configparser
import random
import string

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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prename = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(50), nullable=False)
    last_alert_sent = db.Column(db.DateTime, nullable=True)
    position = db.Column(db.String(120), nullable=True)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    space = db.relationship('Space', back_populates='users')


class Space(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    users = db.relationship('User', back_populates='space', lazy=True)


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


# API routes

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


if __name__ == '__main__':
    if config['DATABASE'].getboolean('AutoUpdate'):
        with app.app_context():
            db.create_all()
    app.run(port=int(config['DEFAULT']['port']), debug=True)
