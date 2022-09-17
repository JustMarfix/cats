import telebot
import mariadb as db
import requests as r
import sys

from config import Config
from io import BytesIO

bot = telebot.TeleBot(Config.token)

conn = db.connect(
    user=Config.user,
    password=Config.password,
    database=Config.database,
    host=Config.host,
    port=Config.port,
)

cursor = conn.cursor()

def send_cat(chat_id):
    with BytesIO(r.get(r.get(Config.url).json()[0]['url']).content) as photo:
        bot.send_photo(chat_id, photo)

try:
    cursor.execute(f"SELECT cid FROM `users` WHERE time = '12h'")
    users = cursor.fetchall()
    i = 0
    while i < len(users):
        send_cat(users[i][0])
        i += 1
except db.Error as e:
    print(f"Ошибка!\nЛог MariaDB: {e}\n\nЛог sys: {sys.exc_info}")
print('Рассылка успешно завершена.')