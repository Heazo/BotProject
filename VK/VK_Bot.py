from TimetableProvider.TimetableCreator import get_rasp_for_day, get_rasp_for_date
from TimetableProvider.DB_Manager import DB_Manager
from vkbottle import Bot, Keyboard, Text
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class VKbot_class:
    def __init__(self, m_token: str, db_manager: DB_Manager):
        self.bot = Bot(token=m_token)
        self.api = self.bot.api
        self.db = db_manager
        logger.info("Initializing VK Bot")
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

    async def send_rasp(self, user_id: int, day_offset: int) -> None:
        """Отправка расписания на день (0 - сегодня, 1 - завтра)"""

        group = await self.db.getUserGroup(str(user_id))
        if group:
            msg = await get_rasp_for_day(self.db, day_offset=day_offset, group_num=group[0])
        else:
            msg = self.find_group_message
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)

        # Отправляем расписание вместе с клавиатурой
        kb = self.get_keyboard()
        await self.sender(user_id, msg, kb)

    async def send_rasp_weekday(self, user_id: int, weekday: int, week_offset: int = 0) -> None:
        """Отправка расписания на конкретный день недели с учетом смещения недели"""

        group = await self.db.getUserGroup(str(user_id))
        if group:
            #datetime.now()
            now = datetime(2026, 6, 8)
            start_of_week = now - timedelta(days=now.weekday())
            target_week_start = start_of_week + timedelta(weeks=week_offset)
            target_date = target_week_start + timedelta(days=weekday)

            msg = await get_rasp_for_date(self.db, target_date, group_num=group[0])
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
        keyboard.add(Text("Неделя", payload={"command": "week"}))
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
        return keyboard

    def create_week_selection_keyboard(self):
        keyboard = Keyboard(one_time=False, inline=True)

        now = datetime(2026, 6, 8)
        start_of_week = now - timedelta(days=now.weekday())

        for i in range(6):
            week_start = start_of_week + timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)

            if i == 0:
                text = "🔵 Эта неделя"
            else:
                text = f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m')}"

            keyboard.add(
                Text(
                    text,
                    payload={
                        "cmd": "week",
                        "offset": i
                    }
                )
            )

            if (i + 1) % 2 == 0:
                keyboard.row()

        keyboard.row()
        keyboard.add(
            Text(
                "Назад",
                payload={"cmd": "back"}
            )
        )

        return keyboard

    def create_day_selection_keyboard(self, week_offset):
        keyboard = Keyboard(one_time=False, inline=True)

        now = datetime(2026, 6, 8)
        start_of_week = now - timedelta(days=now.weekday())
        target_week = start_of_week + timedelta(weeks=week_offset)

        weekdays = [
            ("Пн", 0),
            ("Вт", 1),
            ("Ср", 2),
            ("Чт", 3),
            ("Пт", 4),
            ("Сб", 5),
            ("Вс", 6),
        ]

        today = now.date()

        for i, (name, num) in enumerate(weekdays):

            date = target_week + timedelta(days=num)

            if date.date() == today:
                text = f"🔵 {name} Сегодня"
            elif date.date() == today + timedelta(days=1):
                text = f"🟢 {name} Завтра"
            else:
                text = f"{name} {date.strftime('%d.%m')}"

            keyboard.add(
                Text(
                    text,
                    payload={
                        "cmd": "day",
                        "week": week_offset,
                        "day": num
                    }
                )
            )

            if (i + 1) % 2 == 0:
                keyboard.row()

        keyboard.row()

        keyboard.add(
            Text(
                "Назад к неделям",
                payload={"cmd": "weeks"}
            )
        )

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
            result = await db.insertUserAndGroup(user_id, group_num, "vk")
            if result:
                # После привязки группы тоже показываем клавиатуру
                kb = self.get_keyboard()
                await message.answer(f"Группа {group_num} успешно привязана! \n"
                                     f"Теперь Вы можете получать расписание", keyboard=kb)
            else:
                await message.answer("Ошибка при привязке группы.\n"
                    "Проверьте правильность номера группы.\n"
                    "Если ошибка повторяется, обратитесь к администратору.")

        @self.bot.on.private_message(text=["Сегодня", "today", "/today"])
        async def today_command(message):
            await self.send_rasp(message.from_id, 0)

        @self.bot.on.private_message(text=["Завтра", "tomorrow", "/tomorrow"])
        async def tomorrow_command(message):
            await self.send_rasp(message.from_id, 1)

        @self.bot.on.private_message(text=["День недели", "weekday", "/weekday"])
        async def weekday_command(message):
            """Отправляет клавиатуру с днями недели"""
            kb = self.get_weekday_keyboard()
            await message.answer("Выберите день недели:", keyboard=kb)

        @self.bot.on.private_message(text=["Неделя", "week", "/week"])
        async def week_command(message):

            kb = self.create_week_selection_keyboard()

            await message.answer(
                "Выберите неделю:",
                keyboard=kb
            )

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

        @self.bot.on.private_message()
        async def payload_handler(message):

            if not message.payload:
                return

            payload = json.loads(message.payload)

            cmd = payload.get("cmd")

            if cmd == "week":

                week = int(payload["offset"])

                await message.answer(
                    "Выберите день:",
                    keyboard=self.create_day_selection_keyboard(week)
                )

            elif cmd == "day":

                await self.send_rasp_weekday(
                    message.from_id,
                    weekday=int(payload["day"]),
                    week_offset=int(payload["week"])
                )

            elif cmd == "weeks":

                await message.answer(
                    "Выберите неделю:",
                    keyboard=self.create_week_selection_keyboard()
                )

            elif cmd == "back":

                await message.answer(
                    "Главное меню:",
                    keyboard=self.get_keyboard()
                )

        @self.bot.on.private_message(text=["Назад", "back", "/back"])
        async def back_command(message):
            """Возврат в главное меню"""
            kb = self.get_keyboard()
            await message.answer("Главное меню:", keyboard=kb)


    def event_handler(self) -> None:
        self.bot.run()

    async def run_polling(self) -> None:
        """Run VK polling on the application's existing event loop."""
        self.bot.loop_wrapper._running = True
        try:
            await self.bot.run_polling()
        finally:
            self.bot.loop_wrapper._running = False