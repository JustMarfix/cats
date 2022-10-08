import sys
import requests
import telebot
import mariadb
from io import BytesIO

from first_config import Config

bot = telebot.TeleBot(Config.token)

conn = mariadb.connect(
    user=Config.user,
    password=Config.password,
    database=Config.database,
    host=Config.host,
    port=Config.port,
)

cursor = conn.cursor()


def send_cat(chat_id):
    with BytesIO(requests.get(requests.get(Config.url).json()[0]['url']).content) as photo:
        bot.send_photo(chat_id, photo)

def send_all(h):
    try:
        cursor.execute(f"SELECT cid FROM `users` WHERE time = '{h}'")
        users = cursor.fetchall()
        
        for i in users:
            send_cat(users[i][0])
    except mariadb.Error as e:
        print(f"Ошибка при рассылке людям с таймером {h}:\n {e}")

    print('Рассылка успешно завершена.')
