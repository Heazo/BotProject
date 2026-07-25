#будет получать дату (например завтрашнюю) по которой будет делать запрос в БД и возвращать список кортежей
import psycopg2
from psycopg2.extras import RealDictCursor
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

    def getSessionsFromDB(self, date: str):
        """Retrieve sessions for a specific date.

        Args:
            date (str): Date string used to filter sessions in the database.

        Returns:
            list[dict]: A list of rows from the sessions table as dictionaries.
        """
        cur = self.con.cursor(cursor_factory=RealDictCursor)

        result = cur.execute("""SELECT * FROM public.sessions WHERE date = %s
                                ORDER BY id ASC""", (date,))
        # cur.execute("""SELECT * FROM public.sessions 
        #                         ORDER BY id ASC""")
        result = cur.fetchall()
        cur.close()
        return result

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
    
    #Можно использовать декораторы чтобы сделать код более честым и избавить каждый метод от одних и тех де проверок
    def insertUserAndGroup(self, user_id: str, group_num: str):
        """Insert a user and their associated group into the database.

        Args:
            user_id (str): User identifier to insert into the users table.
            group_num (str): Group identifier to associate with the user.

        Returns:
            bool: True if insertion succeeded, False if an error occurred.
        """
        cur = self.con.cursor()
        
        try:
            insert_query = """
                INSERT INTO users 
                    (vk_id, group_num)
                VALUES (%s, %s)
            """
            cur.execute(insert_query, (user_id, group_num))
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

    def __del__(self):
        """Close the database connection when the manager is destroyed."""
        if self.con:
            self.con.close()
            print("Database connection closed.")

