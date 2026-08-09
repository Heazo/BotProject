import asyncio
import logging

import asyncpg

from TG.TG_Bot import TelegramBotClass
from VK.VK_Bot import VKbot_class
from TimetableProvider.DB_Manager import DB_Manager
from tokens import password, tg_token, vk_token

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> int:
    db_manager = DB_Manager(
        host="localhost",
        port=5432,
        dbname="studies_db",
        user="postgres",
        password=password,
    )

    try:
        await db_manager.connect()
    except (asyncpg.PostgresError, OSError, TimeoutError) as exc:
        await db_manager.close()
        logger.error("Не удалось подключиться к PostgreSQL: %s", exc)
        return 1

    try:
        tgbot = TelegramBotClass(tg_token, db_manager)
        vkbot = VKbot_class(vk_token, db_manager)

        # Both polling tasks share this event loop and the asyncpg pool.
        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(tgbot.run_polling())
            task_group.create_task(vkbot.run_polling())
    finally:
        await db_manager.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
