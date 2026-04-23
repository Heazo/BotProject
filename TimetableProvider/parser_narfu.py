#Парсер сайта рус нарфу. Будет класть в БД результаты парса через DB_Manager.
#Но в виде чего будет этот результат? #Список объектов Session (Пара)
#В последующем сделать парсер (отдельную функцию) по датам и группам, для динамического обновления БД во время работы. Естественно это надо сделать асинхронным
#Спарсить номера всех групп и сопоставить с url адресами

import os
import requests
from bs4 import BeautifulSoup

from Models.session import Session
from Models.group import Group

class ParserNARFU:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_all_rasp(self, url: str) -> list[Session]:
        """Getting a full list of all session for 4 weeks"""

        #lite-mode; hard-mode; extra-mode; ultra-extra-mod | парсим один день, парсим неделю, парсим все доступные недели, парсим весь сайт
        print("requestNarfu")
        #создать таблицу соответствующих url адресов и групп


        # with open("rusNARFU.html", "w") as file:
        #     file.write(html_result)

        soup, html_result = self.get_access(url)

        navbar_brand = soup.find("a", {"class": "navbar-brand"})
        if navbar_brand is None:
            group_num = "Err"
        else:
            group_num = navbar_brand.find_all("span")[1].text.split()[0].strip()     #может быть не всегда так, надо будет проверить на других группах, но пока так (по крайней мере для 19439) работает


        sessions_list = []

        #Парсим все пары, что есть на странице
        days = soup.select('div[class^="list"]')
        for day in days:

            day_date = day.select('div[class^="dayofweek"]').pop()     #find("div", {"class": "dayofweek"})
            if day_date is None:
                continue
            parts = day_date.text.split(',')
            day_of_week = parts[0].strip()
            date = parts[1].strip()

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
                    # print(f"None session")
                    continue

                sessions_list.append(
                    Session(
                        num_elem.text,
                        time_elem.text,
                        kind_elem.text if kind_elem else "",
                        discipline_elem.text,
                        auditorium_elem.text if auditorium_elem else "",
                        group_elem.text if group_elem else "",
                        group_num.strip() if group_num else "",
                        day_of_week,
                        date
                    )
                )
        return sessions_list

    def get_access(self, url: str):
        response = requests.get(url, headers=self.headers)
        response.encoding = response.apparent_encoding
        html_result  = response.text
        soup = None

        if response.status_code == 200:
            print("Successful get request: ", response.status_code)
            soup = BeautifulSoup(html_result, 'html.parser')
            title = soup.title.text
            print("title: ", title)
            return soup, html_result
        else :
            print("Err get request: ", response.status_code)
            return

    def find_groups(self, url = "https://ruz.narfu.ru/")->list[Group]:       #-> list[Group]
        soup, html_result = self.get_access(url)

        #institutions = soup.find_all('div', {"class": "hidden-xs col-sm-4 col-md-3 institution_button"})

        institutions = soup.select('a[href^="?groups&institution="]')

        institutions_urls = []
        group_urls = []
        groups = []
        for institution in institutions:
            institutions_urls.append(institution.get('href'))
        institutions_urls = list(set(institutions_urls))

        for institution_url in institutions_urls:

            insts_soup, html_result = self.get_access(url + institution_url)

            group_buttons = insts_soup.find_all("div", {"class": "group_button"})
            own_institution = insts_soup.find("h4", {"class": "visible-xs visible-sm"}).text

            # file_name = own_institution + ".html"
            # if os.path.exists(file_name):
            #     print(f"Файл {file_name} уже существует")
            #     with open(file_name, "r") as file:
            #         file.read(html_result)
            # else:
            #     print(f"Файл {file_name} не найден, создаю...")
            #     with open(file_name, "w") as file:
            #         file.write(html_result)



            for group_button in group_buttons:
                own_url = group_button.find("a", {"class": "hidden-xs"}).get('href')
                #own_group_num = group_button.find("span", {"class": "number"}).text
                all_info = group_button.find("a", {"class": "hidden-xs"}).text

                own_speciality = None
                if all_info is not None:
                    all_info = all_info.split()
                else :
                    continue
                if len(all_info) <= 2:
                    speciality = ""
                    profile = ""
                else:
                    speciality = all_info[1]
                    profile = all_info[2]
                group_num = all_info[0]


                groups.append(
                    Group(
                        url= own_url.strip(),
                        group_num= group_num,
                        speciality= speciality,
                        profile= profile,
                        institution= own_institution.strip()
                    )
                )

        return groups



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