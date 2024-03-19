from aiogram import types

Location_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button = types.KeyboardButton(text="Отправить мою локацию", request_location=True)
Location_keyboard.add(button)