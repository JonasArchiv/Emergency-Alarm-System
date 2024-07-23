import requests

notification_url = 'http://localhost:5001/notify'

test_user_id = 1
test_payload = {
    "message": "Testbenachrichtigung",
    "position": "Testposition",
    "level": 1,
    "timestamp": "2024-07-23T15:00:00"
}

try:
    response = requests.post(f"{notification_url}/{test_user_id}", json=test_payload)
    response.raise_for_status()

    print("Serverantwort:", response.json())
except requests.RequestException as e:
    print(f"Fehler beim Senden der Benachrichtigung: {e}")
