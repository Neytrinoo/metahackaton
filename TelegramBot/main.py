import datetime
import json
from telegram.ext import Updater, MessageHandler, Filters
import keys
import apiai
import requests

from flask import Flask

url = "https://kindcode.com"


class Task:

    def __init__(self, id):
        self.name = None
        self.description = None
        self.category = None
        self.date_time = None

    def get_json(self):
        return json.dumps({"name": self.name,
                           "description": self.description,
                           "category": self.category,
                           "date_execution": self.date_time,
                           })


session_storage = {}


def isDate(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return True
    except Exception:
        return False


app = apiai.ApiAI(keys.apiai)


def get_response(text, session_id):
    request = app.text_request()
    request.lang = "ru"
    request.session_id = session_id
    request.query = text
    response = json.loads(request.getresponse().read().decode('utf-8'))
    try:
        return response['result']['fulfillment']['speech']
    except Exception:
        return "Произошла ошибка, попробуйте позднее."


def recieved_message(updater, bot):
    user_id = updater.message.from_user.id
    if session_storage[user_id]["last_operation"] == 1:
        session_storage[user_id]["tmp_task"].name = updater.message.text
        updater.message.reply_text("Введите описание задачи.")
        session_storage[user_id] = 2
    elif session_storage[user_id]["last_operation"] == 2:
        session_storage[user_id]["tmp_task"].description = updater.message.text
        session_storage[user_id]["last_operation"] = 3
        updater.message.reply_text("Введите категорию задачи.")
    elif session_storage[user_id]["last_operation"] == 3:
        if updater.message.text.lower() != "нет":
            session_storage[user_id]["tmp_task"].category = updater.message.text
        session_storage[user_id]["last_operation"] = 4
        updater.message.reply_text("Введите срок сдачи")
    elif session_storage[user_id]["last_operation"] == 4:
        resp = get_response(updater.message.text, user_id)
        if isDate(resp):
            session_storage[user_id]["tmp_task"] = resp
            task = session_storage[user_id]["tmp_task"].get_json()
            data = requests.post(f"{url}/api/task/", data={"name": task})
            if data.status_code == 200:
                updater.message.reply_text("Добавлено")
            else:
                updater.message.reply_text("Неверные данные!")
        else:
            updater.message.reply_text(resp)


def recieved_command(updater, bot):
    user_id = updater.message.from_user.id
    if updater.message.text == "/start":
        updater.message.reply_text("Здравствуйте! Авторизуйтесь с помощью команды /auth <Логин> <Пароль>")
        session_storage[updater.message.from_user.id] = {
            "api_key": None,
            "last_operation": -1,
            "tmp_task": None,
            "id": None
        }
    elif updater.message.text.startswith("/auth"):
        _, login, password = updater.message.text.split()
        resp = requests.post(f"{url}/api/auth", data={"username": login,
                                                      "password": password})
        if resp.status_code == 200:
            session_storage[updater.message.from_user.id]["api_key"] = resp.content
            session_storage[updater.message.from_user.id]["last_operation"] = 0
            updater.message.reply_text("Успешная авторизация!")
        else:
            updater.message.reply_text("Неверные данные для входа!")
    elif updater.message.text == "/task" and session_storage[user_id]["api_key"]:
        resp = requests.get(f"{url}/api/tasks", data={"token": session_storage[user_id]["api_key"]}).json()
        for task in resp:
            updater.reply_text(f"ID:{task['id']}\nНазвание:{task['name']}\nОписание:{task['description']}"
                               f"\nДата сдачи:{task['execution_phase']})")
    elif updater.message.text == "/expired_task" and session_storage[user_id]["api_key"]:
        resp = requests.get(f"{url}/api/tasks", data={"token": session_storage[user_id]["api_key"]}).json()
        for task in resp:
            if task['date_execution'] <= datetime.datetime.now():
                updater.reply_text(f"ID:{task['id']}\nНазвание:{task['name']}\nОписание:{task['description']}"
                                   f"\nДата сдачи:{task['execution_phase']})")
    elif updater.message.text == "/add_task" and session_storage[user_id]["api_key"]:
        updater.message.reply_text("Добавим задачу в систему. Введите название задачи.")
        session_storage[updater.message.from_user.id]["last_operation"] = 1
        session_storage[updater.message.from_user.id]["tmp_task"] = Task()
    elif updater.message.text.startswith("/delegate_task") and session_storage[user_id]["api_key"]:
        _, task_id, user_id = updater.message.text.split()
        resp = requests.put(f"{url}/api/task/{task_id}", data={"performer_id": user_id})
        if resp.status_code == 200:
            updater.message.reply_text("Изменено")
        elif resp.status_code == 404:
            updater.message.reply_text("Такой задачи не существует")
        else:
            updater.message.reply_text("Произошла ошибка!")


def main():
    updater = Updater(keys.telegram)
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, recieved_message)
    command_handler = MessageHandler(Filters.command, recieved_command)
    dp.add_handler(text_handler)
    dp.add_handler(command_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()