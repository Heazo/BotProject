from VK.VK_Bot import VKbot_class
#from tokens import vk_token
from TimetableProvider.rusnarfu_API import requestNarfu


def main():
    #vkbot = VKbot_class(vk_token)
    #vkbot.event_handler()
    sessions = requestNarfu()
    print("Количество пар всего: ",len(sessions))
    for session in sessions:
        print("Дата: ", session.date)
        print("Номер пары: " ,session.num_session)
        print("Предмет: ", session.discipline)




if __name__ == '__main__':
    main()

