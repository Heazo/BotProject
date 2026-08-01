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

    def createChoicedDisciplinesTable(self, csv_path: str) -> bool:
        """Create choiced disciplines tables and populate them from catalog.csv.

        The structure is:
            - choiced_disciplines: catalog records
            - user_choiced_disciplines: many-to-many association table between users(user_id)
              and choiced_disciplines(id)

        Args:
            csv_path (str): Path to the CSV file with columns:
                name, normalized_name, semesters, source_pages

        Returns:
            bool: True on success, False otherwise.
        """
        if not self.con:
            print("Error connecting to database")
            return False

        cur = self.con.cursor()

        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS choiced_disciplines (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    normalized_name TEXT NOT NULL,
                    semesters TEXT,
                    source_pages TEXT,
                    UNIQUE (normalized_name)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_choiced_disciplines (
                    user_id BIGINT NOT NULL,
                    discipline_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, discipline_id),
                    CONSTRAINT fk_user_choiced_user_id
                        FOREIGN KEY (user_id)
                        REFERENCES public.users(user_id)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_user_choiced_discipline
                        FOREIGN KEY (discipline_id)
                        REFERENCES public.choiced_disciplines(id)
                        ON DELETE CASCADE
                )
            """)

            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV file not found: {csv_path}")

            with open(csv_path, newline='', encoding='utf-8-sig') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    if not row:
                        continue

                    name = (row.get('name') or '').strip()
                    normalized_name = (row.get('normalized_name') or '').strip()
                    semesters = (row.get('semesters') or '').strip()
                    source_pages = (row.get('source_pages') or '').strip()

                    if not name:
                        continue

                    if not normalized_name:
                        normalized_name = name.lower()

                    cur.execute(
                        """
                        INSERT INTO choiced_disciplines (name, normalized_name, semesters, source_pages)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (normalized_name)
                        DO UPDATE SET
                            name = EXCLUDED.name,
                            semesters = EXCLUDED.semesters,
                            source_pages = EXCLUDED.source_pages
                        """,
                        (name, normalized_name, semesters, source_pages)
                    )

            self.con.commit()
            return True

        except Exception as e:
            self.con.rollback()
            print(f"Error creating choiced disciplines table: {e}")
            return False
        finally:
            cur.close()

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

    def createChoicedDisciplinesTable(self, csv_path: str) -> bool:
        """Create the chosen disciplines catalog from catalog.csv and link it to users through a many-to-many table.

        Args:
            csv_path (str): Path to the CSV file with columns: name, normalized_name, semesters, source_pages.

        Returns:
            bool: True if the table and catalog were created successfully, otherwise False.
        """
        if not self.con:
            print("Error connecting to database")
            return False

        cur = self.con.cursor()
        try:
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema='public' AND table_name='users'
            """)
            user_columns = {row[0]: row[1] for row in cur.fetchall()}

            if "user_id" in user_columns:
                user_key_col = "user_id"
                user_key_type = user_columns["user_id"]
                user_target = "public.users(user_id)"
            elif "user_id" in user_columns:
                user_key_col = "user_id"
                user_key_type = user_columns["user_id"]
                user_target = "public.users(user_id)"
            else:
                raise ValueError("Таблица users должна содержать столбец user_id или user_id")

            if user_key_type in ("character varying", "varchar", "text", "bpchar"):
                join_user_type_sql = "TEXT"
            elif user_key_type in ("integer", "bigint", "smallint"):
                join_user_type_sql = "BIGINT"
            else:
                join_user_type_sql = "TEXT"

            cur.execute("""
                CREATE TABLE IF NOT EXISTS public.choiced_disciplines (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    normalized_name TEXT NOT NULL UNIQUE,
                    semesters TEXT,
                    source_pages TEXT
                )
            """)

            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS public.user_choiced_disciplines (
                    user_id {join_user_type_sql} NOT NULL,
                    discipline_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, discipline_id),
                    CONSTRAINT fk_user_choiced_disciplines_user
                        FOREIGN KEY (user_id) REFERENCES {user_target}
                        ON DELETE CASCADE,
                    CONSTRAINT fk_user_choiced_disciplines_discipline
                        FOREIGN KEY (discipline_id) REFERENCES public.choiced_disciplines(id)
                        ON DELETE CASCADE
                )
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_choiced_disciplines_user_id
                ON public.user_choiced_disciplines (user_id)
            """)

            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV file not found: {csv_path}")

            with open(csv_path, "r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    name = (row.get("name") or "").strip()
                    normalized_name = (row.get("normalized_name") or "").strip()
                    semesters = (row.get("semesters") or "").strip()
                    source_pages = (row.get("source_pages") or "").strip()

                    if not name and not normalized_name:
                        continue

                    cur.execute("""
                        INSERT INTO public.choiced_disciplines (name, normalized_name, semesters, source_pages)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (normalized_name)
                        DO UPDATE SET
                            name = EXCLUDED.name,
                            semesters = EXCLUDED.semesters,
                            source_pages = EXCLUDED.source_pages
                    """, (name, normalized_name, semesters, source_pages))

            self.con.commit()
            print(f"Table choiced_disciplines created and filled from: {csv_path}")
            return True

        except Exception as e:
            self.con.rollback()
            print(f"Error creating choiced disciplines table: {e}")
            return False
        finally:
            if cur:
                cur.close()

    def __del__(self):
        """Close the database connection when the manager is destroyed."""
        if self.con:
            self.con.close()
            print("Database connection closed.")

