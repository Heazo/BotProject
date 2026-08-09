import asyncio
import logging

import asyncpg

from config import load_settings
from TG.TG_Bot import TelegramBotClass
from VK.VK_Bot import VKbot_class
from TimetableProvider.DB_Manager import DB_Manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> int:
    try:
        settings = load_settings()
    except RuntimeError as exc:
        logger.error("Ошибка конфигурации: %s", exc)
        return 1
    logging.getLogger().setLevel(settings.log_level)

    db_manager = DB_Manager(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )

    try:
        await db_manager.connect()
    except (asyncpg.PostgresError, OSError, TimeoutError) as exc:
        await db_manager.close()
        logger.error("Не удалось подключиться к PostgreSQL: %s", exc)
        return 1

    try:
        tgbot = TelegramBotClass(settings.telegram_token, db_manager)
        vkbot = VKbot_class(settings.vk_token, db_manager)

        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(tgbot.run_polling())
            task_group.create_task(vkbot.run_polling())
    finally:
        await db_manager.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
