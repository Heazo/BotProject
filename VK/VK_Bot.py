from TimetableProvider.TimetableCreator import get_unique_rasp
from TimetableProvider.DB_Manager import DB_Manager
from vkbottle import Bot, Keyboard, Text


class VKbot_class:
    def __init__(self, m_token: str, db_manager: DB_Manager):
        self.bot = Bot(token=m_token)
        self.api = self.bot.api
        self.db = db_manager
        print("Initializing VK Bot\n")
        self._register_handlers()

    async def sender(self, user_id: int, msg: str) -> None:
        await self.api.messages.send(user_id=user_id, message=msg, random_id=0)

    async def send_rasp(self, user_id: int) -> None:
        msg = get_unique_rasp(self.db)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        elif msg is None:
            msg = "Расписание на сегодня не найдено."
        else:
            msg = str(msg)

        await self.sender(user_id, msg)
        print(f"send_rasp...{msg}")

    def get_keyboard(self):
        keyboard = Keyboard(one_time=False, inline=False)
        keyboard.add(Text("Начать"))
        return keyboard

    def _register_handlers(self) -> None:
        db = self.db
        @self.bot.on.private_message(text=["начать", "Начать"])
        async def start_russian(message):
            kb = self.get_keyboard()
            await message.answer("Привет!", keyboard=kb)

        @self.bot.on.private_message(text="/поиск <group_num>")
        async def search_handler(message, group_num: str):
            user_id = str(message.from_id)
            result = db.insertUserAndGroup(user_id, group_num)
            if result:
                await message.answer(f"Группа {group_num} успешно привязана!")
            else:
                await message.answer("Ошибка")

        @self.bot.on.private_message(text="1")
        async def start_command(message):
            await message.answer("Абиба Абоба")

        @self.bot.on.private_message(text=["/поиск", "/Поиск"])
        async def start_command(message):
            await message.answer("/start")

        @self.bot.on.private_message(text="/start")
        async def start_command(message):
            await message.answer("/start")

        @self.bot.on.private_message(text="/help")
        async def help_command(message):
            await message.answer("/help")

        @self.bot.on.private_message(text="/about")
        async def about_command(message):
            await message.answer("/about")

        @self.bot.on.private_message(text="/contact")
        async def contact_command(message):
            await message.answer("/contact")

        @self.bot.on.private_message(text="/today")
        async def today_command(message):
            await self.send_rasp(message.from_id)

    def event_handler(self) -> None:
        self.bot.run_forever()
