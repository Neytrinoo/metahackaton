from flask import Flask, request
import logging
import requests
import json
import apiai

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessionStorage = {}
aiapi_key = 'b03844e61b61486badaf0a4f6f25022e'
apia = apiai.ApiAI(aiapi_key)


def get_response(text, session_id):
    request = apia.text_request()
    request.lang = "ru"
    request.session_id = session_id
    request.query = text
    response = json.loads(request.getresponse().read().decode('utf-8'))
    try:
        return response['result']['fulfillment']['speech']
    except Exception:
        return "Произошла ошибка, попробуйте позже."


def isDate(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return True
    except Exception:
        return False


def user_in_system(id):
    return False

def log_in(login, password):
    url = "http://neytrinoo.pythonanywhere.com/api/auth"
    print(login, password)
    params = {
        'username': login,
        'password': password
    }

    response = requests.post(url, params=params)
    code = int(response.status_code)
    if code == 200 or code == 500:
        token = response.json()['token']
        return code, token
    return code, False


def get_list(token):
    url = "http://neytrinoo.pythonanywhere.com/api/task"

    params = {
        'token': token
    }

    response = requests.get(url, params)
    worklist = response.json()['tasks']
    worklist = str(worklist)
    return worklist


def get_task(id, token):
    url = 'http://neytrinoo.pythonanywhere.com/api/task' + '/' + str(id)

    params = {
        'token': token
    }

    response = requests.get(url, params)
    task = response.json()['task']
    task = str(task)
    return task


def add(name, info, category, datetime, token):
    url = "http://neytrinoo.pythonanywhere.com/api/task/"

    params = {
        'token': token,
        'name': name,
        'info': info,
        'category': category,
        'datetime': datetime
    }
    requests.post(url, params)


def get_last_list(id):
    url = "http://neytrinoo.pythonanywhere.com/api/task"

    params = {
        'token': token
    }

    response = requests.get(url, params)
    worklist = response.json()['tasks']
    worklist = str(worklist)
    return worklist


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
    print(response)

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    flag = False
    for user in list(sessionStorage.values()):
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
                'token': None,
                'adding_task': False,
                'task_name': None,
                'task_info': None,
                'task_category': None
            }
            res['response']['text'] = 'Привет! Введи свой логин и пароль'
            return
        else:
            res['response']['text'] = 'Здравствуйте!'
        sessionStorage[user_id]['suggests'] = [{
            'title': 'покажи просроченные задачи',
            'hide': True
        },
            {
                'title': 'покажи мои задачи',
                'hide': True
            },
            {
                'title': 'покажи добавить задачу',
                'hide': True
            }
        ]

    if not sessionStorage[user_id]['login']:
        try:
            if len(req['request']['command'].split()) < 2:
                res['response']['text'] = 'Нужно так: <логин> <пароль>'
            else:
                login, password = req['request']['command'].split()
                result, token = log_in(login, password)
                print('q ' + str(result))
                if result == 404:
                    print('404')
                    res['response']['text'] = 'Пользователь не найден'
                elif result == 403:
                    print('403')
                    res['response']['text'] = 'Неверный пароль'
                else:
                    print(result)
                    res['response']['text'] = 'Отлично'
                    sessionStorage[user_id]['login'] = login
                    sessionStorage[user_id]['password'] = password
                    sessionStorage[user_id]['token'] = token
                    sessionStorage[user_id]['suggests'] = [{
                        'title': 'покажи просроченные задачи',
                        'hide': True
                    },
                        {
                            'title': 'покажи мои задачи',
                            'hide': True
                        },
                        {
                            'title': 'покажи добавить задачу',
                            'hide': True
                        }
                    ]
        except Exception as a:
            print(result)
            res['response']['text'] = 'Отлично'
            sessionStorage[user_id]['login'] = login
            sessionStorage[user_id]['password'] = password
            sessionStorage[user_id]['token'] = token
            sessionStorage[user_id]['suggests'] = [{
                'title': 'покажи просроченные задачи',
                'hide': True
            },
                {
                    'title': 'покажи мои задачи',
                    'hide': True
                },
                {
                    'title': 'покажи добавить задачу',
                    'hide': True
                }
            ]

    elif not sessionStorage[user_id]['adding_task']:
        if not sessionStorage[user_id]['task_name']:
            res['response']['text'] = 'Введи описание задачи'
            sessionStorage[user_id]['task_name'] = req['request']['original_utterance']
        elif not sessionStorage[user_id]['task_info']:
            res['response']['text'] = 'Выбери категорию задачи'
            sessionStorage[user_id]['suggests'] = [{
                'title': 'срочно',
                'hide': True
            },
                {
                    'title': 'можно подождать',
                    'hide': True
                },
                {
                    'title': 'долгосрочная',
                    'hide': True
                }
            ]
            sessionStorage[user_id]['task_info'] = req['request']['original_utterance']
        elif not sessionStorage[user_id]['task_category']:
            res['response']['text'] = 'Скажи дату и время завершения задачи'
            sessionStorage[user_id]['task_category'] = req['request']['original_utterance']
            sessionStorage[user_id]['suggests'] = [{
                'title': 'покажи просроченные задачи',
                'hide': True
            },
                {
                    'title': 'покажи мои задачи',
                    'hide': True
                },
                {
                    'title': 'покажи добавить задачу',
                    'hide': True
                }
            ]
        else:
            datetime = get_response(req['request']['original_utterance'], user_id)
            if not isDate(datetime):
                res['response']['text'] = 'Cкажи дату и время'
            else:
                name = sessionStorage[user_id]['task_name']
                info = sessionStorage[user_id]['task_info']
                category = sessionStorage[user_id]['task_category']
                token = sessionStorage[user_id]['token']
                add(name, info, category, datetime, token)
                sessionStorage[user_id]['adding_task'] = False

    elif req['request']['original_utterance'].lower() == 'покажи мои задачи':
        worklist = get_list(sessionStorage[user_id]['token'])
        res['response']['text'] = worklist
        return
    elif 'покажи задачу номер' in req['request']['original_utterance'].lower():
        num = ''
        for letter in list(req['request']['original_utterance'].lower()):
            if letter.isdigit():
                num = num + letter
        num = int(num)
        task = get_task(num, sessionStorage[user_id]['token'])
        res['response']['text'] = task
    elif req['request']['original_utterance'].lower() == 'просмотреть список просроченных задач':
        worklist = get_last_list(sessionStorage[user_id]['token'])
        res['response']['text'] = worklist
        return
    elif req['request']['original_utterance'].lower() == 'добавить задачу':
        sessionStorage[user_id]['adding_task'] = True
        res['response']['text'] = 'Введи название задачи'
    res['response']['buttons'] = sessionStorage[user_id]['suggests']


if __name__ == '__main__':
    app.run(port=443)
