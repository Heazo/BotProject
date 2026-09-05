#Парсер сайта рус нарфу. Будет класть в БД результаты парса через DB_Manager.
#Но в виде чего будет этот результат? #Список объектов Session (Пара)
#В последующем сделать парсер (отдельную функцию) по датам и группам, для динамического обновления БД во время работы. Естественно это надо сделать асинхронным
#Спарсить номера всех групп и сопоставить с url адресами

import os
import time
import logging

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from Models.session import Session
from Models.group import Group

logger = logging.getLogger(__name__)

class ParserNARFU:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=(403, 429, 500, 502, 503, 504),
            allowed_methods=('GET', 'HEAD'),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def get_all_rasp(self, url: str) -> list[Session]:
        """Getting a full list of all session for 4 weeks"""

        #lite-mode; hard-mode; extra-mode; ultra-extra-mod | парсим один день, парсим неделю, парсим все доступные недели, парсим весь сайт
        logger.info("Requesting timetable from NARFU")
        #создать таблицу соответствующих url адресов и групп


        # with open("rusNARFU.html", "w") as file:
        #     file.write(html_result)

        soup, html_result = self.get_access(url)
        if soup is None:
            return []

        title = soup.find("title")
        if title is None:
            return []

        group_num = title.text.replace("Группа ", "").replace(". Расписание САФУ", "")



        # navbar_brand = soup.find("a", {"class": "navbar-brand"})
        # if navbar_brand is None:
        #     group_num = "Err"
        # else:
        #     group_num = navbar_brand.find_all("span")[1].text.split()[0].strip()     #может быть не всегда так, надо будет проверить на других группах, но пока так (по крайней мере для 19439) работает


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

            sessions = day.select('div[class^="timetable_sheet hidden-xs"]')    #возможно будет смысл переделать на "timetable_sheet_xs visible-xs"

            for session in sessions:

                num_elem = session.find('span', {"class": "num_para"})
                time_elem = session.find('span', {"class": "time_para"})
                kind_elem = session.find('span', {"class": "kindOfWork"})
                discipline_elem = session.find('span', {"class": "discipline"})
                auditorium_elem = session.find('span', {"class": "auditorium"})
                group_elem = session.find('span', {"class": "group"})

                if auditorium_elem is not None:
                    auditorium_elem = auditorium_elem.text.strip()
                    auditorium_elem = ' '.join(auditorium_elem.split())

                # Пропускаем если нет важных элементов
                if not all([num_elem, time_elem, discipline_elem]):
                    continue

                sessions_list.append(
                    Session(
                        num_elem.text,
                        time_elem.text.strip(),
                        kind_elem.text if kind_elem else "",
                        discipline_elem.text,
                        auditorium_elem,
                        group_elem.text if group_elem else "",
                        group_num.strip() if group_num else "",
                        day_of_week,
                        date
                    )
                )
        return sessions_list

    def get_access(self, url: str):
        try:
            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            html_result = response.text
            soup = BeautifulSoup(html_result, 'html.parser')
            title = soup.find('title')
            if title is not None:
                logger.info("NARFU response title: %s", title.get_text(strip=True))
            return soup, html_result
        except requests.RequestException as exc:
            logger.error("NARFU request failed for %s: %s", url, exc)
            return None, ""

    def find_groups(self, url = "https://ruz.narfu.ru/")->list[Group]:       #-> list[Group]
        logger.info("Start find_groups()")
        soup, html_result = self.get_access(url)
        if soup is None:
            logger.error("soup is None in find_groups()")
            return []

        #institutions = soup.find_all('div', {"class": "hidden-xs col-sm-4 col-md-3 institution_button"})

        institutions = soup.select('a[href^="?groups&institution="]')

        institutions_urls = []
        group_urls = []
        groups = []
        for institution in institutions:
            institutions_urls.append(institution.get('href'))
        institutions_urls = list(set(institutions_urls))

        for institution_url in institutions_urls:
            time.sleep(0.5)
            insts_soup, html_result = self.get_access(url + institution_url)
            if insts_soup is None:
                continue

            group_buttons = insts_soup.find_all("div", {"class": "group_button"})
            own_institution_elem = insts_soup.find("h4", {"class": "visible-xs visible-sm"})
            own_institution = own_institution_elem.text if own_institution_elem is not None else ""

            # file_name = own_institution + ".html"
            # if os.path.exists(file_name):
            #     with open(file_name, "r") as file:
            #         file.read(html_result)
            # else:
            #     with open(file_name, "w") as file:
            #         file.write(html_result)



            for group_button in group_buttons:
                own_url = group_button.find("a", {"class": "hidden-xs"}).get('href').strip()
                own_url = url + own_url
                #own_group_num = group_button.find("span", {"class": "number"}).text
                all_info = group_button.find("a", {"class": "hidden-xs"})

                group_num = all_info.find("span", {"class": "number"}).text.strip()     #.text.split()[0].strip()

                speciality = None
                
                if all_info:
                    for content in all_info.contents:
                        if isinstance(content, str): 
                            text = content.strip()
                            if text:
                                speciality = ' '.join(text.split())
                                break
                if speciality is None:
                    speciality = ""
                
                profile = ""

                # own_speciality = None
                # if all_info is not None:
                #     all_info = all_info.split()
                # else :
                #     continue
                # if len(all_info) <= 2:
                #     speciality = ""
                #     profile = ""
                # else:
                #     speciality = all_info[1]
                #     profile = all_info[2]
                # group_num = all_info[0]


                groups.append(
                    Group(
                        url= own_url,
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