from telebot import types


welcomingkeyboard = types.InlineKeyboardMarkup()

username_button = types.InlineKeyboardButton(text="По імені", callback_data="username")
fullName_button = types.InlineKeyboardButton(text="За псевдонімом", callback_data="fullname")
welcomingkeyboard.add(username_button, fullName_button)

changekeyboard = types.InlineKeyboardMarkup()

username_button = types.InlineKeyboardButton(text="По імені", callback_data="user")
fullName_button = types.InlineKeyboardButton(text="За псевдонімом", callback_data="full")
changekeyboard.add(username_button, fullName_button)

keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

searchBtn = types.KeyboardButton('Шукати книгу')
historyBtn = types.KeyboardButton('Історія переглядів')
urlBtn = types.KeyboardButton('Посилання на інший канал Телеграм')
keyboard.add(searchBtn)
keyboard.add(historyBtn, urlBtn)


search_choice_keyboard = types.InlineKeyboardMarkup()
search_choice_keyboard.row(types.InlineKeyboardButton(text='За назвою', callback_data='search_title'),
                types.InlineKeyboardButton(text='За автором', callback_data='search_author'))