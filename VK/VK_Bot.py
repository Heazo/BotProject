from TimetableProvider.TimetableCreator import get_rasp_for_day, get_rasp_for_date
from TimetableProvider.DB_Manager import DB_Manager
from vkbottle import Bot, Keyboard, Text
from datetime import datetime, timedelta
import json
import logging
from config import EmojisSetEnum, Mess_Config

logger = logging.getLogger(__name__)

selected_EmojisSet = EmojisSetEnum.DEFAULT  # Пока что глобально в файле, мб потом как нибудь по дате будет меняться либо для каждого человека отдельно исходя из БД

class VKbot_class:
    def __init__(self, m_token: str, db_manager: DB_Manager):
        self.bot = Bot(token=m_token)
        self.api = self.bot.api
        self.db = db_manager
        logger.info("Initializing VK Bot")
        self._register_handlers()

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
            msg = await get_rasp_for_day(self.db, day_offset=day_offset, group_num=group[0], emojis_set=selected_EmojisSet, user_id=str(user_id))
            if isinstance(msg, list):
                msg = "\n".join(str(item) for item in msg if item is not None)
            kb = self.get_keyboard()
            await self.sender(user_id, msg, kb)
        else:
            msg = Mess_Config.find_group_message
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
            msg = await get_rasp_for_date(self.db, target_date, group_num=group[0], emojis_set=selected_EmojisSet, user_id=str(user_id))
            if isinstance(msg, list):
                msg = "\n".join(str(item) for item in msg if item is not None)
            kb = self.get_keyboard()
            await self.sender(user_id, msg, kb)
        else:
            msg = Mess_Config.find_group_message
            await self.sender(user_id, msg)

    def get_keyboard(self):
        keyboard = Keyboard(one_time=False, inline=True)
        keyboard.add(Text("День недели"))
        keyboard.add(Text("Неделя"))
        keyboard.row()
        keyboard.add(Text("Сегодня"))
        keyboard.add(Text("Завтра"))
        keyboard.row()
        keyboard.add(Text("Предметы по выбору"))
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

    def get_back_button_keyboard(self) -> Keyboard:
        keyboard = Keyboard(one_time=False, inline=True)
        keyboard.add(
            Text(
                "Назад",
                payload={"cmd": "back"}
            )
        )
        return keyboard

    def format_choice_disciplines(
            self,
            disciplines: list[dict]
    ) -> str:
        if not disciplines:
            return Mess_Config.no_choice_disciplines_message

        lines = [
            f"{Mess_Config.my_choice_disciplines_message}"
        ]

        for index, discipline in enumerate(disciplines, start=1):
            lines.append(
                f"{index}. {discipline['name']}"
            )

        lines.append(Mess_Config.how_add_and_remove_disciplines_message)

        return "\n".join(lines)

    def _register_handlers(self) -> None:
        db = self.db

        @self.bot.on.private_message(text=["начать", "Начать", "/start"])
        async def start_russian(message):
            kb = self.get_keyboard()
            await message.answer(Mess_Config.start_message, keyboard=kb)

        @self.bot.on.private_message(text="/search <group_num>")
        async def search_handler(message, group_num: str):
            user_id = str(message.from_id)
            result = await db.insertUserAndGroup(user_id, group_num, "vk")
            if result:
                # После привязки группы тоже показываем клавиатуру
                kb = self.get_keyboard()
                await message.answer(
                    Mess_Config.group_linked_short_message.format(group_num=group_num),
                    keyboard=kb,
                )
            else:
                await message.answer(Mess_Config.group_link_error_message)

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
            await message.answer(Mess_Config.choose_weekday_message, keyboard=kb)

        @self.bot.on.private_message(text=["Неделя", "week", "/week"])
        async def week_command(message):

            kb = self.create_week_selection_keyboard()

            await message.answer(
                Mess_Config.choose_week_message,
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

        @self.bot.on.private_message(text="Предметы по выбору")
        async def choice_disciplines_command(message):
            user_id = str(message.from_id)
            disciplines = await db.getUserDisciplines(user_id)
            await message.answer(
                self.format_choice_disciplines(disciplines),
                keyboard=self.get_back_button_keyboard()
            )

        @self.bot.on.private_message(text="/add <discipline_name>")
        async def add_discipline_handler(message, discipline_name: str):
            """Добавление предмета по выбору через команду /add с поиском по базе"""
            user_id = str(message.from_id)
            discipline_name = discipline_name.strip()
            if not discipline_name:
                await message.answer(
                    Mess_Config.empty_text_choice_discipline_error_message
                )
                return
            discipline = await db.find_best_discipline(
                discipline_name,
                min_score=75
            )
            if discipline is None:
                await message.answer(
                    Mess_Config.choice_discipline_not_found_message
                )
                return
            current_disciplines = await db.getUserDisciplines(user_id)

            already_added = any(
                item["id"] == discipline["id"]
                for item in current_disciplines
            )

            if already_added:
                await message.answer(
                    f"Предмет «{discipline['name']}» "
                    "уже есть в вашем списке.",
                )
                return

            success = await db.addUserDiscipline(
                user_id,
                discipline["id"]
            )

            if not success:
                await message.answer(
                    Mess_Config.choice_discipline_add_error_message
                )
                return

            disciplines = await db.getUserDisciplines(user_id)

            await message.answer(
                f"Предмет «{discipline['name']}» добавлен.\n"
                + self.format_choice_disciplines(disciplines)
            )

        @self.bot.on.private_message(text="/remove <discipline>")
        async def remove_discipline_handler(message, discipline: str):
            """Удаление предмета по выбору через команду /remove с проверкой наличия"""
            user_id = str(message.from_id)
            discipline_name = discipline.strip()

            if not discipline_name:
                await message.answer(
                    Mess_Config.empty_text_choice_discipline_error_message
                )
                return

            disciplines = await db.getUserDisciplines(user_id)

            if not disciplines:
                await message.answer(
                    Mess_Config.no_choice_disciplines_to_delete_message,
                )
                return

                # Ищем предмет среди добавленных пользователем
            found_discipline = None
            for item in disciplines:
                if item["name"].lower() == discipline_name.lower():
                    found_discipline = item
                    break
            if found_discipline is None:
                await message.answer(
                    f"Не удалось найти предмет «{discipline_name}» в вашем списке.\n"
                )
                return
            success = await db.removeUserDiscipline(
                user_id,
                found_discipline["id"]
            )
            if not success:
                await message.answer(
                    Mess_Config.choice_discipline_delete_error_message
                )
                return
            disciplines = await db.getUserDisciplines(user_id)
            await message.answer(
                f"Предмет «{found_discipline['name']}» удалён.\n"
                + self.format_choice_disciplines(disciplines),
            )

        @self.bot.on.private_message(text=["Назад", "back", "/back"])
        async def back_command(message):
            kb = self.get_keyboard()
            await message.answer(Mess_Config.main_menu_message, keyboard=kb)

        @self.bot.on.private_message()
        async def payload_handler(message):

            if not message.payload:
                return

            payload = json.loads(message.payload)

            cmd = payload.get("cmd")

            if cmd == "week":

                week = int(payload["offset"])

                await message.answer(
                    Mess_Config.choose_day_message,
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
                    Mess_Config.choose_week_message,
                    keyboard=self.create_week_selection_keyboard()
                )

            elif cmd == "back":

                await message.answer(
                    Mess_Config.main_menu_message,
                    keyboard=self.get_keyboard()
                )


    def event_handler(self) -> None:
        self.bot.run()

    async def run_polling(self) -> None:
        """Run VK polling on the application's existing event loop."""
        self.bot.loop_wrapper._running = True
        try:
            await self.bot.run_polling()
        finally:
            self.bot.loop_wrapper._running = False