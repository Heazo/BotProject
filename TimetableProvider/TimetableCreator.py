#Будет создавать индивидуальное расписание, обращаясь к DB_Manager

#TODO: Навести порядок необходимо тут, а то тут какой то ужас и кринж

from datetime import datetime, timedelta
from TimetableProvider.DB_Manager import DB_Manager
from config import Mess_Config, EmojisSetEnum

async def delet_unnecessary_sess(session: dict, ch_discipls: list[str]) -> bool:
    for ch_discipl in ch_discipls:
        if ch_discipl in session['discipline']:
            print("лишний предмет по выбору попался")
            return True
    return False

async def create_unique_rasp(db_manager: DB_Manager, day_offset=0, group_num=None, emojis_set: EmojisSetEnum = EmojisSetEnum.DEFAULT, user_id: str = "931321821") -> list[str]:

    #TODO: Возможно будет логичнее передавать словарь смайликов в аргументах метода
    if emojis_set == EmojisSetEnum.DEFAULT:
        emoji_set = Mess_Config.default_emojis
    elif emojis_set == EmojisSetEnum.NEW_YEAR:
        emoji_set = Mess_Config.new_year_emojis
    
    
    #my_date = datetime.now()
    my_date = datetime(2026, 6, 8, 17, 30)
    # date = my_date.strftime("%d.%m.%Y")
    target_date = my_date + timedelta(days=day_offset)
    date_str = target_date.strftime("%d.%m.%Y")
    
    #Сначала проверим дату последнего обновления расписания в базе данных, если обновлений давно небыло, парсим заново
    #Не удалять! Раскомментировать когда появится росписание на сайте!
    # parser = ParserNARFU()
    # last_update = db_manager.getLastUpdateForGroup(group_num)
    # if last_update is None:
    #     sessions = parser.get_all_rasp(db_manager.getURLForGroup(group_num))
    #     db_manager.insertSessions(sessions)     ##А если parser.get_all_rasp() выдаст None???   #Сделать отправку отчёта если None
    # elif my_date - last_update >= timedelta(hours=6):
    #     sessions = parser.get_all_rasp(db_manager.getURLForGroup(group_num))
    #     if sessions is not None:
    #         db_manager.replaceSessionsForGroup(group_num, sessions)
    # else:
    #     sessions = db_manager.getSessionsFromDB(date_str, group_num=group_num)
    sessions = await db_manager.getSessionsFromDB(date_str, group_num=group_num)
    
    unsell_dists = None
    if sessions != None:
        unsell_dists = await db_manager.getUnselectedDisc(user_id)


    # Добавляем заголовок с датой
    day_names = {
        0: "сегодня",
        1: "завтра",
    }
    day_name = day_names.get(day_offset, target_date.strftime("%d.%m.%Y"))

    if sessions is None:
        return [f"⚠️ Произошла ошибка при получении расписания на {day_name} ({date_str}).\nПожалуйста, попробуйте позже."]
    else:
        if len(sessions) == 0:
            return [f"{emoji_set.get('calendar')} На {day_name} ({date_str}) занятий нет 🎉"]
        else:
            rasp = []

            for session in sessions:
                num_type = Mess_Config.num_emojis.get(session['num_session'], "▫️")
                
                if unsell_dists is not None:
                    unnecessary = await delet_unnecessary_sess(session=session, ch_discipls=unsell_dists)

                if unnecessary == True:
                    continue
                
                formatted_session = (
                    f"{num_type}  {session['time_session']}  [{session['kind_of_work']}]\n"
                    f"{emoji_set.get('discipline')} {session['discipline']}\n"
                    f"{emoji_set.get('auditorium')} {session['auditorium']}\n\n"
                )
                rasp.append(formatted_session)

            header = f"{emoji_set.get('calendar')} Расписание на {day_name} ({date_str}):\n\n"
            return [header + "\n".join(rasp)]
    #
    #!db_rasp = None
    #db_rasp = getRaspFromDB()

    # if db_rasp is None:
    #     db_rasp = ""
    #     #Сделать функции парсера
    #     #Обращаемся к парсеру, если после парса все равно None - выводим ошибку
    #     parser = ParserNARFU()
    #     sessions = parser.get_all_rasp("https://ruz.narfu.ru/?timetable&group=19439")
    #     i = 0
    #     for session in sessions:
    #         i = i + 1
    #         db_rasp = db_rasp + str(session.date) + " " + str(session.num_session) + " " + str(session.discipline) + "\n"
    #         if i == 10:
    #             break
    #!return db_rasp

async def get_rasp_for_day(db_manager: DB_Manager, day_offset, group_num, user_id: str = "931321821", emojis_set: EmojisSetEnum = EmojisSetEnum.DEFAULT) -> list[str]:
    return await create_unique_rasp(db_manager, day_offset, group_num, emojis_set, user_id)

async def get_rasp_for_date(db_manager: DB_Manager, date: datetime, group_num: str = None, emojis_set: EmojisSetEnum = EmojisSetEnum.DEFAULT, user_id: str = "931321821") -> list[str]:
    """
    Получить расписание на конкретную дату.

    Args:
        db_manager: менеджер базы данных
        date: объект datetime с нужной датой
        group_num: номер группы
        emojis_set: набор эмоджи для форматирования
        user_id: ID пользователя

    Returns:
        list[str]: расписание в виде списка строк
    """
    if emojis_set == EmojisSetEnum.DEFAULT:
        emoji_set = Mess_Config.default_emojis
    elif emojis_set == EmojisSetEnum.NEW_YEAR:
        emoji_set = Mess_Config.new_year_emojis
    
    
    date_str = date.strftime("%d.%m.%Y")
    sessions = await db_manager.getSessionsFromDB(date_str, group_num=group_num)
    
    unsell_dists = None
    if sessions != None:
        unsell_dists = await db_manager.getUnselectedDisc(user_id)

    # Название дня недели
    weekdays_ru = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }
    day_name = weekdays_ru.get(date.weekday(), "Неизвестный день")

    if sessions is None:
        return [
            f"⚠️ Произошла ошибка при получении расписания на {day_name} ({date_str}).\nПожалуйста, попробуйте позже."]
    else:
        if len(sessions) == 0:
            return [f"{emoji_set.get('calendar')} На {day_name} ({date_str}) занятий нет 🎉"]
        else:
            rasp = []

            for session in sessions:
                num_type = Mess_Config.num_emojis.get(session['num_session'], "▫️")

                if unsell_dists is not None:
                    unnecessary = await delet_unnecessary_sess(session=session, ch_discipls=unsell_dists)
                    if unnecessary:
                        continue

                formatted_session = (
                    f"{num_type}  {session['time_session']}  [{session['kind_of_work']}]\n"
                    f"{emoji_set.get('discipline')} {session['discipline']}\n"
                    f"{emoji_set.get('auditorium')} {session['auditorium']}\n\n"
                )
                rasp.append(formatted_session)

            header = f"{emoji_set.get('calendar')} Расписание на {day_name} ({date_str}):\n\n"
            return [header + "\n".join(rasp)]
        
