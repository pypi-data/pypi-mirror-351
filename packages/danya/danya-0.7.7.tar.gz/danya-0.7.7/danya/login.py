import requests
import base64

token = None
username = None
def login():
    global token
    global username
    username = input('usr')
    password = input('pwd')

    credentials = f"{username}:{password}"
    token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }
    response = requests.post("http://5.35.46.26:10500/get?n=100", headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Ошибка: код ответа {response.status_code}, описание: {response.text}")
