import requests

url = "http://localhost:7070/api/v1/users/add"

payload = {
    "api_key": "XXXX-XXXXX-XXXXX-XXXX",
    "prename": "John",
    "name": "Doe",
    "username": "johndoe",
    "email": "john.doe@example.com",
    "role": "normal"
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())
