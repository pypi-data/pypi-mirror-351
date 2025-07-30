"""
Библиотека для взаимодействия с моделями AI через API.

Основные функции:
    - ask: Отправляет запрос к модели и возвращает ответ.
    - get: Возвращает содержимое определённого текстового файла с ДЗ, семинарами и теорией.
    - send: Отправляет сообщение в чат.
    - hist: Выводит историю сообщений из чата.
    - search: Отправляет запрос к модели для поиска в теории по заданной теме.
>>> from danya import ask, get, send, hist, search
"""


from .login import login
login()
from .main import ask, get
from .chat import send, hist
from .search import search
