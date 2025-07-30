import requests
import importlib.resources
import base64
from .login import token


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

        if self.model in ['o3-mini', 'o1']:
            data['reasoning_effort'] = 'medium'

        try:
            response = requests.post(self.url, headers=headers, json=data, timeout=120) 
            response.raise_for_status() 

            json_response = response.json()
            if 'choices' in json_response and \
               isinstance(json_response['choices'], list) and \
               len(json_response['choices']) > 0 and \
               'message' in json_response['choices'][0] and \
               'content' in json_response['choices'][0]['message']:
                return json_response['choices'][0]['message']['content']
            elif 'message' in json_response and 'content' in json_response['message']:
                 print("Warning: Received response in non-standard 'message.content' format.")
                 return json_response['message']['content']
            else:
                print(f"Error: Unexpected response structure from API: {json_response}")
                return f"Error: Unexpected response structure: {json_response}"


        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return f"Error: Could not connect to the API or invalid response: {e}"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raw_response = response.text if 'response' in locals() else "N/A"
            print(f"Raw response: {raw_response}")
            return f"Error: An unexpected error occurred: {e}"



def read_txt_file(file_name):
    with importlib.resources.open_text('danya.data', file_name) as file:
        content = file.read()
    return content


def ask(message, m=1):
    """
    Отправляет запрос к модели и возвращает ответ.

    Параметры:
        message (str): Текст запроса, который нужно отправить модели.
        m (int): Номер модели, которую нужно использовать. 
                 Поддерживаемые значения:
                 1 - 'gpt-4o'(по умолчанию)
                 2 - 'gpt-4.1'

    Возвращает:
        str: Ответ модели на заданное сообщение.
    """
    model_map = {1: 'gpt-4o', 2: 'gpt-4.1'}
    client = Client()
    if m in model_map:
        client.model = model_map[m]
    return client.get_response(message)

def get(a='m'):
    """
    Возвращает содержимое одного из предопределённых текстовых файлов с ДЗ, семинарами и теорией.

    Параметры:
        a (str): Имя автора файла.
                     - 'а' для Тёмы
                     - 'д' для Дани
                     - 'м' для Миши
    Возвращает:
        str: Содержимое выбранного файла.
    """
    authors = {'а': 'artyom', 'д': 'danya', 'м': 'misha'}
    a = a.lower().replace('d', 'д').replace('a', 'а').replace('m', 'м')
    author_name = authors.get(a, 'artyom')
    filename = f"{author_name}_{'dl'}.txt"
    
    return read_txt_file(filename)
        
