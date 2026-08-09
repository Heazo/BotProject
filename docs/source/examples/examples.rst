Примеры
=====================

Использвание модуля DB_Manager.py
----------------------------------

.. code-block:: python

    from TimetableProvider.DB_Manager import DB_Manager

        #Инициализация
        db_manager = DB_Manager(
        host="localhost",
        port=5432,
        dbname="studies_db",
        user="postgres",
        password="13372281337"
    )

Получаем группы из БД и выводим на экран некоторые их поля
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    groups2 = db_manager.getGroupsFromDB()
    for group in groups2:
        print(f"{group.speciality} ({group.group_num}): {group.url}")

Запись пользователей и их групп
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Используется для записи новых пользователей в БД, или изменения группы пользователя
.. code-block:: python

    db_manager.insertUserAndGroup("Test", "151412")

Получаем расписание на определенную дату
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    #date = datetime.now().strftime("%d.%m.%Y")
    my_date = datetime(2026, 6, 21)
    date = my_date.strftime("%d.%m.%Y")
    print("Дата: ",date)
    sessions = db_manager.getSessionsFromDB(date)
    if sessions is not None:
        for session in sessions:
            print(session["time_session"], "\n", session["num_session"], ". ", session["kind_of_work"], "\n", session["discipline"], "\n", session["auditorium"], "\n=============================================", sep="")

    else:
        print(f"Расписание на {date} не найдено!")


Использвание модуля parser_narfu.py
-----------------------------------
.. code-block:: python

    from TimetableProvider.parser_narfu import ParserNARFU
    #Инициализация
    parser = ParserNARFU()

    #Получаем все группы с сайта и записываем их в БД
    groups = parser.find_groups()
    db_manager.insertGroups(groups)

Получаем расспинание одной из групп и записываем в базу данных
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    sessions = parser.get_all_rasp("https://ruz.narfu.ru/?timetable&group=19439")
    db_manager.insertSessions(sessions)

Пример того как можно выводить полученные пары в консоль
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    sessions = parser.get_all_rasp("https://ruz.narfu.ru/?timetable&group=19439")
    print("Количество пар всего: ",len(sessions))
    for session in sessions:
        print("-----------------------------------------------------------------")
        print("Дата: ", session.date)
        print("Номер пары: " ,session.num_session)
        print("Подгруппа (поток): ", session.group_thread)
        print("Номер группы: ", session.group_num)
        print("Предмет: ", session.discipline)
        print("Аудитория: ", session.auditorium)
        print("-----------------------------------------------------------------")


Очень кривой пример как можно спарсить пары вообще для всех групп
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Кривой потому что сайт блокируает слишком частые запросы и весь бот вылетает с ошибкой, по этому приходится каждый раз начинайть парс с группы на которой вылетело

.. code-block:: python

    kostil = False
    groups = db_manager.getGroupsFromDB()
    for group in groups:
        if group.group_num != "521222" and not kostil:
            continue
        else:
           kostil = True 

        sessions = parser.get_all_rasp(group.url)
        db_manager.insertSessions(sessions)

Пример добавления индивидуального предмета
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    #Сделать проверку на то что ничего не нашлось, и тогда напишем об этом пользователю
    #disp = "Имструменты анализа данных"
    #res = db_manager.find_best_discipline(disp)
    #db_manager.addUserDiscipline("931321821", res['id'])
    #disciplines = db_manager.getUserDisciplines("931321821")
    #print(disciplines[0]["name"])
    #print(disciplines[1]["name"])