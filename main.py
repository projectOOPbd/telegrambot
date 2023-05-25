from config import TOKEN
import telebot
import sqlite3
from threading import Thread

bot = telebot.TeleBot(TOKEN)

# Підключення до бази даних SQLite
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Створення таблиці користувачів, якщо її ще не існує
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT
    )
''')
conn.commit()


@bot.message_handler(commands=['start'])
def handle_start(message):
    # Перевірка, чи існує запис користувача в базі даних
    cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
    result = cursor.fetchone()

    if result is None:
        # Якщо запис відсутній, запитуємо як до користувача звертатись
        bot.send_message(message.chat.id, 'Привіт! Я новий бот. Як до вас звертатись?')
        bot.register_next_step_handler(message, save_name)
    else:
        # Якщо запис існує, відправляємо вітання з іменем користувача
        full_name = result[0]
        bot.send_message(message.chat.id, f'Привіт, {full_name}! Почніть надсилати повідомлення, і я їх повторю.')


def save_name(message):
    # Записуємо повне ім'я користувача в базу даних
    full_name = message.text
    username = message.from_user.username
    cursor.execute('INSERT INTO users (id, full_name, username) VALUES (?, ?, ?)',
                   (message.chat.id, full_name, username))
    conn.commit()
    bot.send_message(message.chat.id, f'Дуже приємно, {full_name}! Почніть надсилати повідомлення, і я їх повторю.')


@bot.message_handler(commands=['change_username'])
def handle_change_username(message):
    # Перевірка, чи існує запис користувача в базі даних
    cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
    result = cursor.fetchone()

    if result is not None:
        current_full_name = result[0]
        bot.send_message(message.chat.id, f'Ваш поточний псевдонім: {current_full_name}. Введіть новий псевдонім:')
        bot.register_next_step_handler(message, update_username)
    else:
        bot.send_message(message.chat.id, 'Ви ще не маєте псевдоніму. Спочатку введіть своє ім\'я.')


def update_username(message):
    new_username = message.text

    def update_username_thread():
        cursor.execute('UPDATE users SET full_name=? WHERE id=?', (new_username, message.chat.id))
        conn.commit()
        bot.send_message(message.chat.id, f'Ваш псевдонім було оновлено: {new_username}.')

    thread = Thread(target=update_username_thread)
    thread.start()


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Отримуємо повне ім'я користувача з бази даних
    cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
    result = cursor.fetchone()

    if result is not None:
        full_name = result[0]
        bot.send_message(message.chat.id, f'{full_name}, ви написали: {message.text}')


# Запуск бота
bot.polling()

# Закриття підключення до бази даних після завершення роботи бота
conn.close()
