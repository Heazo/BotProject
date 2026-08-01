from TimetableProvider.TimetableCreator import get_rasp_for_day, get_rasp_for_date
from TimetableProvider.DB_Manager import DB_Manager
from vkbottle import Bot, Keyboard, Text
from datetime import datetime, timedelta


class VKbot_class:
    def __init__(self, m_token: str, db_manager: DB_Manager):
        self.bot = Bot(token=m_token)
        self.api = self.bot.api
        self.db = db_manager
        print("Initializing VK Bot\n")
        self._register_handlers()
        self.find_group_message = "Пожалуйста, укажите номер группы.\nПример: /search 123456"

    async def sender(self, user_id: int, msg: str, keyboard=None) -> None:
        """Отправка сообщения с опциональной клавиатурой"""
        await self.api.messages.send(
            user_id=user_id,
            message=msg,
            random_id=0,
            keyboard=keyboard.get_json() if keyboard else None
        )

    async def send_rasp_today(self, user_id: int) -> None:
        group = self.db.getUserGroup(str(user_id))
        if group:
            msg = get_rasp_for_day(self.db, day_offset=0, group_num=group[0])
        else:
            msg = self.find_group_message
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)

        # Отправляем расписание вместе с клавиатурой
        kb = self.get_keyboard()
        await self.sender(user_id, msg, kb)
        print(f"Your group: {group}")
        print(f"send_rasp_today...{msg}")

    async def send_rasp_tomorrow(self, user_id: int) -> None:
        group = self.db.getUserGroup(str(user_id))
        if group:
            msg = get_rasp_for_day(self.db, day_offset=1, group_num=group[0])
        else:
            msg = self.find_group_message

        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)

        # Отправляем расписание вместе с клавиатурой
        kb = self.get_keyboard()
        await self.sender(user_id, msg, kb)
        print(f"Your group: {group}")
        print(f"send_rasp_tomorrow...{msg}")

    async def send_rasp_weekday(self, user_id: int, weekday: int, week_offset: int = 0) -> None:
        """Отправка расписания на конкретный день недели с учетом смещения недели"""

        group = self.db.getUserGroup(str(user_id))
        if group:
            #datetime.now()
            now = datetime(2026, 6, 8)
            start_of_week = now - timedelta(days=now.weekday())
            target_week_start = start_of_week + timedelta(weeks=week_offset)
            target_date = target_week_start + timedelta(days=weekday)

            msg = get_rasp_for_date(self.db, target_date, group_num=group[0])
        else:
            msg = self.find_group_message

        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)

        kb = self.get_keyboard()
        await self.sender(user_id, msg, kb)

    def get_keyboard(self):
        keyboard = Keyboard(one_time=False, inline=True)
        keyboard.add(Text("Начать"))
        keyboard.row()
        keyboard.add(Text("День недели", payload={"command": "weekday"}))
        keyboard.row()
        keyboard.add(Text("Сегодня", payload={"command": "today"}))
        keyboard.add(Text("Завтра", payload={"command": "tomorrow"}))
        return keyboard

    def get_weekday_keyboard(self):
        """Клавиатура с днями недели"""
        keyboard = Keyboard(one_time=False, inline=True)
        # Понедельник - Воскресенье (2 ряда по 4 и 3 кнопки)
        keyboard.add(Text("Пн", payload={"weekday": 0}))
        keyboard.add(Text("Вт", payload={"weekday": 1}))
        keyboard.add(Text("Ср", payload={"weekday": 2}))
        keyboard.add(Text("Чт", payload={"weekday": 3}))
        keyboard.row()
        keyboard.add(Text("Пт", payload={"weekday": 4}))
        keyboard.add(Text("Сб", payload={"weekday": 5}))
        keyboard.add(Text("Вс", payload={"weekday": 6}))
        keyboard.row()
        # Кнопка для возврата в главное меню
        keyboard.add(Text("Назад", payload={"command": "back"}))
        return keyboard

    def _register_handlers(self) -> None:
        db = self.db

        @self.bot.on.private_message(text=["начать", "Начать", "/start"])
        async def start_russian(message):
            kb = self.get_keyboard()
            await message.answer("Привет! Выберите день для просмотра расписания:", keyboard=kb)

        @self.bot.on.private_message(text="/search <group_num>")
        async def search_handler(message, group_num: str):
            user_id = str(message.from_id)
            result = db.insertUserAndGroup(user_id, group_num, "vk")
            if result:
                # После привязки группы тоже показываем клавиатуру
                kb = self.get_keyboard()
                await message.answer(f"Группа {group_num} успешно привязана!", keyboard=kb)
            else:
                await message.answer("Ошибка")

        @self.bot.on.private_message(text=["Сегодня", "today", "/today"])
        async def today_command(message):
            await self.send_rasp_today(message.from_id)

        @self.bot.on.private_message(text=["Завтра", "tomorrow", "/tomorrow"])
        async def tomorrow_command(message):
            await self.send_rasp_tomorrow(message.from_id)

        @self.bot.on.private_message(text=["День недели", "weekday", "/weekday"])
        async def weekday_command(message):
            """Отправляет клавиатуру с днями недели"""
            kb = self.get_weekday_keyboard()
            await message.answer("Выберите день недели:", keyboard=kb)

        @self.bot.on.private_message(text=["Пн", "Вт", "Ср", "Чт",
                                           "Пт", "Сб", "Вс"])
        async def weekday_selection(message):
            """Обработка выбора дня недели из текстового ввода"""
            weekday_map = {
                "Пн": 0, "Вт": 1, "Ср": 2, "Чт": 3,
                "Пт": 4, "Сб": 5, "Вс": 6
            }
            weekday = weekday_map.get(message.text)
            if weekday is not None:
                await self.send_rasp_weekday(message.from_id, weekday)

        @self.bot.on.private_message(text=["Назад", "back", "/back"])
        async def back_command(message):
            """Возврат в главное меню"""
            kb = self.get_keyboard()
            await message.answer("Главное меню:", keyboard=kb)

    def event_handler(self) -> None:
        self.bot.run()