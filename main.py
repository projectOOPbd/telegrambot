from config import TOKEN
import telebot
import sqlite3
from threading import Thread
from keyboard import *
import os
import pyodbc

bot = telebot.TeleBot(TOKEN)

server = 'DESKTOP-KTTQUC7'
database = 'libraryNULP'
user = 'sa'
password = 'fZYuM?=B9<zY5xF'

cnxn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};SERVER=' + server +
    ';DATABASE=' + database + ';ENCRYPT=yes;UID=' + user + ';PWD=' + password + ';TrustServerCertificate=yes')
datacursor = cnxn.cursor()

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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        full_name TEXT,
        search_query_1 TEXT,
        search_query_2 TEXT,
        search_query_3 TEXT,
        search_query_4 TEXT,
        search_query_5 TEXT
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
        bot.send_message(message.chat.id, 'Привіт! Я Libby - твоя кишенькова бібліотека. Як я можу до вас звертатись?',
                         reply_markup=welcomingkeyboard)
    else:
        # Якщо запис існує, відправляємо вітання з іменем користувача
        full_name = result[0]
        bot.send_message(message.chat.id, f'Привіт, {full_name}! Очікую Ваших вказівок. Виберіть опцію: ',
                         reply_markup=keyboard)


@bot.message_handler(commands=['menu'])
def handle_menu(message):
    cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
    result = cursor.fetchone()
    full_name = result[0]
    bot.send_message(message.chat.id, f'{full_name}, виберіть опцію:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_inline_callback(call):
    if call.data == 'username':
        if call.from_user.username:

            cursor.execute('INSERT INTO users (id, full_name, username) VALUES (?, ?, ?)',
                           (call.message.chat.id, call.from_user.username, call.from_user.username))
            conn.commit()
            bot.send_message(call.message.chat.id,
                             f'Дуже приємно, {call.from_user.username}! Тепер я зможу вам допомагати. Виберіть опцію:',
                             reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, 'У вас відсутнє ім`я користувача. Будь ласка, введіть псевдонім:')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.register_next_step_handler(call.message, save_name)
    elif call.data == 'fullname':
        bot.send_message(call.message.chat.id, 'Введіть бажаний псевдонім:')
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
            bot.send_message(call.message.chat.id, f'Ваш новий псевдонім: {call.from_user.username}!')
        else:
            bot.send_message(call.message.chat.id, 'У вас відсутнє ім`я користувача. Будь ласка, введіть псевдонім:')
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            bot.register_next_step_handler(call.message, update_username)

    elif call.data == 'search_title':
        cursor.execute('SELECT full_name FROM users WHERE id=?', (call.message.chat.id,))
        result = cursor.fetchone()
        full_name = result[0]
        bot.send_message(call.message.chat.id, f'{full_name}, введіть назву книги:')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, search_books_by_title_inline)
    elif call.data == 'search_author':
        cursor.execute('SELECT full_name FROM users WHERE id=?', (call.message.chat.id,))
        result = cursor.fetchone()
        full_name = result[0]
        bot.send_message(call.message.chat.id, f'{full_name}, введіть автора книги:')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, search_books_by_author_inline)


def save_name(message):
    # Записуємо повне ім'я користувача в базу даних
    full_name = message.text
    username = message.from_user.username
    cursor.execute('INSERT INTO users (id, full_name, username) VALUES (?, ?, ?)',
                   (message.chat.id, full_name, username))
    conn.commit()
    bot.send_message(message.chat.id, f'Дуже приємно, {full_name}! Тепер я готова вам допомагати.')


@bot.message_handler(commands=['change_username'])
def handle_change_username(message):
    # Перевірка, чи існує запис користувача в базі даних
    cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
    result = cursor.fetchone()

    if result is not None:
        current_full_name = result[0]
        bot.send_message(message.chat.id, f'Ваш поточний псевдонім: {current_full_name}. Введіть новий псевдонім:',
                         reply_markup=changekeyboard)
    else:
        bot.send_message(message.chat.id, 'Ви ще не маєте псевдоніму. Спочатку введіть своє ім\'я.')


def update_username(message):
    new_username = message.text

    def update_username_thread():
        cursor.execute('UPDATE users SET full_name=? WHERE id=?', (new_username, message.chat.id))
        conn.commit()
        bot.send_message(message.chat.id, f'Ваш псевдонім було оновлено, тепер я звертатимусь до вас: {new_username}.')

    thread = Thread(target=update_username_thread)
    thread.start()


