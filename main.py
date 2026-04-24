from VK.VK_Bot import VKbot_class
#from VK.VK_Bot2 import VKbot_class
from tokens import vk_token
from TimetableProvider.parser_narfu import ParserNARFU
from TimetableProvider.DB_Manager import DB_Manager



def main():
    db_manager = DB_Manager(
        host="localhost",
        port=5432,
        dbname="studies_db",
        user="postgres",
        password="13372281337"
    )
    parser = ParserNARFU()

    
    #groups = parser.find_groups()
    #db_manager.insertGroups(groups)

    #sessions = parser.get_all_rasp("https://ruz.narfu.ru/?timetable&group=19439")
    #db_manager.insertSessions(sessions)

    # groups2 = db_manager.getGroupsFromDB()
    # for group in groups2:
    #     print(f"{group.speciality} ({group.group_num}): {group.url}")

#    sessions = db_manager.insertSessions()   #для тестов - удалить!
#    for session in sessions:
#         print(session)

    #vkbot = VKbot_class(vk_token)
    #vkbot.event_handler()

    # parser = ParserNARFU()
    # sessions = parser.get_all_rasp("https://ruz.narfu.ru/?timetable&group=19439")
    # print("Количество пар всего: ",len(sessions))
    # for session in sessions:
    #     print("Дата: ", session.date)
    #     print("Номер пары: " ,session.num_session)
    #     print("Подгруппа (поток): ", session.group_thread)
    #     print("Номер группы: ", session.group_num)
    #     print("Предмет: ", session.discipline)
    #groups = parser.find_groups()
    #for group in groups:
    #    print(f"{group.speciality} ({group.group_num}): {group.url}")



if __name__ == '__main__':
   main()
