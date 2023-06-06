from telebot import types

welcomingkeyboard = types.InlineKeyboardMarkup()

username_button = types.InlineKeyboardButton(text="По імені", callback_data="username")
fullName_button = types.InlineKeyboardButton(text="За псевдонімом", callback_data="fullname")
welcomingkeyboard.add(username_button, fullName_button)

changekeyboard = types.InlineKeyboardMarkup()

username_button = types.InlineKeyboardButton(text="По імені", callback_data="user")
fullName_button = types.InlineKeyboardButton(text="За псевдонімом", callback_data="full")
changekeyboard.add(username_button, fullName_button)

keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

searchBtn = types.KeyboardButton('Шукати книгу')
historyBtn = types.KeyboardButton('Історія переглядів')
urlBtn = types.KeyboardButton('Посилання для навчання')
rateBtn = types.KeyboardButton('Оцінити книгу')
keyboard.add(searchBtn)
keyboard.add(historyBtn, urlBtn, rateBtn)

search_choice_keyboard = types.InlineKeyboardMarkup()
search_choice_keyboard.row(types.InlineKeyboardButton(text='За назвою', callback_data='search_title'),
                           types.InlineKeyboardButton(text='За автором', callback_data='search_author'))

urlkeyboard = types.InlineKeyboardMarkup(row_width=1)

vnsurl=types.InlineKeyboardButton(text= 'Внутрішнє начальне середовище', url='https://vns.lpnu.ua/login/index.php')
boturl=types.InlineKeyboardButton(text='Розклад LPNU', url='https://t.me/nulp_pro_bot')
urlkeyboard.add(boturl, vnsurl)
