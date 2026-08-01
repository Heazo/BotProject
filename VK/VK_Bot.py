from TimetableProvider.TimetableCreator import get_rasp_for_day
from TimetableProvider.DB_Manager import DB_Manager
from vkbottle import Bot, Keyboard, Text
from vkbottle.tools import Callback
import json

class VKbot_class:
    def __init__(self, m_token: str, db_manager: DB_Manager):
        self.bot = Bot(token=m_token)
        self.api = self.bot.api
        self.db = db_manager
        print("Initializing VK Bot\n")
        self._register_handlers()

    async def sender(self, user_id: int, msg: str) -> None:
        await self.api.messages.send(user_id=user_id, message=msg, random_id=0)

    async def send_rasp_today(self, user_id: int) -> None:
        msg = get_rasp_for_day(self.db, day_offset=0)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        elif msg is None:
            msg = "Расписание на сегодня не найдено."
        else:
            msg = str(msg)
        await self.sender(user_id, msg)
        print(f"send_rasp_today...{msg}")

    async def send_rasp_tomorrow(self, user_id: int) -> None:
        msg = get_rasp_for_day(self.db, day_offset=1)
        if isinstance(msg, list):
            msg = "\n".join(str(item) for item in msg if item is not None)
        elif msg is None:
            msg = "Расписание на завтра не найдено."
        else:
            msg = str(msg)
        await self.sender(user_id, msg)
        print(f"send_rasp_tomorrow...{msg}")

    def get_inline_keyboard(self):
        keyboard = Keyboard(inline=True)  # inline=True - это инлайн-клавиатура

        # Первая строка с кнопкой "Расп сегодня"
        keyboard.add(
            Callback("Расп сегодня", payload={"action": "today"})
        )

        # Вторая строка с кнопкой "Расп завтра"
        keyboard.row()
        keyboard.add(
            Callback("Расп завтра", payload={"action": "tomorrow"})
        )

        return keyboard

    def get_reply_keyboard(self):
        keyboard = Keyboard(one_time=False, inline=False)
        keyboard.add(Text("Начать"))
        return keyboard

    def _register_handlers(self) -> None:
        db = self.db

        @self.bot.on.private_message(text=["/start", "начать", "Начать"])
        async def start_command(message):
            kb = self.get_inline_keyboard()
            await message.answer("Привет!", keyboard=kb)

            # ОБРАБОТЧИК CALLBACK-ЗАПРОСОВ
            @self.bot.on.raw_event("callback_query", dict)
            async def handle_callback_events(event: dict):
                print(f"Получен callback запрос")

                # Получаем данные из события
                object_data = event.get('object', {})
                payload = object_data.get('payload', {})
                from_id = object_data.get('user_id')

                # Парсим payload если это строка
                if isinstance(payload, str):
                    try:
                        payload = json.loads(payload)
                    except json.JSONDecodeError:
                        payload = {}

                action = payload.get('action') if isinstance(payload, dict) else None

                # Готовим ответ для подтверждения callback
                # Это ОБЯЗАТЕЛЬНО, иначе кнопка будет грузиться!
                callback_response = {
                    "response": {
                        "type": "show_snackbar",
                        "text": "✅ Обрабатываю запрос..."
                    }
                }

                if action == 'today':
                    print(f"Обработка today для пользователя {from_id}")

                    # Получаем расписание
                    msg = get_rasp_for_day(db, day_offset=0)

                    if isinstance(msg, list):
                        msg = "\n".join(str(item) for item in msg if item is not None)
                    elif msg is None:
                        msg = "❌ Расписание на сегодня не найдено."
                    else:
                        msg = str(msg)

                    # Отправляем расписание
                    await self.bot.api.messages.send(
                        user_id=from_id,
                        message=f"📚 Расписание на СЕГОДНЯ:\n\n{msg}",
                        random_id=0
                    )

                    # Возвращаем подтверждение для VK (убираем загрузку)
                    return callback_response

                elif action == 'tomorrow':
                    print(f"Обработка tomorrow для пользователя {from_id}")

                    msg = get_rasp_for_day(db, day_offset=1)

                    if isinstance(msg, list):
                        msg = "\n".join(str(item) for item in msg if item is not None)
                    elif msg is None:
                        msg = "❌ Расписание на завтра не найдено."
                    else:
                        msg = str(msg)

                    await self.bot.api.messages.send(
                        user_id=from_id,
                        message=f"📖 Расписание на ЗАВТРА:\n\n{msg}",
                        random_id=0
                    )

                    return callback_response

        @self.bot.on.private_message(text="/search <group_num>")
        async def search_handler(message, group_num: str):
            user_id = str(message.from_id)
            result = db.insertUserAndGroup(user_id, group_num, "vk")
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
            await self.send_rasp_today(message.from_id)

        @self.bot.on.private_message(text="/tomorrow")
        async def tomorrow_command(message):
            await self.send_rasp_tomorrow(message.from_id)

    def event_handler(self) -> None:
        self.bot.run()
