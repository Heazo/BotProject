import asyncio
import logging
from collections.abc import Sequence
from typing import Any

import asyncpg
from thefuzz import fuzz

from Models.group import Group
from Models.session import Session

logger = logging.getLogger(__name__)


class DB_Manager:
    """Asynchronous PostgreSQL access layer backed by an asyncpg pool."""

    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self._connection_params = {
            "host": host,
            "port": port,
            "database": dbname,
            "user": user,
            "password": password,
        }
        self.pool: asyncpg.Pool | None = None
        self._pool_lock = asyncio.Lock()

    async def connect(self) -> None:
        """Create the connection pool if it has not been created yet."""
        if self.pool is not None:
            return
        async with self._pool_lock:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(**self._connection_params)
                logger.info("Database is connected.")

    async def close(self) -> None:
        """Close all connections in the pool."""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection closed.")

    async def _ensure_pool(self) -> asyncpg.Pool:
        await self.connect()
        if self.pool is None:
            raise RuntimeError("Database connection pool is not initialized")
        return self.pool

    async def connectDB(
        self, host: str, port: int, dbname: str, user: str, password: str
    ) -> None:
        """Update connection settings and establish the pool."""
        await self.close()
        self._connection_params = {
            "host": host,
            "port": port,
            "database": dbname,
            "user": user,
            "password": password,
        }
        await self.connect()

    async def getSessionsFromDB(
        self, date: str, group_num: str | None = None
    ) -> list[dict[str, Any]] | None:
        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                if group_num:
                    rows = await connection.fetch(
                        """
                        SELECT * FROM public.sessions
                        WHERE date = $1 AND group_num = $2
                        ORDER BY id ASC
                        """,
                        date,
                        group_num,
                    )
                else:
                    rows = await connection.fetch(
                        """
                        SELECT * FROM public.sessions
                        WHERE date = $1
                        ORDER BY id ASC
                        """,
                        date,
                    )
                return [dict(row) for row in rows]
        except asyncpg.PostgresError as exc:
            logger.error("Ошибка БД: %s", exc)
            return None
    
    async def getUnselectedDisc(self, user_id: str) -> list[str] | None:
        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                rows = await connection.fetch(
                    """
                    SELECT ch.name FROM public.choiced_disciplines ch
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM public.user_choiced_disciplines usr_ch
                        WHERE usr_ch.user_id = $1 AND usr_ch.discipline_id = ch.id
                    );
                    """, user_id)
                return [row["name"] for row in rows]
        except asyncpg.PostgresError as exc:
            logger.error("Ошибка БД: %s", exc)
            return None
        

    async def getLastUpdateForGroup(self, group_num: str) -> Any:
        if not group_num:
            return None
        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                return await connection.fetchval(
                    """
                    SELECT MAX(updated_at) AS last_update
                    FROM public.sessions
                    WHERE group_num = $1
                    """,
                    group_num,
                )
        except asyncpg.PostgresError as exc:
            logger.error("Error retrieving last update for group %s: %s", group_num, exc)
            return None

    async def getURLForGroup(self, group_num: str) -> str | None:
        if not group_num:
            return None
        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                return await connection.fetchval(
                    "SELECT url FROM public.groups WHERE group_num = $1",
                    group_num,
                )
        except asyncpg.PostgresError as exc:
            logger.error("Error retrieving URL for group %s: %s", group_num, exc)
            return None

    async def getGroupsFromDB(self) -> list[Group]:
        pool = await self._ensure_pool()
        async with pool.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM public.groups")
        return [
            Group(
                group_num=row[0],
                speciality=row[1],
                profile=row[2],
                url=row[3],
                institution=row[4],
            )
            for row in rows
        ]

    async def getUserGroup(self, user_id: str) -> tuple[Any, ...] | None:
        pool = await self._ensure_pool()
        async with pool.acquire() as connection:
            row = await connection.fetchrow(
                "SELECT group_num FROM public.users WHERE user_id = $1",
                user_id,
            )
        return tuple(row) if row else None

    async def insertSessions(self, sessions: Sequence[Session]) -> None:
        pool = await self._ensure_pool()
        query = """
            INSERT INTO sessions
                (num_session, time_session, kind_of_work, discipline,
                 auditorium, group_thread, group_num, day_of_week, date)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        values = [
            (
                session.num_session,
                session.time_session,
                session.kindOfWork,
                session.discipline,
                session.auditorium,
                session.group_thread,
                session.group_num,
                session.day_of_week,
                session.date,
            )
            for session in sessions
        ]
        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.executemany(query, values)

    async def replaceSessionsForGroup(
        self, group_num: str, sessions: Sequence[Session]
    ) -> bool:
        if not group_num:
            logger.warning("Invalid group number")
            return False

        pool = await self._ensure_pool()
        query = """
            INSERT INTO sessions
                (num_session, time_session, kind_of_work, discipline,
                 auditorium, group_thread, group_num, day_of_week, date, is_choiced)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        values = [
            (
                session.num_session,
                session.time_session,
                session.kindOfWork,
                session.discipline,
                session.auditorium,
                session.group_thread,
                session.group_num,
                session.day_of_week,
                session.date,
                session.is_choiced,
            )
            for session in sessions
        ]
        try:
            async with pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(
                        "DELETE FROM public.sessions WHERE group_num = $1",
                        group_num,
                    )
                    if values:
                        await connection.executemany(query, values)
            return True
        except asyncpg.PostgresError as exc:
            logger.error("Error replacing sessions for group %s: %s", group_num, exc)
            return False

    async def insertGroups(self, groups: Sequence[Group]) -> None:
        pool = await self._ensure_pool()
        query = """
            INSERT INTO groups (group_num, speciality, profile, url, institution)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (group_num) DO NOTHING
        """
        values = [
            (group.group_num, group.speciality, group.profile, group.url, group.institution)
            for group in groups
        ]
        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.executemany(query, values)

    async def insertUserAndGroup(
        self, user_id: str, group_num: str, platform: str = "tg"
    ) -> bool:
        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO users (user_id, group_num, platform)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id)
                    DO UPDATE SET group_num = EXCLUDED.group_num
                    """,
                    user_id,
                    group_num,
                    platform,
                )
            return True
        except asyncpg.ForeignKeyViolationError:
            logger.error("Group %s does not exist in groups table", group_num)
            return False
        except asyncpg.PostgresError as exc:
            logger.error("Database error: %s", exc)
            return False

    async def getUserDisciplines(self, user_id: str) -> list[dict[str, Any]]:
        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                rows = await connection.fetch(
                    """
                    SELECT cd.id, cd.name, cd.normalized_name, cd.semesters,
                           cd.source_pages
                    FROM public.user_choiced_disciplines ucd
                    JOIN public.choiced_disciplines cd
                      ON ucd.discipline_id = cd.id
                    WHERE ucd.user_id = $1
                    """,
                    user_id,
                )
            return [dict(row) for row in rows]
        except asyncpg.PostgresError as exc:
            logger.error("Error retrieving user disciplines: %s", exc)
            return []

    async def addUserDiscipline(self, user_id: str, discipline_id: int) -> bool:
        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO user_choiced_disciplines (user_id, discipline_id)
                    VALUES ($1, $2)
                    ON CONFLICT (user_id, discipline_id) DO NOTHING
                    """,
                    user_id,
                    discipline_id,
                )
            return True
        except asyncpg.PostgresError as exc:
            logger.error("Database error: %s", exc)
            return False

    @staticmethod
    def _normalize_discipline_name(value: str) -> str:
        if not value:
            return ""
        text = value.lower().strip()
        replace_map = {
            "ё": "е", "й": "и", "-": " ", "_": " ", "/": " ", ".": " ",
            ",": " ", ":": " ", ";": " ", "(": " ", ")": " ", '"': " ",
            "'": " ", "«": " ", "»": " ", "\n": " ", "\t": " ",
        }
        for old, new in replace_map.items():
            text = text.replace(old, new)
        return " ".join(text.split())

    async def find_best_discipline(
        self, discipline_name: str, min_score: int = 75
    ) -> dict[str, Any] | None:
        if not discipline_name or not discipline_name.strip():
            return None
        query = self._normalize_discipline_name(discipline_name)
        if not query:
            return None

        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                rows = await connection.fetch(
                    """
                    SELECT id, name, normalized_name, semesters, source_pages
                    FROM public.choiced_disciplines
                    """
                )
        except asyncpg.PostgresError as exc:
            logger.error("Error searching discipline: %s", exc)
            return None

        best_match = None
        best_score = 0
        for row in rows:
            row_dict = dict(row)
            for candidate in (row_dict.get("name"), row_dict.get("normalized_name")):
                if not candidate:
                    continue
                normalized_candidate = self._normalize_discipline_name(candidate)
                score = max(
                    fuzz.ratio(query, normalized_candidate),
                    fuzz.token_set_ratio(query, normalized_candidate),
                    fuzz.partial_ratio(query, normalized_candidate),
                )
                if score > best_score:
                    best_score = score
                    best_match = row_dict
        return best_match if best_match and best_score >= min_score else None

    async def removeUserDiscipline(
            self, user_id: str, discipline_id: int
    ) -> bool:
        pool = await self._ensure_pool()

        try:
            async with pool.acquire() as connection:
                result = await connection.execute(
                    """
                    DELETE FROM user_choiced_disciplines
                    WHERE user_id = $1
                      AND discipline_id = $2
                    """,
                    user_id,
                    discipline_id,
                )

            return result == "DELETE 1"

        except asyncpg.PostgresError as exc:
            logger.error("Database error: %s", exc)
            return False

    async def addChosenDisciplineForUser(
        self, user_id: str, discipline_name: str
    ) -> bool:
        pool = await self._ensure_pool()
        try:
            async with pool.acquire() as connection:
                discipline_id = await connection.fetchval(
                    """
                    SELECT id FROM public.choiced_disciplines
                    WHERE LOWER(normalized_name) = LOWER($1)
                       OR LOWER(name) = LOWER($2)
                    LIMIT 1
                    """,
                    discipline_name,
                    discipline_name,
                )
                if discipline_id is None:
                    logger.warning("Discipline not found: %s", discipline_name)
                    return False
                await connection.execute(
                    """
                    INSERT INTO public.user_choiced_disciplines (user_id, discipline_id)
                    VALUES ($1, $2)
                    ON CONFLICT (user_id, discipline_id) DO NOTHING
                    """,
                    user_id,
                    discipline_id,
                )
            return True
        except asyncpg.PostgresError as exc:
            logger.error("Error adding chosen discipline for user: %s", exc)
            return False
