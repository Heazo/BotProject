#основное место бота с определениями команд, кнопками и так далее

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from TimetableProvider.TimetableCreator import get_unique_rasp

def sender(id, msg):
    vk_session.method('messages.sendMessage', {"user_id" : id, "message" : msg, "random_id" : 0})

def send_rasp(id, msg):
    get_unique_rasp()
    sender(id, msg)


def vk_api_init():
    vk_session = vk_api.VkApi(token='')
    session = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id

            if msg == "/start":
                sender(id, msg)
            if msg == "/help":
                sender(id, msg)
            if msg == "/about":
                sender(id, msg)
            if msg == "/contact":
                sender(id, msg)
            if msg == "/today":
                send_rasp(id, msg)

