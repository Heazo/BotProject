from calendar import weekday

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from TimetableProvider.TimetableCreator import get_rasp_for_day, get_rasp_for_weekday
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
            BotCommand(command="search", description="Привязать группу (пример: /search 123456)"),
            BotCommand(command="today", description="Расписание на сегодня"),
            BotCommand(command="tomorrow", description="Расписание на завтра"),
            BotCommand(command="week", description="Расписание на неделю"),
            BotCommand(command="monday", description="Расписание на понедельник"),
            BotCommand(command="tuesday", description="Расписание на вторник"),
            BotCommand(command="wednesday", description="Расписание на среду"),
            BotCommand(command="thursday", description="Расписание на четверг"),
            BotCommand(command="friday", description="Расписание на пятницу"),
            BotCommand(command="saturday", description="Расписание на субботу"),
            BotCommand(command="sunday", description="Расписание на воскресенье")
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

    async def send_rasp_mon(self, user_id: int) -> None:
        """Отправка расписания на понедельник"""
        msg = get_rasp_for_weekday(self.db, weekday=0)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_mon...{msg}")

    async def send_rasp_tue(self, user_id: int) -> None:
        """Отправка расписания на вторник"""
        msg = get_rasp_for_weekday(self.db, weekday=1)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_tue...{msg}")

    async def send_rasp_wed(self, user_id: int) -> None:
        """Отправка расписания на среду"""
        msg = get_rasp_for_weekday(self.db, weekday=2)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_wed...{msg}")

    async def send_rasp_thu(self, user_id: int) -> None:
        """Отправка расписания на четверг"""
        msg = get_rasp_for_weekday(self.db, weekday=3)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_thu...{msg}")

    async def send_rasp_fri(self, user_id: int) -> None:
        """Отправка расписания на пятницу"""
        msg = get_rasp_for_weekday(self.db, weekday=4)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_fri...{msg}")

    async def send_rasp_sat(self, user_id: int) -> None:
        """Отправка расписания на субботу"""
        msg = get_rasp_for_weekday(self.db, weekday=5)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_sat...{msg}")

    async def send_rasp_sun(self, user_id: int) -> None:
        """Отправка расписания на воскресенье"""
        msg = get_rasp_for_weekday(self.db, weekday=6)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)
        print(f"send_rasp_sun...{msg}")


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

        @self.dp.message(Command("mon", "monday"))
        async def monday_command(message: types.Message):
            await self.send_rasp_mon(message.from_user.id)

        @self.dp.message(Command("tue", "tuesday"))
        async def tuesday_command(message: types.Message):
            await self.send_rasp_tue(message.from_user.id)

        @self.dp.message(Command("wed", "wednesday"))
        async def wednesday_command(message: types.Message):
            await self.send_rasp_wed(message.from_user.id)

        @self.dp.message(Command("thu", "thursday"))
        async def thursday_command(message: types.Message):
            await self.send_rasp_thu(message.from_user.id)

        @self.dp.message(Command("fri", "friday"))
        async def friday_command(message: types.Message):
            await self.send_rasp_fri(message.from_user.id)

        @self.dp.message(Command("sat", "saturday"))
        async def saturday_command(message: types.Message):
            await self.send_rasp_sat(message.from_user.id)

        @self.dp.message(Command("sun", "sunday"))
        async def sunday_command(message: types.Message):
            await self.send_rasp_sun(message.from_user.id)

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