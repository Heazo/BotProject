from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from TimetableProvider.TimetableCreator import get_unique_rasp
from TimetableProvider.DB_Manager import DB_Manager


class TelegramBotClass:
    def __init__(self, token: str, db_manager: DB_Manager):
        self.bot = Bot(token=token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.db = db_manager
        print("Initializing Telegram Bot\n")
        self._register_handlers()

    async def sender(self, user_id: int, msg: str) -> None:
        """Отправка сообщения пользователю"""
        await self.bot.send_message(chat_id=user_id, text=msg)

    async def send_rasp(self, user_id: int) -> None:
        """Отправка расписания"""
        msg = get_unique_rasp(self.db)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        elif msg is None:
            msg = "Расписание на сегодня не найдено."
        else:
            msg = str(msg)

        await self.sender(user_id, msg)
        print(f"send_rasp...{msg}")

    def get_keyboard(self) -> ReplyKeyboardMarkup:
        """Создание клавиатуры"""
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Начать")]],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        return keyboard

    def _register_handlers(self) -> None:
        """Регистрация всех обработчиков"""
        db = self.db
        bot_instance = self.bot  # Для доступа к методам бота в хендлерах

        # Обработчик команды /start
        @self.dp.message(Command("start"))
        async def start_command(message: types.Message):
            kb = self.get_keyboard()
            await message.answer("Привет!", reply_markup=kb)

        # Обработчик текстового сообщения "Начать" (регистронезависимо)
        @self.dp.message(F.text.lower() == "начать")
        async def start_text(message: types.Message):
            kb = self.get_keyboard()
            await message.answer("Привет!", reply_markup=kb)

        # Обработчик команды /поиск с параметром
        @self.dp.message(Command("поиск"))
        async def search_handler(message: types.Message, command: CommandObject):
            # Получаем аргумент команды (группу)
            group_num = command.args
            user_id = str(message.from_user.id)

            if not group_num:
                await message.answer("Пожалуйста, укажите номер группы. Пример: /поиск 1234")
                return

            result = db.insertUserAndGroup(user_id, group_num)
            if result:
                await message.answer(f"Группа {group_num} успешно привязана!")
            else:
                await message.answer("Ошибка при привязке группы. Проверьте правильность номера.")

        # Обработчик команды /today
        @self.dp.message(Command("today"))
        async def today_command(message: types.Message):
            await self.send_rasp(message.from_user.id)

    async def run_polling(self) -> None:
        """Запуск бота в режиме polling"""
        print("Bot started polling...")
        await self.dp.start_polling(self.bot)

    def run(self) -> None:
        """Синхронная обёртка для запуска"""
        asyncio.run(self.run_polling())

