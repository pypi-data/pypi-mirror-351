import requests
import importlib.resources
import base64
import openai
from .login import token

# Подключаемся к OpenAI (старый API-клиент, версия <=0.28)
openai.api_key = "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"

class Client:
    def __init__(self, model='gpt-4o'):
        self.url = 'http://5.35.46.26:10500/chat'
        self.model = model
        self.system_prompt = (
            'Всегда форматируй все формулы и символы в Unicode или ASCII. '
            'Не используй LaTeX или другие специальные вёрстки. '
            'Пиши по-русски.'
        )

    def get_response(self, message):
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user',   'content': message}
        ]

        # Для официальных OpenAI-моделей gpt-4.1 и o4-mini
        if self.model in ['gpt-4.1', 'o4-mini']:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
            )
            return resp.choices[0].message.content

        # Для всех остальных — на ваш локальный сервер
        headers = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.model,
            'messages': messages
        }
        if self.model in ['o3-mini', 'o1']:
            data['reasoning_effort'] = 'medium'

        try:
            response = requests.post(self.url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            jr = response.json()
            return jr['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as e:
            print("Status code:", e.response.status_code)
            print("Response body:", e.response.text)
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raw = response.text if 'response' in locals() else "N/A"
            print(f"Raw response: {raw}")
            return f"Error: {e}"

def read_txt_file(file_name):
    with importlib.resources.open_text('danya.data', file_name) as file:
        return file.read()

def ask(message, m=1):
    """
    Отправляет запрос к модели и возвращает ответ.

    Параметры:
        message (str): текст запроса.
        m (int): номер модели:
                 1 — gpt-4o (локальная),
                 2 — gpt-4.1 (официальная OpenAI),
                 3 — o4-mini (официальная OpenAI, облегчённая).
    Возвращает:
        str: ответ модели.
    """
    model_map = {
        1: 'gpt-4o',
        2: 'gpt-4.1',
        3: 'o4-mini'
    }
    client = Client()
    if m in model_map:
        client.model = model_map[m]
    return client.get_response(message)

def get(a='m'):
    """
    Возвращает содержимое файла с материалами по автору:
        'а' — artyom,
        'д' — danya,
        'м' — misha.
    """
    authors = {'а': 'artyom', 'д': 'danya', 'м': 'misha'}
    a = a.lower().replace('d', 'д').replace('a', 'а').replace('m', 'м')
    name = authors.get(a, 'artyom')
    return read_txt_file(f"{name}_dl.txt")