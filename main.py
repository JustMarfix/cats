from collections import UserList
import mariadb
import telebot
import schedule
from io import BytesIO
import requests

from first_config import Config
from telebot.apihelper import ApiTelegramException

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
        global cursor
        cursor.execute(f"SELECT cid FROM `users` WHERE time = '{h}'")
        users = cursor.fetchall()
        
        for i in users:
            global user
            user = i
            send_cat(i[0])
    except mariadb.Error as e:
        print(f"Ошибка при рассылке людям с таймером {h}:\n {e}")
    except ApiTelegramException:
        cursor.execute(f"DELETE FROM `users` WHERE `uid` = {user[0]}")

    print('Рассылка успешно завершена.')


@bot.message_handler(content_types=['text'])
def new_message(message):
    try:
        global cursor
        cursor.execute(f"SELECT * FROM users WHERE uid = {message.from_user.id}")
        res = cursor.fetchall()

        if not res:
            # Регистрация пользователя
            cursor.execute(f"INSERT INTO `users` (`uid`, `cid`, `name`, `time`) VALUES ('{message.from_user.id}', '{message.chat.id}', '{message.from_user.first_name}', '12h');")
            conn.commit()

            bot.reply_to(message, 'Спасибо, что выбрали наших котиков! Теперь мы будем присылать Вам котяток :3')
            bot.reply_to(message, 'Чтобы отключить рассылку, просто остановите бота.')

            send_cat(message.chat.id)
    except mariadb.Error as e:
        bot.reply_to(message, f"😿 У нас возникла ошибка... Мы уже бежим исправлять её своими лапками! \nТекст: {e}")
        print(e)
        bot.send_message(Config.admin_id, "Алярм! Бот сломался!!")
        bot.send_message(Config.admin_id, "Алярм! Бот сломался!!")
        bot.send_message(Config.admin_id, "Алярм! Бот сломался!!")
        bot.send_message(Config.admin_id, e)

    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.add(telebot.types.InlineKeyboardButton(text="12 часов", callback_data='12h'))
    keyboard.add(telebot.types.InlineKeyboardButton(text="1 день", callback_data='24h'))
    keyboard.add(telebot.types.InlineKeyboardButton(text="3 дня", callback_data='3d'))
    keyboard.add(telebot.types.InlineKeyboardButton(text="7 дней", callback_data='7d'))

    bot.send_message(
        message.chat.id,
        "Выберите, раз во сколько времени Вам будет отправляться котик.",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    cursor.execute(f"UPDATE `users` SET time = '{call.data}' WHERE cid = {call.message.chat.id}")
    conn.commit()

    bot.answer_callback_query(callback_query_id=call.id, text='Изменения внесены.')
    bot.send_message(call.message.chat.id, "Изменения внесены.")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

def update_connection():
    cursor.execute("SELECT * FROM `users`")
    stock = cursor.fetchall()

def main():
    schedule.every().day.at("05:00").do(send_all,"12h")
    schedule.every().day.at("17:00").do(send_all,"12h")
    schedule.every().day.at("17:00").do(send_all, "24h")
    schedule.every(3).days.at("05:00").do(send_all, "3d")
    schedule.every().monday.at("05:00").do(send_all, "7d")
    schedule.every().day.do(print, "Новый день!!")
    schedule.every(1).hours.do(update_connection)

cursor.execute(f"SELECT cid FROM `users`")
users = cursor.fetchall()
for usr in users:
    try:
        global user
        user = usr
        bot.send_message(usr[0], "Починили бота.")
    except ApiTelegramException as error: 
        print(error)
        cursor.execute(f"DELETE FROM `users` WHERE `uid` = {user[0]}")

main()

bot.infinity_polling()
