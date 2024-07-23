from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    notifications = db.relationship('Notification', back_populates='user', lazy=True)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='notifications')


@app.route('/users/add', methods=['POST'])
def add_user():
    username = request.json.get('username')
    email = request.json.get('email')

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "Username or email already exists"}), 409

    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201


@app.route('/notify/<int:user_id>', methods=['POST'])
def notify_user(user_id):
    message = request.json.get('message')

    if not message:
        return jsonify({"error": "Message is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    new_notification = Notification(message=message, user_id=user_id)
    db.session.add(new_notification)
    db.session.commit()

    # Emit notification via WebSocket
    socketio.emit('notification', {
        "user_id": user_id,
        "message": message,
        "timestamp": new_notification.timestamp.isoformat()
    }, namespace='/notify')

    return jsonify({"message": "Notification sent successfully"}), 201


@app.route('/users/<int:user_id>/notifications', methods=['GET'])
def get_user_notifications(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    notifications = Notification.query.filter_by(user_id=user_id).all()
    notification_list = [{"id": n.id, "message": n.message, "timestamp": n.timestamp} for n in notifications]

    return jsonify(notification_list), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, port=5001, debug=True)
