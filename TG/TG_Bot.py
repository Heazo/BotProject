from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from TimetableProvider.TimetableCreator import get_rasp_for_day
from TimetableProvider.DB_Manager import DB_Manager


class TelegramBotClass:
    def __init__(self, token: str, db_manager: DB_Manager):
        self.bot = Bot(token=token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.db = db_manager
        print("Initializing Telegram Bot\n")
        self._register_handlers()

    async def set_commands(self) -> None:
        """Установка команд в меню бота"""
        commands = [
            BotCommand(command="search", description="Привязать группу (пример: /search 1234)"),
            BotCommand(command="today", description="Расписание на сегодня"),
            BotCommand(command="tomorrow", description="Расписание на завтра"),
            BotCommand(command="week", description="Расписание на неделю")
        ]
        await self.bot.set_my_commands(commands)
        print("Commands set successfully!")

    async def sender(self, user_id: int, msg: str) -> None:
        """Отправка сообщения пользователю"""
        await self.bot.send_message(chat_id=user_id, text=msg)

    async def send_rasp_today(self, user_id: int) -> None:
        """Отправка расписания на сегодня"""
        msg = get_rasp_for_day(self.db, day_offset=0)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_today...{msg}")

    async def send_rasp_tomorrow(self, user_id: int) -> None:
        """Отправка расписания на завтра"""
        msg = get_rasp_for_day(self.db, day_offset=1)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_tomorrow...{msg}")

    def _register_handlers(self) -> None:
        """Регистрация всех обработчиков"""
        db = self.db

        # Обработчик команды /start
        @self.dp.message(Command("start"))
        async def start_command(message: types.Message):
            await message.answer("Привет!")

        # Обработчик команды /search с параметром
        @self.dp.message(Command("search"))
        async def search_handler(message: types.Message, command: CommandObject):
            group_num = command.args
            user_id = str(message.from_user.id)

            if not group_num:
                await message.answer(
                    "Пожалуйста, укажите номер группы.\n"
                    "Пример: /search 1234"
                )
                return

            result = db.insertUserAndGroup(user_id, group_num)
            if result:
                await message.answer(
                    f"Группа {group_num} успешно привязана!\n\n"
                    "Теперь вы можете получать расписание:\n"
                    "• /today — на сегодня\n"
                    "• /tomorrow — на завтра\n"
                    "• /week — на неделю"
                )
            else:
                await message.answer(
                    "Ошибка при привязке группы.\n"
                    "Проверьте правильность номера группы.\n"
                    "Если ошибка повторяется, обратитесь к администратору."
                )

        # Обработчик команды /today
        @self.dp.message(Command("today"))
        async def today_command(message: types.Message):
            await self.send_rasp_today(message.from_user.id)

        # Обработчик команды /tomorrow
        @self.dp.message(Command("tomorrow"))
        async def tomorrow_command(message: types.Message):
            await self.send_rasp_tomorrow(message.from_user.id)

        # Обработчик команды /week
        @self.dp.message(Command("week"))
        async def week_command(message: types.Message):
            await message.answer("Расписание на неделю (функция в разработке)")

    async def run_polling(self) -> None:
        """Запуск бота в режиме polling"""
        await self.set_commands()  # Устанавливаем команды ПЕРЕД запуском
        print("Bot started polling...")
        await self.dp.start_polling(self.bot)

    def run(self) -> None:
        """Синхронная обёртка для запуска"""
        asyncio.run(self.run_polling())