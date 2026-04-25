#будет получать дату (например завтрашнюю) по которой будет делать запрос в БД и возвращать список кортежей
import psycopg2
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
        
    
    def getSessionsFromDB (self, date): # -> list[tuple]

        cur = self.con.cursor()

        result = cur.execute("SELECT * FROM sessions WHERE date = %s", (date,)).fetchall()

        cur.close()

        #result = date   #Для тестов - удалить!
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

    def insertUserAndGroup(self, user_id: str, group_num: str):
        cur = self.con.cursor()
        #Переименовать с vk_id на user_id в БД!!!
        insert_query = """
            INSERT INTO users 
                (vk_id, group_num)
            VALUES (%s, %s)
        """ 
        cur.execute(insert_query,(user_id, group_num))
        self.con.commit()
        cur.close()
    

    def __del__(self):
        if self.con:
            self.con.close()
            print("Database connection closed.")


    