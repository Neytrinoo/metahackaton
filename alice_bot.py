from flask import Flask, request
import logging

import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}


def user_in_system(id):
    return False


def log_in_1(login):
    return True


def log_in_2(password):
    return True


def get_list(id):
    return ''


def add(name, info, category, date, keywords):
    return True


def get_last_list(id):
    return True


def delegation(id, fio):
    return True


def start_timer(id):
    return True


def finish_timer(id):
    return True


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    flag = False
    for user in sessionStorage:
        if (user['id'] == user_id) and user['password']:
            flag = True

    if req['session']['new']:
        if not flag:
            sessionStorage[user_id] = {
                'suggests': [],
                'login': None,
                'password': None,
                'fio': None,
                'id': None,
                'token': None
            }
            res['response']['text'] = 'Привет! Введи свой логин'

            res['response']['buttons'] = get_suggests(user_id)
            return
        else:
            'Здравствуйте!'


    if not sessionStorage[user_id]['login']:
        result = log_in_1(req['request']['original_utterance'])
        if result:
            res['response']['text'] = 'Теперь пароль'
            sessionStorage[user_id]['login'] = req['request']['original_utterance']
        else:
            res['response']['text'] = 'Пользователь не найден'
    elif not sessionStorage[user_id]['password']:
        result = log_in_2(req['request']['original_utterance'])
        if result:
            res['response']['text'] = 'Добро пожаловать'
            sessionStorage[user_id]['password'] = req['request']['original_utterance']
        else:
            res['response']['text'] = 'Пароль неверный'

    elif req['request']['original_utterance'].lower() == 'покажи мои задачи':
        worklist = get_list(user_id)
        res['response']['text'] = worklist
        return
    elif req['request']['original_utterance'].lower() == 'просмотреть список просроченных задач':
        worklist = get_last_list(user_id)
        res['response']['text'] = worklist
        return




def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
