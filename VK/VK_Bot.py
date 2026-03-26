#основное место бота с определениями команд, меню и так далее

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from TimetableProvider.TimetableCreator import get_unique_rasp

class VKbot_class:
    def __init__(self, m_token):
        self.vk_session = vk_api.VkApi(token=m_token)
        self.session = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        print("Initializing VK Bot\n")


    def sender(self, id, msg):
        self.vk_session.method('messages.send', {"user_id" : id, "message" : msg, "random_id" : 0})

    def send_rasp(self, id):
        msg = get_unique_rasp()
        self.sender(id, msg)
        print(f"send_rasp...{msg}")

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    if msg == "начать":
                        self.sender(id, "Абиба абоба")
                    if msg == "/start":
                        self.sender(id, msg)
                    if msg == "/help":
                        self.sender(id, msg)
                    if msg == "/about":
                        self.sender(id, msg)
                    if msg == "/contact":
                        self.sender(id, msg)
                    if msg == "/today":
                        self.send_rasp(id)
