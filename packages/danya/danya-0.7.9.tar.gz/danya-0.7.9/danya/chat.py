import requests
from datetime import datetime
from .login import token, username

BASE_URL = "5.35.46.26:10500"
SEND_URL = f"http://{BASE_URL}/send"
GET_URL = f"http://{BASE_URL}/get"


def send(content):
    """
    Отправляет сообщение в чат.

    Аргументы:
        content (str): Содержимое сообщения.

    Возвращает:
        int | None: Идентификатор сообщения, если успешно, иначе None.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "username": username,
        "content": content
    }

    r = requests.post("http://5.35.46.26:10500/send", json=data, headers=headers)
    if r.status_code == 200:
        msg_id = r.json().get("message_id")
        return msg_id
    print(f"Ошибка при отправке сообщения: {r.text}")


def hist(n=10, last_id=None):
    """
    Выводит историю сообщений из чата.

    Аргументы:
        last_id (int, optional): Идентификатор последнего сообщения для фильтрации. По умолчанию None.
        n (int, optional): Количество сообщений для отображения. По умолчанию 10.

    Возвращает:
        int | None: Идентификатор последнего сообщения, если успешно, иначе None.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {"limit": n}
    if last_id is not None:
        payload["last_id"] = last_id

    try:
        
        url = GET_URL + '?'

        if payload.get('last_id') is not None:
            url += f'last_id={last_id}&'
        if payload.get('limit') is not None:
            url += f'n={n}'

        response = requests.post(url, headers=headers)
        response.raise_for_status() 
    except requests.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None

    msgs = response.json()
    if not msgs:
        print("История сообщений пуста.")
        return None

    for msg in msgs:
        timestamp = msg.get('timestamp', 'unknown')
        try:
            ts = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            ts = timestamp  
        print(f"[{msg['id']} – {ts}] {msg.get('username', 'unknown')}: {msg.get('content', '')}")
    return msgs[-1]['id'] if msgs else None



