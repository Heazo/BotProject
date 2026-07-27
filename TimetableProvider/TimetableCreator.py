#Будет создавать индивидуальное расписание, обращаясь к DB_Manager

from datetime import datetime, timedelta
from html import parser

from TimetableProvider.parser_narfu import ParserNARFU
from TimetableProvider.DB_Manager import DB_Manager



def create_unique_rasp(db_manager: DB_Manager, day_offset=0) -> list[str]:

    # datetime.now()
    my_date = datetime(2026, 4, 21)
    # date = my_date.strftime("%d.%m.%Y")
    target_date = my_date + timedelta(days=day_offset)
    date_str = target_date.strftime("%d.%m.%Y")
    sessions = db_manager.getSessionsFromDB(date_str)

    # Добавляем заголовок с датой
    day_names = {
        0: "сегодня",
        1: "завтра",
        -1: "вчера"
    }
    day_name = day_names.get(day_offset, target_date.strftime("%d.%m.%Y"))

    # print(sessions)
    if sessions is None:
        return [f"⚠️ Произошла ошибка при получении расписания на {day_name} ({date_str}).\nПожалуйста, попробуйте позже."]
    else:
        if len(sessions) == 0:
            return [f"📅 На {day_name} ({date_str}) занятий нет 🎉"]
        else:
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

            header = f"📅 Расписание на {day_name} ({date_str}):\n\n"
            return [header + "\n".join(rasp)]
    #
    #!db_rasp = None
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
    #!return db_rasp

def get_rasp_for_day(db_manager: DB_Manager, day_offset) -> list[str]:
    return create_unique_rasp(db_manager, day_offset)

def get_rasp_for_weekday(db_manager: DB_Manager, weekday: int) -> list[str]:
    """
    Получить расписание на указанный день недели текущей недели.

    Args:
        db_manager: менеджер базы данных
        weekday: день недели (0 - понедельник, 1 - вторник, ..., 6 - воскресенье)

    Returns:
        list[str]: расписание в виде списка строк
    """
    # Получаем текущую дату
    # now = datetime.now()

    my_date = datetime(2026, 4, 21)

    # Вычисляем день недели текущей даты (0 - понедельник, 6 - воскресенье)
    current_weekday = my_date.weekday()

    # Вычисляем смещение до нужного дня недели
    # Если нужный день уже прошел на этой неделе, берем следующую неделю
    if weekday < current_weekday:
        # Нужный день был на этой неделе, берем следующий такой день
        days_until = 7 - (current_weekday - weekday)
    else:
        # Нужный день еще будет на этой неделе
        days_until = weekday - current_weekday

    # Получаем дату нужного дня
    target_date = my_date + timedelta(days=days_until)
    date_str = target_date.strftime("%d.%m.%Y")

    # Получаем расписание из БД
    sessions = db_manager.getSessionsFromDB(date_str)

    # Названия дней недели на русском
    weekdays = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }

    day_name = weekdays.get(weekday, "Неизвестный день")

    if sessions is None:
        return [
            f"⚠️ Произошла ошибка при получении расписания на {day_name} ({date_str}).\nПожалуйста, попробуйте позже."]
    else:
        if len(sessions) == 0:
            return [f"📅 На {day_name} ({date_str}) занятий нет 🎉"]
        else:
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

            header = f"📅 Расписание на {day_name} ({date_str}):\n\n"
            return [header + "\n".join(rasp)]