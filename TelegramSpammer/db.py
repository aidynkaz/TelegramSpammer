from typing import Tuple, List


import os

from typing import List, Tuple
import sqlite3

conn = sqlite3.connect(os.path.join('db', 'script.db'))
cursor = conn.cursor()


def insert(table : str, values : str):
    
    """Inserts specified values into specified table"""

    if table == 'links':
        column = 'link'
        values = _parse_links(values)
    else:
        column = 'message_text'

    for value in values:
        cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))

    conn.commit()
        

def update(table : str, values : str):

    """Updates specified values in specified table
    !At the momend is used for message!"""
    if table == 'messages':
        column = 'message_text'
    else:
        raise KeyError(f"Update function does not support operations with '{table}' table")

    cursor.execute(
        f"UPDATE {table} "
        f"SET {column} = ? "
        f"WHERE id=1", (values,))
    conn.commit()


def getall(table : str) -> List[str]:

    """Extension onto fetchall
    Selects everything from specified table and puts in to a list"""

    cursor.execute(f'SELECT * from {table}')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(row[1])
    if table == 'links':
        result = _delete_empties(result)
    return result


def delete(table : str, values : str):

    """Deletes specified values from specified table"""

    if table == 'links':
        values = _parse_links(values)
        column = 'link'
        for value in values:
            cursor.execute(f"DELETE FROM {table} where ({column}) = (?)", (value,))
    else:
        column = 'message_text'
        cursor.execute(f"DELETE FROM {table} where {column} = ?", values)
    conn.commit()

def _init_db():

    """Initialize database by executing 'createdb' script"""

    with open('createdb.sql', 'r') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db():
    _init_db()


def _parse_links(message : str) -> Tuple:

    """Splits string by '\n' to a tuple"""

    parsed_msg = tuple(message.split('\n'))
    return parsed_msg


def _delete_empties(list_to_clear : List) -> List:

    """Paramters: links -> List
       
       Deletes duplicates and removes empty elements"""

    cleared_list = set(list_to_clear)
    try:
        cleared_list.remove('')
    except KeyError as e:
        pass
    return list(cleared_list)

check_db()
