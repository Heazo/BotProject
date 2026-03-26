#Будет создавать индивидуальное росписание, обращаясь к DB_Manager

from datetime import datetime
from .DB_Manager import getRaspFromDB



def create_unique_rasp():
    date = datetime.now().strftime("%d.%m.%Y")
    db_rasp = getRaspFromDB(date)
    if db_rasp is None:
        print("No Rasp Err\n")
        #Сделать функции парсера
        #Обращаемся к парсеру, если после парса все равно None - выводим ошибку
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