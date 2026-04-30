#будет получать дату (например завтрашнюю) по которой будет делать запрос в БД и возвращать список кортежей
import psycopg2
from psycopg2.extras import RealDictCursor
import Models.session as Session
import Models.group as Group

class DB_Manager:
    def __init__(self, host, port, dbname, user, password):
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
        
    def connectDB(self, host, port, dbname, user, password):
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
        
    #Обернуть в try!!!!
    def getSessionsFromDB (self, date): # -> list[tuple]

        cur = self.con.cursor(cursor_factory=RealDictCursor)

        result = cur.execute("""SELECT * FROM public.sessions WHERE date = %s
                                ORDER BY id ASC""", (date,))
        # cur.execute("""SELECT * FROM public.sessions 
        #                         ORDER BY id ASC""")
        result = cur.fetchall()
        cur.close()

        return result
    
    ###Защитить от дубликатов!!!

    def insertSessions(self, sessions: list[Session]):

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
                session.date
            ))
        self.con.commit()
        cur.close()

    #Обернуть в try!!!!
    def insertGroups(self, groups: list[Group]):
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
        cur = self.con.cursor()
        #Переименовать с vk_id на user_id в БД!!!
        try:
            insert_query = """
                INSERT INTO users 
                    (vk_id, group_num)
                VALUES (%s, %s)
            """ 
            cur.execute(insert_query,(user_id, group_num))
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
    

    def __del__(self):
        if self.con:
            self.con.close()
            print("Database connection closed.")

