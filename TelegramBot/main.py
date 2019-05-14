import datetime
import json
from telegram.ext import Updater, MessageHandler, Filters
import keys
import apiai
import requests

from flask import Flask


class Task:

    def __init__(self):
        self.name = None
        self.description = None
        self.category = None
        self.date_time = None

    def get_json(self):
        return json.dumps({"name": self.name,
                           "description": self.description,
                           "category": self.category,
                           "date_time": self.date_time})


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
            # TODO code post request
            requests.post("https://api.com/", data={"task": task})
        else:
            updater.message.reply_text(resp)


def recieved_command(updater, bot):
    if updater.message.text == "/start":
        updater.message.reply_text("Здравствуйте! Авторизуйтесь с помощью команды /auth <Логин> <Пароль>")
        session_storage[updater.message.from_user.id] = {
            "api_key": None,
            "last_operation": -1,
            "tmp_task": None
        }
    elif updater.message.text.startswith("/auth"):
        _, login, password = updater.message.text.split()
        # TODO Auth to rest with login and password. Get token to do smth.
        success = True
        if success:
            session_storage[updater.message.from_user.id]["api_key"] = "api"
            session_storage[updater.message.from_user.id]["last_operation"] = 0
    elif updater.message.text == "/task":
        pass
        # TODO Get task list from rest
    elif updater.message.text == "/expired_task":
        pass
        # TODO Get expired tasks list from rest
    elif updater.message.text == "/add_task":
        updater.message.reply_text("Добавим задачу в систему. Введите название задачи.")
        session_storage[updater.message.from_user.id]["last_operation"] = 1
        session_storage[updater.message.from_user.id]["tmp_task"] = Task()
    elif updater.message.text.startswith("/delegate_task"):
        _, task_id, user_id = updater.message.text.split()
        # TODO Task delegation by task_id to user with user_id


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
