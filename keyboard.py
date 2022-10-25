from aiogram import types


menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    types.KeyboardButton('Language'),
    types.KeyboardButton('Help'),
)

adm = types.ReplyKeyboardMarkup(resize_keyboard=True)
adm.add(
    types.KeyboardButton('Blacklist'),
    types.KeyboardButton('Add to blacklist'),
    types.KeyboardButton('Remove from blacklist'),
    types.KeyboardButton('Bulk messaging'),
    types.KeyboardButton('Back to main menu'),
)


back = types.ReplyKeyboardMarkup(resize_keyboard=True)
back.add(
    types.KeyboardButton('Cancel')
)

lang = types.InlineKeyboardMarkup(row_width=2)
lang.add(
    types.InlineKeyboardButton(text='Ukrainian',
                               callback_data='set_lang_Ukrainian'),
    types.InlineKeyboardButton(text='English',
                               callback_data='set_lang_English'),
)
