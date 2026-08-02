#будет получать дату (например завтрашнюю) по которой будет делать запрос в БД и возвращать список кортежей
import csv
import os

import psycopg2
from psycopg2.extras import RealDictCursor
from thefuzz import fuzz, process
from Models.session import Session
from Models.group import Group

class DB_Manager:
    """Database manager for PostgreSQL-backed session and group data.

    This class wraps a PostgreSQL connection and provides methods for retrieving
    sessions and groups, as well as inserting sessions, groups, and user-group
    associations.
    """

    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        """Initialize the manager and open a database connection.
        Args:
            host (str): PostgreSQL server host (for example, 'localhost').
            port (int): PostgreSQL server port (usually 5432).
            dbname (str): Name of the target database.
            user (str): Database user name.
            password (str): Database user password.
        """

        try:
            self.con = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password)
            print("Database is connected.")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.con = None

    def connectDB(self, host: str, port: int, dbname: str, user: str, password: str):
        """Connect to the database if a connection is not already open.

        Args:
            host (str): PostgreSQL server host.
            port (int): PostgreSQL server port.
            dbname (str): Name of the target database.
            user (str): Database user name.
            password (str): Database user password.
        """

        if self.con:
            print("The database is already connected.")
        else:
            try:
                self.con = psycopg2.connect(
                    host=host,
                    port=port,
                    dbname=dbname,
                    user=user,
                    password=password)
                print("Database is connected.")
            except Exception as e:
                print(f"Error connecting to database: {e}")
                self.con = None

    def getSessionsFromDB(self, date: str, group_num: str = None) -> list[dict]:
        """Retrieve sessions for a specific date.

        Args:
            date (str): Date string used to filter sessions in the database.
            group_num (str, optional): Group number to further filter sessions.

        Returns:
            list[dict]: A list of rows from the sessions table as dictionaries.
        """

        try:
            cur = self.con.cursor(cursor_factory=RealDictCursor)

            if group_num:
                result = cur.execute("""SELECT * FROM public.sessions WHERE date = %s AND group_num = %s
                                        ORDER BY id ASC""", (date, group_num))
            else:
                result = cur.execute("""SELECT * FROM public.sessions WHERE date = %s
                                        ORDER BY id ASC""", (date,))
            
            # cur.execute("""SELECT * FROM public.sessions
            #                         ORDER BY id ASC""")
            result = cur.fetchall()
            cur.close()

            return result

        except Exception as e:
            print(f"Ошибка БД: {e}")
            return None

    def getLastUpdateForGroup(self, group_num: str):
        """Return the most recent update timestamp for a specific group.

        Args:
            group_num (str): Group number to query in the sessions table.

        Returns:
            datetime.datetime | datetime.date | None: Latest value from the
            updated_at column, or None if no rows are found.
        """
        if not self.con or not group_num:
            return None

        cur = self.con.cursor()
        try:
            cur.execute(
                """
                SELECT MAX(updated_at) AS last_update
                FROM public.sessions
                WHERE group_num = %s
                """,
                (group_num,)
            )
            result = cur.fetchone()

            if not result or result[0] is None:
                return None

            value = result[0]
            #if hasattr(value, 'date'):
                #return value.date()
            return value
        except Exception as e:
            print(f"Error retrieving last update for group {group_num}: {e}")
            return None
        finally:
            cur.close()
            
    def getURLForGroup(self, group_num: str) -> str:
        """Retrieve the URL associated with a specific group.

        Args:
            group_num (str): Group number to look up in the groups table.

        Returns:
            str: The URL associated with the group, or None if not found.
        """
        if not self.con or not group_num:
            return None

        cur = self.con.cursor()
        try:
            cur.execute("""SELECT url FROM public.groups WHERE group_num = %s""", (group_num,))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Error retrieving URL for group {group_num}: {e}")
            return None
        finally:
            cur.close()

    def getGroupsFromDB(self) -> list[Group]:
        """Retrieve all groups from the database.

        Returns:
            list[Group]: A list of Group objects loaded from the groups table.
        """

        cur = self.con.cursor()
        cur.execute("""SELECT * FROM public.groups""")
        result = cur.fetchall()
        cur.close()

        groups = []
        for row in result:
            group = Group(
                group_num=row[0],
                speciality=row[1],
                profile=row[2],
                url=row[3],
                institution=row[4]
            )
            groups.append(group)

        return groups
    
    def getUserGroup(self, user_id: str) -> str:
        """Retrieve the group number associated with a specific user.

        Args:
            user_id (str): User identifier to look up in the users table.

        Returns:
            str: The group number associated with the user, or None if not found.
        """

        cur = self.con.cursor()
        cur.execute("""SELECT group_num FROM public.users WHERE user_id = %s""", (user_id,))
        result = cur.fetchone()
        cur.close()

        if result:
            return result
        else:
            return None

    def F1(self):
        print("F1 !!!!!!!!!!!!!!")

    def insertSessions(self, sessions: list[Session]):
        """Insert a batch of session records into the database.

        Args:
            sessions (list[Session]): Session objects to insert into the sessions table.
        """
        cur = self.con.cursor()
        insert_query = """
            INSERT INTO sessions 
                (num_session, time_session, kind_of_work, discipline, 
                auditorium, group_thread, group_num, day_of_week, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for session in sessions:
            cur.execute(insert_query, (
                session.num_session,
                session.time_session,
                session.kindOfWork,
                session.discipline,
                session.auditorium,
                session.group_thread,
                session.group_num,
                session.day_of_week,
                session.date,
            ))
        self.con.commit()
        cur.close()

    def replaceSessionsForGroup(self, group_num: str, sessions: list[Session]) -> bool:
        """Replace all sessions for a group with a new list of sessions.

        Args:
            group_num (str): Group number whose rows should be replaced.
            sessions (list[Session]): New session objects for this group.

        Returns:
            bool: True on success, False on failure.
        """
        if not self.con or not group_num:
            print("Error connecting to database or invalid group number")
            return False

        cur = self.con.cursor()
        try:
            cur.execute(
                "DELETE FROM public.sessions WHERE group_num = %s",
                (group_num,)
            )

            if sessions:
                insert_query = """
                    INSERT INTO sessions 
                        (num_session, time_session, kind_of_work, discipline,
                        auditorium, group_thread, group_num, day_of_week, date, is_choiced)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.executemany(insert_query, [
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
                ])

            self.con.commit()
            return True
        except Exception as e:
            self.con.rollback()
            print(f"Error replacing sessions for group {group_num}: {e}")
            return False
        finally:
            if cur:
                cur.close()

    def insertGroups(self, groups: list[Group]):
        """Insert groups into the database, ignoring duplicates.

        Args:
            groups (list[Group]): Group objects to insert into the groups table.
        """
        if not self.con:
            print("Error connecting to database")
            return

        cur = self.con.cursor()
        insert_query = """
            INSERT INTO groups (group_num, speciality, profile, url, institution)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (group_num) DO NOTHING
        """
        data = [(g.group_num, g.speciality, g.profile, g.url, g.institution) for g in groups]
        cur.executemany(insert_query, data)
        self.con.commit()
        cur.close()
    
    #Можно использовать декораторы чтобы сделать код более честым и избавить каждый метод от одних и тех же проверок
    def insertUserAndGroup(self, user_id: str, group_num: str, platform: str = "tg"):
        """Insert a user and their associated group into the database.

        Args:
            user_id (str): User identifier to insert into the users table.
            group_num (str): Group identifier to associate with the user.
            platform (str): Platform identifier - 'vk' or 'tg' (default: 'vk').

        Returns:
            bool: True if insertion succeeded, False if an error occurred.
        """
        cur = self.con.cursor()
        
        try:
            insert_query = """
                INSERT INTO users 
                    (user_id, group_num, platform)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET group_num = EXCLUDED.group_num
            """
            cur.execute(insert_query, (user_id, group_num, platform))
            self.con.commit()
        except psycopg2.errors.UniqueViolation:
            self.con.rollback()
            print(f"Error: User \"{user_id}\" already exists")
            return False
        except psycopg2.errors.ForeignKeyViolation:
            self.con.rollback()
            print(f"Error: Group {group_num} does not exist in groups table")
            return False
        except psycopg2.Error as e:
            self.con.rollback()
            print(f"Database error: {e.pgerror}")
            print(f"Error code: {e.pgcode}")
            return False
        except Exception as e:
            self.con.rollback()
            print(f"Unexpected error: {e}")
            return False
        finally:
            if cur:
                cur.close()
        return True
    
    def getUserDisciplines(self, user_id: str) -> list[dict]:
        """Retrieve the list of disciplines chosen by a user.

        Args:
            user_id (str): User identifier to look up in the user_choiced_disciplines table.

        Returns:
            list[dict]: A list of dictionaries containing discipline details.
        """
        cur = self.con.cursor(cursor_factory=RealDictCursor)
        try:
            query = """
                SELECT cd.id, cd.name, cd.normalized_name, cd.semesters, cd.source_pages
                FROM public.user_choiced_disciplines ucd
                JOIN public.choiced_disciplines cd ON ucd.discipline_id = cd.id
                WHERE ucd.user_id = %s
            """
            cur.execute(query, (user_id,))
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"Error retrieving user disciplines: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    def addUserDiscipline(self, user_id: str, discipline_id: int):
        """Add a discipline choice for a user.

        Args:
            user_id (str): User identifier.
            discipline_id (int): Discipline identifier.

        Returns:
            bool: True if insertion succeeded, False if an error occurred.
        """
        cur = self.con.cursor()

        try:
            insert_query = """
                INSERT INTO user_choiced_disciplines (user_id, discipline_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, discipline_id) DO NOTHING
            """
            cur.execute(insert_query, (user_id, discipline_id))
            self.con.commit()
        except psycopg2.Error as e:
            self.con.rollback()
            print(f"Database error: {e.pgerror}")
            print(f"Error code: {e.pgcode}")
            return False
        except Exception as e:
            self.con.rollback()
            print(f"Unexpected error: {e}")
            return False
        finally:
            if cur:
                cur.close()
        return True

    @staticmethod
    def _normalize_discipline_name(value: str) -> str:
        """Normalize a discipline name for fuzzy comparison.

        The method reduces punctuation and casing differences, and keeps both
        Russian and English names comparable in a single search space.
        """
        if not value:
            return ""

        text = value.lower().strip()
        replace_map = {
            'ё': 'е',
            'й': 'и',
            '-': ' ',
            '_': ' ',
            '/': ' ',
            '.': ' ',
            ',': ' ',
            ':': ' ',
            ';': ' ',
            '(': ' ',
            ')': ' ',
            '"': ' ',
            "'": ' ',
            '«': ' ',
            '»': ' ',
            '\n': ' ',
            '\t': ' ',
        }
        for old, new in replace_map.items():
            text = text.replace(old, new)

        return ' '.join(text.split())

    def find_best_discipline(self, discipline_name: str, min_score: int = 75) -> dict | None:
        """Return the single best match from choiced_disciplines.

        Works with both Russian and English input and uses thefuzz to rank the
        closest discipline name. If the best score is below the threshold,
        returns None instead of a random match.
        """
        if not self.con or not discipline_name or not discipline_name.strip():
            return None

        query = self._normalize_discipline_name(discipline_name)
        if not query:
            return None

        cur = self.con.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("""
                SELECT id, name, normalized_name, semesters, source_pages
                FROM public.choiced_disciplines
            """)
            rows = cur.fetchall()

            best_match = None
            best_score = 0

            for row in rows:
                for candidate in (row.get('name'), row.get('normalized_name')):
                    if not candidate:
                        continue

                    normalized_candidate = self._normalize_discipline_name(candidate)
                    if not normalized_candidate:
                        continue

                    score = max(
                        fuzz.ratio(query, normalized_candidate),
                        fuzz.token_set_ratio(query, normalized_candidate),
                        fuzz.partial_ratio(query, normalized_candidate),
                    )

                    if score > best_score:
                        best_score = score
                        best_match = dict(row)

            if best_match is None or best_score < min_score:
                return None

            return best_match
        except Exception as e:
            print(f"Error searching discipline: {e}")
            return None
        finally:
            cur.close()

    def addChosenDisciplineForUser(self, user_id: str, discipline_name: str) -> bool:
        """Attach a chosen discipline to a user by exact discipline name."""
        if not self.con:
            print("Error connecting to database")
            return False

        cur = self.con.cursor()
        try:
            cur.execute(
                """
                SELECT id FROM public.choiced_disciplines
                WHERE LOWER(normalized_name) = LOWER(%s)
                OR LOWER(name) = LOWER(%s)
                LIMIT 1
                """,
                (discipline_name, discipline_name)
            )
            result = cur.fetchone()
            if not result:
                print(f"Discipline not found: {discipline_name}")
                return False

            discipline_id = result[0]
            cur.execute(
                """
                INSERT INTO public.user_choiced_disciplines (user_id, discipline_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, discipline_id) DO NOTHING
                """,
                (user_id, discipline_id)
            )
            self.con.commit()
            return True
        except Exception as e:
            self.con.rollback()
            print(f"Error adding chosen discipline for user: {e}")
            return False
        finally:
            cur.close()
            

        

    def __del__(self):
        """Close the database connection when the manager is destroyed."""
        if self.con:
            self.con.close()
            print("Database connection closed.")

