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

    # vkbot = VKbot_class(vk_token, db_manager)
    # vkbot.event_handler()

    tgbot = TelegramBotClass(tg_token, db_manager)
    tgbot.run()



if __name__ == '__main__':
   main()


