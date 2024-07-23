from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/notify/<int:user_id>', methods=['POST'])
def notify(user_id):
    data = request.json

    # Send Notification
    print(f"Sending notification to user {user_id}: {data}")

    return jsonify({"status": "Notification sent"}), 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)
