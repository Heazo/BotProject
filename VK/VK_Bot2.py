#основное место бота с определениями команд, меню и так далее

from vkbottle.bot import Bot, Message

from tokens import vk_token
from TimetableProvider.TimetableCreator import get_unique_rasp

bot = Bot(token=vk_token)

@bot.on.private_message(text="начать")
async def handle_start(message: Message):
    await message.answer("Абиба абоба")

@bot.on.private_message(text="/start")
async def handle_start_cmd(message: Message):
    await message.answer("/start")

@bot.on.private_message(text="/help")
async def handle_help(message: Message):
    await message.answer("/help")

@bot.on.private_message(text="/about")
async def handle_about(message: Message):
    await message.answer("/about")

@bot.on.private_message(text="/contact")
async def handle_contact(message: Message):
    await message.answer("/contact")

@bot.on.private_message(text="/today")
async def handle_today(message: Message):
    msg = get_unique_rasp()
    await message.answer(msg)
    print(f"send_rasp...{msg}")

