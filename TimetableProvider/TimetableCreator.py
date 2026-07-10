#Будет создавать индивидуальное росписание, обращаясь к DB_Manager

from datetime import datetime
from html import parser

from TimetableProvider.parser_narfu import ParserNARFU
from TimetableProvider.DB_Manager import DB_Manager



def create_unique_rasp(db_manager: DB_Manager) -> list[str]:
    # date = datetime.now().strftime("%d.%m.%Y")
    my_date = datetime(2026, 4, 21)
    date = my_date.strftime("%d.%m.%Y")
    sessions = db_manager.getSessionsFromDB(date)
    if sessions is not None:
        rasp = []
        num_emojis = {
            "1": "1️⃣",
            "2": "2️⃣",
            "3": "3️⃣",
            "4": "4️⃣",
            "5": "5️⃣",
            "6": "6️⃣",
            "7": "7️⃣"
        }

        for session in sessions:
            num_type = num_emojis.get(session['num_session'], "▫️")

            formatted_session = (
                f"{num_type}  {session['time_session']}  [{session['kind_of_work']}]\n"
                f"   📖 {session['discipline']}\n"
                f"   🏫 {session['auditorium']}\n\n"
            )
            rasp.append(formatted_session)
        return rasp
    else:
        return ["Расписание на сегодня не найдено."]
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


def get_unique_rasp(db_manager: DB_Manager) -> list[str]:
    return create_unique_rasp(db_manager)


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