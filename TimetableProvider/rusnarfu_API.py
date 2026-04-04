#Парсер сайта рус нарфу. Будет класть в БД результаты парса через DB_Manager.
#Но в виде чего будет этот результат? #Список объектов
#В последующем сделать парсер по датам и группам, для динамического обновления БД во время работы
#Спарсить номера всех групп и сопоставить с url адресами

import requests
from bs4 import BeautifulSoup

from Models.session import Session
from Models.stady_day import Stady_day
from Models.week import Week

def requestNarfu():
    #lite-mode; hard-mode; extra-mode; ultra-extra-mod | парсим один день, парсим неделю, парсим все доступные недели, парсим весь сайт
    print("requestNarfu")
    url = 'https://ruz.narfu.ru/?timetable&group=19439'     #создать таблицу соответствующих url адресов и групп

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    html_result  = response.text
    soup = None

    if response.status_code == 200:
        print("Successful get request: ", response.status_code)
        soup = BeautifulSoup(html_result, 'html.parser')
    else :
        print("Err get request: ", response.status_code)
        return
    #title = str(soup.find_all('title'))

    # #Парсим class="nav nav-tabs"
    # title = soup.title.text
    # nav_tab_weeks = soup.find_all("span", {"class": "visible-lg"})   # nav_tab_weeks[0].text - текущая неделя
    # print("title: ",title)
    # print("week: ",nav_tab_weeks[0].text)

    #Парсим текущую неделю

    #Парсим class="tab-content" то есть все недели
    weeks = soup.find_all("div" ,{"class": "row tab-pane"})
    weeks.insert(0, soup.find_all("div" ,{"class": "row tab-pane active"}).pop())

    data = []   #Список списков словарей

    sessions_list = []
    stady_day_list = []
    week_list = []

    for week in weeks:
        print("id = ",week.get('id'))
        days = week.select('div[class^="list"]')

        for day in days:
            day_date = week.find("div", {"class": "dayofweek hidden-xs hidden-sm"}).text
            sessions = day.select('div[class^="timetable_sheet"]')

            for session in sessions:

                num_elem = session.find('span', {"class": "num_para"})
                time_elem = session.find('span', {"class": "time_para"})
                kind_elem = session.find('span', {"class": "kindOfWork"})
                discipline_elem = session.find('span', {"class": "discipline"})
                auditorium_elem = session.find('span', {"class": "auditorium"})
                group_elem = session.find('span', {"class": "group"})

                # Пропускаем если нет важных элементов
                if not all([num_elem, time_elem, discipline_elem]):
                    #print(f"None session")
                    continue

                sessions_list.append(
                    Session(
                        num_elem.text,
                        time_elem.text,
                        kind_elem.text if kind_elem else "",
                        discipline_elem.text,
                        auditorium_elem.text if auditorium_elem else "",
                        group_elem.text if group_elem else "",
                        day_date
                    )
                )
            stady_day_list.append(Stady_day(day_date, sessions_list))
        week_list.append(Week(stady_day_list))
    return week_list

#def pars_for_day():



#Возможно на английском для БД будет лучше
# data_session = {
#     'день': day_date,
#     'номер пары': session.find('span', {"class": "num_para"}).text,
#     'время пары': session.find('span', {"class": "time_para"}).text,
#     'тип занятия': session.find('span', {"class": "kindOfWork"}).text,
#     'предмет': session.find('span', {"class": "discipline"}).text,
#     'аудитория': session.find('span', {"class": "auditorium"}).text,
#     'поток': session.find('span', {"class": "group"}).text
# }