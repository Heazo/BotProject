from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import logging
from datetime import datetime, timedelta
from TimetableProvider.TimetableCreator import get_rasp_for_day, get_rasp_for_date
from TimetableProvider.DB_Manager import DB_Manager
from config import EmojisSetEnum, Mess_Config

logger = logging.getLogger(__name__)

selected_EmojisSet = EmojisSetEnum.NEW_YEAR  #пока что глобално в файле, мб потом как нибудь по дате будет меняться либо для каждого человека отдельно исходя из БД

# Определяем состояния для FSM
class WeekSelectionStates(StatesGroup):
    selecting_week = State()
    selecting_day = State()

class TelegramBotClass:
    def __init__(self, token: str, db_manager: DB_Manager):
        self.bot = Bot(token=token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.db = db_manager
        self.week_offset = 0  # Храним выбранную неделю
        logger.info("Initializing Telegram Bot")
        self._register_handlers()

    async def set_commands(self) -> None:
        """Установка команд в меню бота"""
        commands = [
            BotCommand(command="search", description=Mess_Config.find_group_message),
            BotCommand(command="today", description=Mess_Config.today_description),
            BotCommand(command="tomorrow", description=Mess_Config.tomorrow_description),
            BotCommand(command="week", description=Mess_Config.week_description),
            *[
                BotCommand(command=command, description=description)
                for command, description in zip(
                    (
                        "monday", "tuesday", "wednesday", "thursday",
                        "friday", "saturday", "sunday",
                    ),
                    Mess_Config.weekday_descriptions,
                )
            ],
        ]
        await self.bot.set_my_commands(commands)
        logger.info("Commands set successfully")

    async def sender(self, user_id: int, msg: str) -> None:
        """Отправка сообщения пользователю"""
        
        await self.bot.send_message(chat_id=user_id, text=msg)

    async def send_rasp(self, user_id: int, day_offset: int) -> None:
        """Отправка расписания на день (0 - сегодня, 1 - завтра)"""

        group = await self.db.getUserGroup(str(user_id))
        if group:
            msg = await get_rasp_for_day(self.db, day_offset=day_offset, group_num=group[0], emojis_set=selected_EmojisSet)
        else:
            msg = Mess_Config.find_group_message
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)

    async def send_rasp_weekday(self, user_id: int, weekday: int, week_offset: int = 0) -> None:
        """Отправка расписания на конкретный день недели с учетом смещения недели"""

        group = await self.db.getUserGroup(str(user_id))
        if group:
            #datetime.now()
            now = datetime(2026, 6, 8)
            start_of_week = now - timedelta(days=now.weekday())
            target_week_start = start_of_week + timedelta(weeks=week_offset)
            target_date = target_week_start + timedelta(days=weekday)

            msg = await get_rasp_for_date(self.db, target_date, group_num=group[0], emojis_set=selected_EmojisSet)
        else:
            msg = Mess_Config.find_group_message

        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        await self.sender(user_id, msg)

    def create_week_selection_keyboard(self, current_week_offset: int = 0) -> InlineKeyboardMarkup:
        """Создание клавиатуры для выбора недели"""
        
        week_options = []
        for i in range(6):
            week_num = current_week_offset + i
            # datetime.now()
            now = datetime(2026, 6, 8)
            start_of_week = now - timedelta(days=now.weekday())
            week_start = start_of_week + timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)

            start_str = week_start.strftime("%d.%m")
            end_str = week_end.strftime("%d.%m")

            if week_num == 0:
                week_label = f"🔵 Текущая неделя"
            else:
                week_label = f"📅 {start_str} - {end_str}"

            week_options.append((week_label, week_num))

        keyboard = []
        for label, week_num in week_options:
            button = InlineKeyboardButton(
                text=label,
                callback_data=f"select_week_{week_num}"
            )
            keyboard.append([button])


        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def create_day_selection_keyboard(self, week_offset: int) -> InlineKeyboardMarkup:
        """Создание клавиатуры для выбора дня недели после выбора недели"""
        
        # datetime.now()
        now = datetime(2026, 6, 8)
        start_of_week = now - timedelta(days=now.weekday())
        target_week_start = start_of_week + timedelta(weeks=week_offset)

        weekdays = {
            "Пн": 0,
            "Вт": 1,
            "Ср": 2,
            "Чт": 3,
            "Пт": 4,
            "Сб": 5,
            "Вс": 6
        }

        keyboard = []
        row = []

        for i, (day_name, day_num) in enumerate(weekdays.items()):
            day_date = target_week_start + timedelta(days=day_num)
            date_str = day_date.strftime("%d.%m")

            today = now.date()
            day_date_only = day_date.date()

            if day_date_only == today:
                day_label = f"🔵 {day_name} (сегодня)"
            elif day_date_only == today + timedelta(days=1):
                day_label = f"🟢 {day_name} (завтра)"
            else:
                day_label = f"{day_name} {date_str}"

            button = InlineKeyboardButton(
                text=day_label,
                callback_data=f"select_day_{week_offset}_{day_num}"
            )
            row.append(button)

            if (i + 1) % 2 == 0:
                keyboard.append(row)
                row = []

        if row:
            keyboard.append(row)

        keyboard.append([
            InlineKeyboardButton(
                text="Назад к неделям",
                callback_data="back_to_weeks"
            )
        ])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    def _register_handlers(self) -> None:
        """Регистрация всех обработчиков"""
        
        db = self.db

        weekday_commands = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6
        }

        @self.dp.message(Command("start"))
        async def start_command(message: types.Message):
            await message.answer(Mess_Config.start_message)

        # Обработчик команды /search с параметром
        @self.dp.message(Command("search"))
        async def search_handler(message: types.Message, command: CommandObject):
            group_num = command.args
            user_id = str(message.from_user.id)

            if not group_num:
                await message.answer(Mess_Config.find_group_message)
                return

            result = await db.insertUserAndGroup(user_id, group_num, "tg")
            if result:
                await message.answer(
                    Mess_Config.group_linked_message.format(group_num=group_num)
                )
            else:
                await message.answer(Mess_Config.group_link_error_message)

        # Обработчик команды /today
        @self.dp.message(Command("today"))
        async def today_command(message: types.Message):
            await self.send_rasp(message.from_user.id, 0)

        # Обработчик команды /tomorrow
        @self.dp.message(Command("tomorrow"))
        async def tomorrow_command(message: types.Message):
            await self.send_rasp(message.from_user.id, 1)

        for command_name, weekday_num in weekday_commands.items():
            @self.dp.message(Command(command_name))
            async def weekday_command(message: types.Message, wn=weekday_num):
                user_id = str(message.from_user.id)
                await self.send_rasp_weekday(message.from_user.id, wn, 0)

        @self.dp.message(Command("week"))
        async def week_command(message: types.Message, state: FSMContext):
            user_id = str(message.from_user.id)

            # Устанавливаем состояние
            await state.set_state(WeekSelectionStates.selecting_week)
            keyboard = self.create_week_selection_keyboard(0)
            await message.answer(
                Mess_Config.choose_week_message,
                reply_markup=keyboard
            )

        # Обработчик callback-запросов для состояния "выбор недели"
        @self.dp.callback_query(StateFilter(WeekSelectionStates.selecting_week))
        async def process_week_selection(callback: types.CallbackQuery, state: FSMContext):
            data = callback.data

            if data.startswith("select_week_"):
                week_offset = int(data.split("_")[2])
                await state.update_data(week_offset=week_offset)
                await state.set_state(WeekSelectionStates.selecting_day)

                keyboard = self.create_day_selection_keyboard(week_offset)
                await callback.message.edit_text(
                    Mess_Config.choose_day_message,
                    reply_markup=keyboard
                )
                await callback.answer()

        # Обработчик callback-запросов для состояния "выбор дня"
        @self.dp.callback_query(StateFilter(WeekSelectionStates.selecting_day))
        async def process_day_selection(callback: types.CallbackQuery, state: FSMContext):
            data = callback.data

            if data == "back_to_weeks":
                await state.set_state(WeekSelectionStates.selecting_week)
                keyboard = self.create_week_selection_keyboard(0)
                await callback.message.edit_text(
                    Mess_Config.choose_week_message,
                    reply_markup=keyboard
                )
                await callback.answer()
                return

            if data.startswith("select_day_"):
                parts = data.split("_")
                week_offset = int(parts[2])
                weekday_num = int(parts[3])

                user_id = callback.from_user.id

                # Получаем и отправляем расписание
                await callback.message.delete()
                await self.send_rasp_weekday(user_id, weekday_num, week_offset)
                await callback.answer()

                # Очищаем состояние
                await state.clear()

    async def run_polling(self) -> None:
        """Запуск бота в режиме polling"""
        
        await self.set_commands()  # Устанавливаем команды ПЕРЕД запуском
        logger.info("Bot started polling")
        await self.dp.start_polling(self.bot)

    def run(self) -> None:
        """Синхронная обёртка для запуска"""
        
        asyncio.run(self.run_polling())