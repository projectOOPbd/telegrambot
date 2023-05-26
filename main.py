from config import TOKEN
import telebot
import sqlite3
from threading import Thread
from keyboard import welcomingkeyboard
from keyboard import changekeyboard
from keyboard import keyboard
from keyboard import search_choice_keyboard

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
        bot.send_message(message.chat.id, 'Привіт! Я новий бот. Як до вас звертатись?', reply_markup=welcomingkeyboard)
    else:
        # Якщо запис існує, відправляємо вітання з іменем користувача
        full_name = result[0]
        bot.send_message(message.chat.id, f'Привіт, {full_name}! Почніть надсилати повідомлення, і я їх повторю.')

    bot.send_message(message.chat.id, 'Виберіть опцію:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callback(call):
    if call.data == 'username':
        if call.from_user.username:

            cursor.execute('INSERT INTO users (id, full_name, username) VALUES (?, ?, ?)',
                           (call.message.chat.id, call.from_user.username, call.from_user.username))
            conn.commit()
            bot.send_message(call.message.chat.id, f'Дуже приємно, {call.from_user.username}! Почніть надсилати '
                                                   f'повідомлення, і я їх повторю.')
        else:
            bot.send_message(call.message.chat.id, 'У вас відсутнє ім`я користувача. Будь ласка, введіть псевдонім:')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.register_next_step_handler(call.message, save_name)
    elif call.data == 'fullname':
        bot.send_message(call.message.chat.id, 'Введіть псевдонім:')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, save_name)
    elif call.data == "full":
        bot.send_message(call.message.chat.id, 'Введіть псевдонім:')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, update_username)
    elif call.data == "user":
        if call.from_user.username:
            cursor.execute('UPDATE users SET full_name=? WHERE id=?',
                           (call.from_user.username, call.message.chat.id))
            conn.commit()
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, f'Ваш новий псевдонім: {call.from_user.username}! Почніть надсилати '
                                                   f'повідомлення, і я їх повторю.')
        else:
            bot.send_message(call.message.chat.id, 'У вас відсутнє ім`я користувача. Будь ласка, введіть псевдонім:')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.register_next_step_handler(call.message, update_username)

    elif call.data == 'search_title':
        bot.send_message(call.message.chat.id, 'Введіть назву книги:')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, search_books_by_title_inline)
    elif call.data == 'search_author':
        bot.send_message(call.message.chat.id, 'Введіть автора книги:')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, search_books_by_author_inline)


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
        bot.send_message(message.chat.id, f'Ваш поточний псевдонім: {current_full_name}. Введіть новий псевдонім:',
                         reply_markup=changekeyboard)
        # bot.register_next_step_handler(message, update_username)
    else:
        bot.send_message(message.chat.id, 'Ви ще не маєте псевдоніму. Спочатку введіть своє ім\'я.')


def update_username(message):
    new_username = message.text

    def update_username_thread():
        cursor.execute('UPDATE users SET full_name=? WHERE id=?', (new_username, message.chat.id))
        conn.commit()
        bot.send_message(message.chat.id, f'Ваш псевдонім було оновлено тепер ви: {new_username}.')

    thread = Thread(target=update_username_thread)
    thread.start()


def search_books_by_title(title, limit):
    newcursor = conn.cursor()

    # Виконуємо запит до бази даних з обмеженням на кількість результатів
    newcursor.execute("SELECT nameBook, author, gpa, pdffile FROM book WHERE nameBook LIKE ? LIMIT ?",
                      ('%' + title + '%', limit))
    results = newcursor.fetchall()

    return results


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Шукати книгу':
        bot.send_message(message.chat.id, 'Виберіть метод пошуку:', reply_markup=search_choice_keyboard)
    else:
        # Отримуємо повне ім'я користувача з бази даних
        cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
        result = cursor.fetchone()

        if result is not None:
            full_name = result[0]
            bot.send_message(message.chat.id, f'{full_name}, ви написали: {message.text}')


def search_books(message):
    book_title = message.text

    # Виклик функції пошуку книги за назвою з обмеженням на 5 результатів
    results = search_books_by_title(book_title, 5)

    if results:
        response = ""
        for row in results:
            bookname, author, rating, pdffile = row
            response += f"Автор: {author}\nНазва: {bookname}\nРейтинг: {rating}\nПосилання на PDF: {pdffile}\n\n"

        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Книги не знайдено.")


def search_books_by_title_inline(message):
    book_title = message.text

    # Виклик функції пошуку книги за назвою з обмеженням на 5 результатів
    results = search_books_by_title(book_title, 5)

    if results:
        response = ""
        for row in results:
            bookname, author, rating, pdffile = row
            response += f"Автор: {author}\nНазва: {bookname}\nРейтинг: {rating}\nПосилання на PDF: {pdffile}\n\n"

        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Книги не знайдено.")


def search_books_by_author_inline(message):
    author = message.text

    # Виклик функції пошуку книги за автором з обмеженням на 5 результатів
    results = search_books_by_author(author, 5)

    if results:
        response = ""
        for row in results:
            bookname, author, rating, pdffile = row
            response += f"Автор: {author}\nНазва: {bookname}\nРейтинг: {rating}\nПосилання на PDF: {pdffile}\n\n"

        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Книги не знайдено.")


def search_books_by_author(author, limit):
    newcursor = conn.cursor()

    # Виконуємо запит до бази даних з обмеженням на кількість результатів
    newcursor.execute("SELECT nameBook, author, gpa, pdffile FROM book WHERE author LIKE ? LIMIT ?",
                      ('%' + author + '%', limit))
    results = newcursor.fetchall()

    return results


# Запуск бота
bot.polling()

# Закриття підключення до бази даних після завершення роботи бота
conn.close()