def search_books_by_title(title, limit):
    newcursor = cnxn.cursor()
    title = title.title()
    # Розділяємо введений рядок на окремі слова
    keywords = title.split()

    # Формуємо рядок запиту з урахуванням кількох слів у заголовку
    query = "SELECT TOP {0} nameBook, author, gpa, fishnet, pdffile FROM book WHERE ".format(limit)
    conditions = []
    for keyword in keywords:
        conditions.append("nameBook LIKE ?")
    query += " OR ".join(conditions)

    # Створюємо список параметрів для запиту
    params = ['%' + keyword + '%' for keyword in keywords]

    # Виконуємо запит до бази даних
    newcursor.execute(query, params)
    results = newcursor.fetchall()

    return results


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
    result = cursor.fetchone()
    full_name = result[0]
    if message.text == 'Шукати книгу':
        bot.send_message(message.chat.id, f'{full_name}, виберіть метод пошуку:', reply_markup=search_choice_keyboard)
    elif message.text == 'Історія переглядів':
        show_search_history(message)
    elif message.text == "Посилання для навчання":
        bot.send_message(message.chat.id, f'{full_name}, ось корисні посилання для Вас:', reply_markup=urlkeyboard)
    elif message.text == 'Оцінити книгу':
        set_book_rating(message)
    else:
        # Отримуємо повне ім'я користувача з бази даних
        cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
        result = cursor.fetchone()

        if result is not None:
            full_name = result[0]
            bot.send_message(message.chat.id,
                             f'{full_name}, ви написали: {message.text}, '
                             f'я не ChatGPT і не можу розпізнати таку команду')


def search_books(message):
    book_title = message.text

    # Виклик функції пошуку книги за назвою з обмеженням на 5 результатів
    results = search_books_by_title(book_title, 5)

    if results:
        response = ""
        for row in results:
            book, author, rating, pdffile = row
            response += f"Автор: {author}\nНазва: {book}\nРейтинг: {rating}\nПосилання на PDF: {pdffile}\n\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "На жаль я не змогла знайти книгу.")


def search_books_by_title_inline(message):
    book_title = message.text

    # Виклик функції пошуку книги за назвою з обмеженням на 5 результатів
    results = search_books_by_title(book_title, 5)
    board = telebot.types.InlineKeyboardMarkup()
    temp_file_path = ''
    if results:
        response = ""
        for row in results:
            bookname, author, rating, fishnet, pdffile = row
            response += f"Автор: {author}\nНазва: {bookname}\nРейтинг: {rating}\n\n"
            cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
            result = cursor.fetchone()
            full_name = result[0]
            link = f'{fishnet}'
            update_search_history(message.chat.id, full_name, bookname)
            temp_file_path = f'{bookname}.pdf'
            with open(temp_file_path, 'wb') as file:
                file.write(pdffile)
            button = telebot.types.InlineKeyboardButton(text='Посилання', url=link)
            board.add(button)

        with open(temp_file_path, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=response, reply_markup=board)
        os.remove(temp_file_path)

    else:
        bot.send_message(message.chat.id, "На жаль я не змогла знайти книгу.")


def search_books_by_author_inline(message):
    author = message.text
    temp_file_path = ''
    # Виклик функції пошуку книги за автором з обмеженням на 5 результатів
    results = search_books_by_author(author, 5)
    board = telebot.types.InlineKeyboardMarkup()
    if results:
        response = ""
        for row in results:
            bookname, author, rating, fishnet, pdffile = row
            response += f"Автор: {author}\nНазва: {bookname}\nРейтинг: {rating}\n\n"
            cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
            link = f'{fishnet}'
            result = cursor.fetchone()
            full_name = result[0]
            update_search_history(message.chat.id, full_name, bookname)
            temp_file_path = f'{bookname}.pdf'
            with open(temp_file_path, 'wb') as file:
                file.write(pdffile)
            button = telebot.types.InlineKeyboardButton(text='Посилання', url=link)
            board.add(button)

        with open(temp_file_path, 'rb') as file:
            bot.send_document(message.chat.id, file, caption=response, reply_markup=board)
        os.remove(temp_file_path)
    else:
        bot.send_message(message.chat.id, "На жаль я не змогла знайти книгу.")


def search_books_by_author(author, limit):
    newcursor = cnxn.cursor()
    author = author.title()
    # Розділяємо введений рядок на окремі слова
    keywords = author.split()
    # Формуємо рядок запиту з урахуванням кількох слів у заголовку
    query = "SELECT TOP {0} nameBook, author, gpa, fishnet, pdffile FROM book WHERE ".format(limit)
    conditions = []
    for keyword in keywords:
        conditions.append("author LIKE ?")
    query += " OR ".join(conditions)
    # Створюємо список параметрів для запиту
    params = ['%' + keyword + '%' for keyword in keywords]
    # Виконуємо запит до бази даних
    newcursor.execute(query, params)
    results = newcursor.fetchall()

    return results


