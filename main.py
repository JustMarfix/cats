from lib2to3.pytree import Base
import requests as r
import mariadb as db
import telebot

from first_config import Config

from telebot import types

bot = telebot.TeleBot(Config.token)

conn = db.connect(
    user=Config.user,
    password=Config.password,
    database=Config.database,
    host=Config.host,
    port=Config.port,
)

cursor = conn.cursor()

@bot.message_handler(content_types=['text'])
def new_message(message):
    try:
        cursor.execute(f"SELECT * FROM users WHERE uid = {message.from_user.id}")
        res = cursor.fetchall()
        if not res:
            # Регистрация пользователя
            cursor.execute(f"INSERT INTO `users` (`uid`, `cid`, `name`, `time`) VALUES ('{message.from_user.id}', '{message.chat.id}', '{message.from_user.first_name}', '12h');")
            conn.commit()
            bot.reply_to(message, 'Спасибо, что выбрали наших котиков! Теперь мы будем присылать Вам котят.')
            bot.reply_to(message, 'Чтобы отключить рассылку, просто остановите бота.')
            print(message.chat.id)
    except db.Error as e:
        bot.reply_to(message, ("😿 Привет, самый крутой человек! 😿\n\n"
                    "Пожалуйста извини нас, но у нас произошла техническая ошибка. "
                    "Мы уже чиним её нашими лапками. 🔧"))
        print(e)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="12 часов", callback_data='12h'))
    keyboard.add(types.InlineKeyboardButton(text="1 день", callback_data='24h'))
    keyboard.add(types.InlineKeyboardButton(text="3 дня", callback_data='3d'))
    keyboard.add(types.InlineKeyboardButton(text="7 дней", callback_data='7d'))
    bot.send_message(message.chat.id, "Выберите, раз во сколько времени Вам будет отправляться котик.", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, text='Изменения внесены.')
    if call.data == '12h':
        cursor.execute(f"UPDATE `users` SET time = '12h' WHERE cid = {call.message.chat.id}")
        conn.commit()
    elif call.data == '24h':
        cursor.execute(f"UPDATE `users` SET time = '24h' WHERE cid = {call.message.chat.id}")
        conn.commit()
    elif call.data == '3d':
        cursor.execute(f"UPDATE `users` SET time = '3d' WHERE cid = {call.message.chat.id}")
        conn.commit()
    elif call.data == '7d':
        cursor.execute(f"UPDATE `users` SET time = '7d' WHERE cid = {call.message.chat.id}")
        conn.commit()
    bot.send_message(call.message.chat.id, "Изменения внесены.")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

cursor.execute(f"SELECT cid FROM `users`")
users = cursor.fetchall()
i = 0

while i < len(users):
    bot.send_message(users[i][0], "Бот снова в сети! Мы продолжаем рассылать котиков!")
    i += 1

bot.infinity_polling()