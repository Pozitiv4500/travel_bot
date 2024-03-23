from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

Location_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button = types.KeyboardButton(text="Отправить мою локацию", request_location=True)
Location_keyboard.add(button)

MainMenu = types.InlineKeyboardMarkup(row_width=2)
# Добавляем кнопку "Управление путешествием" с соответствующим смайликом
manage_travel_button = types.InlineKeyboardButton(text="Управление путешествием 🌍", callback_data="manage_travel")
MainMenu.add(manage_travel_button)
# Добавляем кнопку "Заметки к путешествию" с соответствующим смайликом
travel_notes_button = types.InlineKeyboardButton(text="Заметки к путешествию 📝", callback_data="travel_notes")
MainMenu.add(travel_notes_button)
# Добавляем кнопку "Путешествия с друзьями" с соответствующим смайликом
travel_with_friends_button = types.InlineKeyboardButton(text="Путешествия с друзьями 👫",callback_data="travel_with_friends")
MainMenu.add(travel_with_friends_button)
# Добавляем кнопку "Прокладывание маршрута путешествия" с соответствующим смайликом
plan_travel_route_button = types.InlineKeyboardButton(text="Прокладывание маршрута путешествия 🗺️",callback_data="plan_travel_route")
MainMenu.add(plan_travel_route_button)
edit_profile_button = types.InlineKeyboardButton(text="Редактировать информацию о себе ✏️", callback_data="edit_profile")
MainMenu.add(edit_profile_button)

manage_travel_menu = types.InlineKeyboardMarkup(row_width=1)
manage_travel_menu.add(
    types.InlineKeyboardButton("Создать новое путешествие 🌍", callback_data="create_trip"),
    types.InlineKeyboardButton("Посмотреть список путешествий 📋", callback_data="list_trips"),
    types.InlineKeyboardButton("Редактировать путешествие ✏️", callback_data="edit_trip"),
    types.InlineKeyboardButton("Удалить путешествие 🗑️", callback_data="delete_trip"),
    types.InlineKeyboardButton("Назад ↩️", callback_data="show_menu")
)

change = InlineKeyboardMarkup()
button_yes = InlineKeyboardButton(text="Добавить", callback_data="add_another_point")
button_no = InlineKeyboardButton(text="Завершить", callback_data="finish_trip_creation")
change.row(button_yes, button_no)

right_city_reg = types.InlineKeyboardMarkup()
button_yes = types.InlineKeyboardButton(text="Всё верно", callback_data="city_confirm")
button_no = types.InlineKeyboardButton(text="Неверно", callback_data="city_reenter")
right_city_reg.add(button_yes, button_no)

right_city = types.InlineKeyboardMarkup()
button_yes = types.InlineKeyboardButton(text="Всё верно", callback_data="city_confirm_ch")
button_no = types.InlineKeyboardButton(text="Неверно", callback_data="city_reenter_ch")
right_city.add(button_yes, button_no)

right_city_2 = types.InlineKeyboardMarkup()
button_yes = types.InlineKeyboardButton(text="Всё верно", callback_data="city_confirm_ch_2")
button_no = types.InlineKeyboardButton(text="Неверно", callback_data="city_reenter_ch_2")
right_city_2.add(button_yes, button_no)

right_city_3 = types.InlineKeyboardMarkup()
button_yes = types.InlineKeyboardButton(text="Всё верно", callback_data="city_confirm_ch_3")
button_no = types.InlineKeyboardButton(text="Неверно", callback_data="city_reenter_ch_3")
right_city_3.add(button_yes, button_no)

back_to_menu_travels_keyboard = types.InlineKeyboardMarkup(row_width=1)
back_to_menu_travels_keyboard.add(types.InlineKeyboardButton("Назад ↩️", callback_data="manage_travel"))