def update_search_history(user_id, full_name, search_query):
    cursor.execute('SELECT * FROM search_history WHERE user_id=?', (user_id,))
    result = cursor.fetchone()

    if result is None:
        # Якщо запис відсутній, вставляємо новий запис
        cursor.execute('''
            INSERT INTO search_history (user_id, full_name, search_query_1)
            VALUES (?, ?, ?)
        ''', (user_id, full_name, search_query))
    else:
        query1 = search_query
        query2 = result[3]
        query3 = result[4]
        query4 = result[5]
        query5 = result[6]
        cursor.execute('''
            UPDATE search_history
            SET search_query_1=?, search_query_2=?, search_query_3=?, search_query_4=?, search_query_5=?
            WHERE user_id=?
        ''', (query1, query2, query3, query4, query5, user_id))

    conn.commit()


def show_search_history(message):
    # Отримуємо повне ім'я користувача з бази даних
    cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
    result = cursor.fetchone()
    temp_file_path = ''
    if result is not None:
        full_name = result[0]

        # Отримуємо всі запити користувача зі збереженої історії
        cursor.execute('SELECT search_query_1, search_query_2, search_query_3, search_query_4, search_query_5 '
                       'FROM search_history WHERE user_id=?', (message.chat.id,))
        result = cursor.fetchone()

        if result is not None:
            queries = list(result)  # Конвертуємо результат у список

            # Видаляємо повторюючіся запити
            unique_queries = list(set(queries))
            unique_queries = [q for q in unique_queries if q is not None]  # Видаляємо пусті запити
            cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
            result = cursor.fetchone()
            full_name = result[0]

            if unique_queries:
                responsefor = f"{full_name}, ось ваша історія переглядів:\n\n"
                bot.send_message(message.chat.id, responsefor)
                for query in unique_queries:
                    result = search_books_by_title(query, 1)
                    if result:
                        response = ""
                        board = telebot.types.InlineKeyboardMarkup(row_width=1)
                        for row in result:
                            bookname, author, rating, pdffile, binary = row
                            response += f"Автор: {author}\nНазва: {bookname}\nРейтинг: {rating}\n\n"
                            link = f'{pdffile}'
                            temp_file_path = f'{bookname}.pdf'
                            with open(temp_file_path, 'wb') as file:
                                file.write(binary)
                            button = telebot.types.InlineKeyboardButton(text='Посилання', url=link)
                            board.add(button)

                        with open(temp_file_path, 'rb') as file:
                            bot.send_document(message.chat.id, file, caption=response, reply_markup=board)
                        os.remove(temp_file_path)
            else:
                bot.send_message(message.chat.id, f"{full_name}, на даний момент Ваша історія пошуків порожня.")

        else:
            bot.send_message(message.chat.id, f"{full_name}, на даний момент Ваша історія пошуків порожня.")
    else:
        bot.send_message(message.chat.id, "Спочатку введіть своє ім'я.")


def set_book_rating(message):
    chat_id = message.chat.id
    cursor.execute('SELECT full_name FROM users WHERE id=?', (message.chat.id,))
    result = cursor.fetchone()
    full_name = result[0]
    # Отримання імені книги від користувача
    bot.send_message(chat_id, f"{full_name}, введіть назву книги, яку бажаєте оцінити:")
    bot.register_next_step_handler(message, process_book_name)


def process_book_name(message):
    chat_id = message.chat.id
    book_name = message.text

    # Перевірка, чи існує книга з таким ім'ям у базі даних
    datacursor.execute("SELECT * FROM book WHERE nameBook=?", (book_name,))
    book = datacursor.fetchone()
    if book:
        # Отримання рейтингу від користувача
        bot.send_message(chat_id, "Введіть рейтинг книги у числовому форматі від 1 до 10:")
        bot.register_next_step_handler(message, process_rating, book_name)
    else:
        response = "Книга з таким іменем не знайдена."
        bot.send_message(chat_id, response)


def process_rating(message, book_name):
    chat_id = message.chat.id
    rating = float(message.text)

    if 0 <= rating <= 10:
        # Оновлення рейтингу книги в базі даних
        datacursor.execute('UPDATE book SET gpa=? WHERE nameBook=?', (rating, book_name))
        cnxn.commit()  # Зберегти зміни у базі даних

        response = "Рейтинг книги: {} було оновлено на {}".format(book_name, rating)
        bot.send_message(chat_id, response)
    else:
        response = "Рейтинг повинен бути від 0 до 10. Введіть рейтинг ще раз:"
        bot.send_message(chat_id, response)
        bot.register_next_step_handler(message, process_rating, book_name)


# Запуск бота
bot.polling()

# Закриття підключення до бази даних після завершення роботи бота
conn.close()
cnxn.close()
