from VK.VK_Bot import VKbot_class
from tokens import vk_token
from TimetableProvider.rusnarfu_API import requestNarfu


def main():
    #vkbot = VKbot_class(vk_token)
    #vkbot.event_handler()
    week_list = requestNarfu()
    for week in week_list:
        for day in week.days:
            print(day.day_date)
            for session_list in day.sessions:
                for session in session_list:
                    print("Номер пары: ",session.num_session)
                    print("Номер пары: ", session.discipline)
                    print("")



if __name__ == '__main__':
    main()

