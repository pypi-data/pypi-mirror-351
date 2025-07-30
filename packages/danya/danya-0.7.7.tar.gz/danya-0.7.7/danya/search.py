import requests
import importlib.resources
from .login import token

def read_txt_file(file_name):
    with importlib.resources.open_text('danya.data', file_name) as file:
        content = file.read()
    return content

class Client:
    def __init__(self, model='gpt-4o'):
        self.url = 'http://5.35.46.26:10500/chat'
        self.model = 'gpt-4o'
        self.model_selected = False
        self.system_prompt = ('В тексте ниже найди ответ по теме, которую я скажу.'
                              'Выпиши только нужный пункт из текста (1-29) целиком, ничего не пиши от себя, не меняй и не сокращай!'
                              + read_txt_file('theory_t.txt'))

    def get_response(self, message):
        headers = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': message}
        ]

        data = {
            'model': self.model,
            'messages': messages
        }

        response = requests.post(self.url, headers=headers, json=data)
        
        return response.json()['choices'][0]['message']['content']


def search(topic):
    """
    Отправляет запрос к модели для поиска в теории по заданной теме.

    Параметры:
        topic (str): Тема или запрос, который нужно отправить модели для анализа.

    Возвращает:
        str: Ответ модели, содержащий извлечённую информацию по заданной теме.
    """
    client = client = Client()

    return client.get_response(topic)