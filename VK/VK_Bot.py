from TimetableProvider.TimetableCreator import get_unique_rasp
from vkbottle import Bot


class VKbot_class:
    def __init__(self, m_token: str):
        self.bot = Bot(token=m_token)
        self.api = self.bot.api
        self._register_handlers()
        print("Initializing VK Bot\n")

    async def sender(self, user_id: int, msg: str) -> None:
        await self.api.messages.send(user_id=user_id, message=msg, random_id=0)

    async def send_rasp(self, user_id: int) -> None:
        msg = get_unique_rasp()
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        elif msg is None:
            msg = "Расписание на сегодня не найдено."
        else:
            msg = str(msg)

        await self.sender(user_id, msg)
        print(f"send_rasp...{msg}")

    def _register_handlers(self) -> None:
        @self.bot.on.private_message(text=["начать", "Начать"])
        async def start_russian(message):
            await message.answer("Абиба абоба")

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
