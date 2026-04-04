from session import Session

class Stady_day:
    def __init__(self, day_date, session_list : list[Session]):
        self.day_date = day_date
        self.sessions = session_list