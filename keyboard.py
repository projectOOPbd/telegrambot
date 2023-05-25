from telebot import types


welcomingkeyboard = types.InlineKeyboardMarkup()

username_button = types.InlineKeyboardButton(text="По імені", callback_data="username")
fullName_button = types.InlineKeyboardButton(text="За псевдонімом", callback_data="fullname")
welcomingkeyboard.add(username_button, fullName_button)
