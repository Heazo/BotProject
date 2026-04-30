#Будет создавать индивидуальное росписание, обращаясь к DB_Manager

from datetime import datetime
from html import parser

from TimetableProvider.parser_narfu import ParserNARFU
#from .DB_Manager import getRaspFromDB



def create_unique_rasp():
    date = datetime.now().strftime("%d.%m.%Y")
    #
    db_rasp = None
    #db_rasp = getRaspFromDB()

    # if db_rasp is None:
    #     print("No Rasp Err\n")
    #     db_rasp = ""
    #     #Сделать функции парсера
    #     #Обращаемся к парсеру, если после парса все равно None - выводим ошибку
    #     parser = ParserNARFU()
    #     sessions = parser.get_all_rasp("https://ruz.narfu.ru/?timetable&group=19439")
    #     print("Количество пар всего: ",len(sessions))
    #     i = 0
    #     for session in sessions:
    #         i = i + 1
    #         db_rasp = db_rasp + str(session.date) + " " + str(session.num_session) + " " + str(session.discipline) + "\n"
    #         print("Дата: ", session.date)
    #         print("Номер пары: " ,session.num_session)
    #         print("Предмет: ", session.discipline)
    #         if i == 10:
    #             break
    return db_rasp


def get_unique_rasp() -> list[str]:
    return create_unique_rasp()


    # Для запросов по дням недели
    # Monday
    # Tuesday
    # Wednesday
    # Thursday
    # Friday
    # Saturday
    # Sunday
    # понедельник
    # вторник
    # среда
    # четверг
    # пятница
    # суббота
    # воскресенье