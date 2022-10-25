import sqlite3
from config import admin

connection = sqlite3.connect('data.db')
q = connection.cursor()


def join(chat_id):
    q.execute(f"SELECT * FROM users WHERE user_id = {chat_id}")
    result = q.fetchall()
    if len(result) == 0:
        sql = 'INSERT INTO users (user_id, block, language) VALUES ({}, 0, ' \
              '"English")'.format(chat_id)
        q.execute(sql)
        connection.commit()


async def antiflood(*args, **kwargs):
    m = args[0]
    if m.chat.id == admin:
        pass
    else:
        await m.answer("Please, stop flooding! Now you have to wait 3 seconds "
                       "to continue!")


async def set_language(chat_id, lang):
    q.execute(f"UPDATE users SET language='{lang}' WHERE user_id = {chat_id}")
    connection.commit()
