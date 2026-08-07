from TG.TG_Bot import TelegramBotClass
from VK.VK_Bot import VKbot_class
#from VK.VK_Bot2 import VKbot_class
from tokens import vk_token, tg_token, password
from TimetableProvider.parser_narfu import ParserNARFU
from TimetableProvider.DB_Manager import DB_Manager
from datetime import datetime


def main():
    db_manager = DB_Manager(
        host="localhost",
        port=5432,
        dbname="studies_db",
        user="postgres",
        password=password
    )
    
    #13372281337        VvSilv25042026sql
    
    #parser = ParserNARFU()

    vkbot = VKbot_class(vk_token, db_manager)
    vkbot.event_handler()

    # tgbot = TelegramBotClass(tg_token, db_manager)
    # tgbot.run()

    #Сделать проверку на то что ничего не нашлось, и тогда напишем об этом пользователю
    #disp = "Имструменты анализа данных"
    #res = db_manager.find_best_discipline(disp)
    #db_manager.addUserDiscipline("931321821", res['id'])
    #disciplines = db_manager.getUserDisciplines("931321821")
    #print(disciplines[0]["name"])
    #print(disciplines[1]["name"])

if __name__ == '__main__':
   main()


