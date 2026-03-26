#Будет создавать индивидуальное росписание, обращаясь к DB_Manager

from datetime import datetime
from DB_Manager import getRaspFromDB



def create_unique_rasp():
    date = datetime.now().strftime("%d.%m.%Y")
    db_rasp = getRaspFromDB(date)
    if db_rasp is None:
        #Обращаемся к парсеру, если после парса все равно None - выводим ошибку



def get_unique_rasp() -> list[str]:
    create_unique_rasp()
    return 1


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