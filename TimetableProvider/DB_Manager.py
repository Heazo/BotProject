#будет получать дату (например завтрашнюю) по которой будет делать запрос в БД и возвращать список кортежей


import sqlite3

def getRaspFromDB (date) -> list[tuple]:

    con = sqlite3.connect("")
    cur = con.cursor()

    result = cur.execute("")

    con.close()
    return result

