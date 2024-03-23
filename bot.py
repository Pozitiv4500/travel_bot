import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from geopy import Location

from keyboards import Location_keyboard, MainMenu, manage_travel_menu, change, right_city, right_city_2, \
    back_to_menu_travels_keyboard, right_city_3, right_city_reg
from geopy.geocoders import Nominatim


from config import BOT_TOKEN
from messages import welcome_message
from models import db_start, create_profile, check_user_exists, edit_profile, create_trip_db, create_location, \
    check_trip_existence, get_user_trips_with_locations, format_trip_message, get_user_data, edit_trip_mod, \
    add_trip_point, get_user_trip_names, get_trip_points, delete_trip_point_by_id, delete_trip_by_id, \
    add_friend_to_trip, get_joined_trips_info, get_friends_trips_names, get_user_trip_names_format

from statesform import Registration, ChangeUser, MakeTravel, EditTravel, AddPoints, AddUserToTrip

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Устанавливаем токен вашего бота


# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot,storage=MemoryStorage())

geolocator = Nominatim(user_agent="travel_bot",timeout=20)

async def on_startup(_):
    await db_start()




# Хэндлер на сообщения с возрастом пользователя
@dp.message_handler(commands=['start'])
async def process_age(message: types.Message):
    # Получаем имя пользователя из профиля
    if await check_user_exists(message.from_user.id):
        await message.answer(welcome_message, reply_markup=MainMenu)
    else:
        name = message.from_user.full_name
        await message.reply(
            f"Доброго полудня, {name}! Я помогу тебе организовать твоё путешествие. Для начала давай узнаем о тебе немного больше.")
        await message.answer(f"Сколько тебе лет? (Введите ваш возраст)")
        await Registration.Age.set()

# Хэндлер на сообщения с возрастом пользователя
@dp.message_handler(state=Registration.Age)
async def request_location(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)  # Сохраняем возраст пользователя в состоянии
        await state.set_state(Registration.Location)
        await message.reply("Пожалуйста, нажмите на кнопку ниже, чтобы отправить вашу текущую локацию или введите название вашего населенного пункта вручную.", reply_markup=Location_keyboard)

    except ValueError:
        await message.reply("Пожалуйста, напишите цифрами ваш возраст")



# Хэндлер на сообщения с городом пользователя или запрос локации
@dp.message_handler(content_types=[types.ContentType.LOCATION, types.ContentType.TEXT], state=Registration.Location)
async def process_city_or_location(message: types.Message, state: FSMContext):

    if message.content_type == types.ContentType.LOCATION:
        # Если пользователь отправил локацию, сохраняем её и завершаем регистрацию
        latitude = message.location.latitude
        longitude = message.location.longitude

        location = geolocator.reverse((latitude, longitude), language='ru')
        location_name = location.address if location else "Неизвестно"

        await state.update_data(latitude=latitude, longitude=longitude, location=location_name)
        await state.set_state(Registration.ConfirmLocation)  # Завершаем текущее состояние
        await confirm_city_already(message,state)

    else:
        # Если пользователь отправил текст, проверяем, является ли он названием города
        city = message.text
        location = geolocator.geocode(city)
        if location:
            latitude = location.latitude
            longitude = location.longitude


            await state.update_data(latitude=latitude, longitude=longitude, location = location.address)

            await state.set_state(Registration.ConfirmLocation)
            await message.reply(f"Это ваш населенный пункт? {location}", reply_markup=right_city_reg)
        else:
            # Город не найден, отправляем сообщение с кнопками "Всё верно" и "Наверное"
            await message.reply("Ваш населенный пункт не найден. Пожалуйста, попробуйте ввести название вашего населенного пункта ещё раз.")

async def confirm_city_already(message, state: FSMContext):

    # Сохраняем профиль пользователя в базе данных
    user_data = await state.get_data()
    user_id = message.from_user.id
    age = user_data.get('age')
    latitude = user_data.get('latitude')
    longitude = user_data.get('longitude')
    bio = user_data.get('bio')
    location = user_data.get('location')
    username = message.from_user.username  # Получаем имя пользователя
    await create_profile(user_id, age, location, latitude, longitude, bio, username)
    await message.answer("Спасибо за предоставленную информацию!")
    await state.finish()
    await show_menu(message)

# Хэндлер для кнопки "Всё верно"
@dp.callback_query_handler(lambda c: c.data == 'city_confirm', state=Registration.ConfirmLocation)
async def confirm_city(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Registration.Bio)  # Завершаем текущее состояние
    await callback_query.message.edit_text(
        "Пожалуйста, расскажите нам немного о себе! Напишите немного о себе: кем вы являетесь, чем увлекаетесь, какие у вас интересы?")  # Изменяем сообщение с подтверждением


# Хэндлер для кнопки "Наверное"
@dp.callback_query_handler(lambda c: c.data == 'city_reenter', state=Registration.ConfirmLocation)
async def reenter_city(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "Пожалуйста, введите название вашего населенного пункта ещё раз.")  # Изменяем сообщение с приглашением ввести название пункта ещё раз
    await state.set_state(Registration.Location)


# Хэндлер на сообщения с биографией пользователя
@dp.message_handler(state=Registration.Bio)
async def process_bio(message: types.Message, state: FSMContext):
    bio = message.text
    await state.update_data(bio=bio)  # Сохраняем биографию пользователя в состоянии

    # Сохраняем профиль пользователя в базе данных
    user_data = await state.get_data()
    user_id = message.from_user.id
    age = user_data.get('age')
    latitude = user_data.get('latitude')
    longitude = user_data.get('longitude')
    bio = user_data.get('bio')
    location = user_data.get('location')
    username = message.from_user.username  # Получаем имя пользователя
    await create_profile(user_id, age, location, latitude, longitude, bio, username)
    await message.reply("Спасибо за предоставленную информацию!")
    await state.finish()
    await show_menu(message)

# Хэндлер для кнопки "Наверное"
@dp.callback_query_handler(lambda c: c.data == 'city_reenter', state=Registration.ConfirmLocation)
async def reenter_city(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Пожалуйста, введите название вашего населенного пункта ещё раз.")  # Изменяем сообщение с приглашением ввести название пункта ещё раз
    await state.set_state(Registration.Location)

# Хэндлер на сообщения с биографией пользователя



# Хэндлер для команды /menu
@dp.message_handler()
async def show_menu(message: types.Message):
    if await check_user_exists(message.from_user.id):
        await message.answer(welcome_message, reply_markup=MainMenu)
    else:
        await process_age(message)


@dp.callback_query_handler(lambda callback_query: callback_query.data == "show_menu")
async def callback_show_menu(callback_query: types.CallbackQuery):


    await callback_query.message.edit_text(welcome_message, reply_markup=MainMenu)

#редактирование профиля ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'edit_profile')
async def edit_profile_user(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = await get_user_data(user_id)
    if user_data:
        location = f"Местоположение: {user_data['home_name']}"
        age = f"Возраст: {user_data['age']}"
        bio = f"Информация о себе: {user_data['bio']}"
    else:
        location = "Местоположение не указано"
        age = "Возраст не указан"
        bio = "Информация о себе не указана"

    await callback_query.message.edit_text(
        "Здесь вы можете изменить ваш профиль 😊\n"
        "Выберите, что вы хотите изменить:\n\n"
        f"{location}\n{age}\n{bio}",
        reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton("Изменить местоположение 📍", callback_data="edit_location"),
            types.InlineKeyboardButton("Изменить возраст 🎂", callback_data="edit_age"),
            types.InlineKeyboardButton("Изменить информацию о себе 📝", callback_data="edit_bio"),
            types.InlineKeyboardButton("Назад ↩️", callback_data="show_menu")
        )
    )

async def edit_profile_r(message):
    user_id = message.from_user.id

    user_data = await get_user_data(user_id)
    if user_data:
        location = f"Местоположение: {user_data['home_name']}"
        age = f"Возраст: {user_data['age']}"
        bio = f"Информация о себе: {user_data['bio']}"
    else:
        location = "Местоположение не указано"
        age = "Возраст не указан"
        bio = "Информация о себе не указана"
    if isinstance(message, types.CallbackQuery):
        await message.message.answer(
            "Здесь вы можете изменить ваш профиль 😊\n"
            "Выберите, что вы хотите изменить:\n\n"
            f"{location}\n{age}\n{bio}",
            reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton("Изменить местоположение 📍", callback_data="edit_location"),
                types.InlineKeyboardButton("Изменить возраст 🎂", callback_data="edit_age"),
                types.InlineKeyboardButton("Изменить информацию о себе 📝", callback_data="edit_bio"),
                types.InlineKeyboardButton("Назад ↩️", callback_data="show_menu")
            )
        )
    else:
        await message.answer(
            "Здесь вы можете изменить ваш профиль 😊\n"
            "Выберите, что вы хотите изменить:\n\n"
            f"{location}\n{age}\n{bio}",
            reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                types.InlineKeyboardButton("Изменить местоположение 📍", callback_data="edit_location"),
                types.InlineKeyboardButton("Изменить возраст 🎂", callback_data="edit_age"),
                types.InlineKeyboardButton("Изменить информацию о себе 📝", callback_data="edit_bio"),
                types.InlineKeyboardButton("Назад ↩️", callback_data="show_menu")
            )
        )

@dp.callback_query_handler(lambda callback_query: callback_query.data == "edit_location")
async def edit_location(callback_query: types.CallbackQuery):
    await ChangeUser.Location.set()
    await callback_query.message.answer(
        "Чтобы обновить ваше местоположение, нажмите на кнопку ниже или введите название вашего населенного пункта вручную 📍",
        reply_markup=Location_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == "edit_age")
async def edit_age(callback_query: types.CallbackQuery):
    await ChangeUser.Age.set()
    await callback_query.message.edit_text("Отправьте ваш новый возраст 🎂")

@dp.callback_query_handler(lambda callback_query: callback_query.data == "edit_bio")
async def edit_bio(callback_query: types.CallbackQuery):
    await ChangeUser.Bio.set()
    await callback_query.message.edit_text("Расскажите нам немного о себе: кем вы являетесь, чем увлекаетесь, какие у вас интересы? 📝")


#редактирование местоположения
@dp.message_handler(content_types=[types.ContentType.LOCATION, types.ContentType.TEXT], state=ChangeUser.Location)
async def process_city_or_location(message: types.Message, state: FSMContext):

    if message.content_type == types.ContentType.LOCATION:
        # Если пользователь отправил локацию, сохраняем её и завершаем регистрацию
        latitude = message.location.latitude
        longitude = message.location.longitude

        location = geolocator.reverse((latitude, longitude), language='ru')
        await edit_profile(message.from_user.id, home_name=location, latitude=latitude, longitude=longitude)

        await message.reply("Местоположение успешно обновлено! 📍")

        await edit_profile_r(message)
        await state.finish()
    else:
        # Если пользователь отправил текст, проверяем, является ли он названием города
        city = message.text
        location = geolocator.geocode(city)
        if location:
            latitude = location.latitude
            longitude = location.longitude


            await state.update_data(latitude=latitude, longitude=longitude, id = message.from_user.id, location = location)
            await state.set_state(ChangeUser.Final)
            await message.reply(f"Это ваше местоположение? {location}", reply_markup=right_city)
        else:
            # Город не найден, отправляем сообщение с кнопками "Всё верно" и "Наверное"
            await message.reply("Ваше местоположение не найдено. Пожалуйста, попробуйте ввести ваше местоположение ещё раз.")


# Обработка текстовых сообщений для редактирования профиля
@dp.callback_query_handler(lambda c: c.data == "city_confirm_ch", state=ChangeUser.Final)
async def process_location(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    home_name = data.get('location')
    id = data.get('id')
    await edit_profile(id, home_name=home_name,latitude=latitude, longitude=longitude)
    await callback_query.message.answer("Местоположение успешно обновлено! 📍")
    await edit_profile_r(callback_query)
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'city_reenter_ch', state=ChangeUser.Final)
async def process_location_not(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Пожалуйста, введите ваше местоположение ещё раз.")  # Изменяем сообщение с приглашением ввести название пункта ещё раз
    await state.set_state(ChangeUser.Location)

@dp.message_handler(state=ChangeUser.Age)
async def process_age_state(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        await edit_profile(message.from_user.id, age=age)
        await message.reply("Возраст успешно обновлен! 🎂")
        await edit_profile_r(message)
        await state.finish()
    except ValueError:
        await message.reply("Пожалуйста, напишите цифрами ваш возраст")


@dp.message_handler(state=ChangeUser.Bio)
async def process_bio(message: types.Message, state: FSMContext):
    bio = message.text
    await edit_profile(message.from_user.id, bio=bio)
    await message.reply("Информация о себе успешно обновлена! 📝")
    await edit_profile_r(message)
    await state.finish()


# Обработчик для кнопки "Управление путешествием"-------------------------------------------------------------------------------------------------------------------------------
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'manage_travel')
async def manage_travel(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Добро пожаловать в управление путешествиями! 🌟\n\nЗдесь вы можете создавать новые путешествия, просматривать список уже запланированных приключений, редактировать детали каждого путешествия и даже удалить те, которые уже завершились. Приятного путешествия! ✈️🚗🚀",reply_markup=manage_travel_menu)


async def manage_travel_mess(message: types.Message):
    await message.answer("Добро пожаловать в управление путешествиями! 🌟\n\nЗдесь вы можете создавать новые путешествия, просматривать список уже запланированных приключений, редактировать детали каждого путешествия и даже удалить те, которые уже завершились. Приятного путешествия! ✈️🚗🚀",reply_markup=manage_travel_menu)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'create_trip')
async def create_trip(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали создание нового путешествия. Пожалуйста, введите название путешествия:")
    await MakeTravel.Name.set()


@dp.callback_query_handler(lambda c: c.data == 'delete_trip')
async def delete_trip(callback_query: types.CallbackQuery):
    # Получаем идентификатор пользователя
    user_id = callback_query.from_user.id
    trips_data = await get_user_trips_with_locations(user_id)

    # Получаем список имен путешествий пользователя
    trip_names = await get_user_trip_names(user_id)
    trip_ids = [trip['trip_id'] for trip in trips_data]

    if not trip_names:
        await callback_query.message.edit_text("У вас пока нет созданных путешествий.",
                                               reply_markup=back_to_menu_travels_keyboard)
        return

    # Создаем список кнопок для каждого путешествия
    buttons = []

    for trip_id, trip_name in zip(trip_ids, trip_names):
        buttons.append(types.InlineKeyboardButton(trip_name, callback_data=f"delete_trip_{trip_id}"))

    trip_message = await format_trip_message(trips_data)
    # Отправляем сообщение с информацией о путешествиях и кнопками для удаления путешествия
    await callback_query.message.edit_text(trip_message, reply_markup=types.InlineKeyboardMarkup().add(*buttons).add(
        types.InlineKeyboardButton("Назад ↩️", callback_data="manage_travel")))

    # Ответим на колбэк, чтобы убрать кружок ожидания
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('delete_trip_'))
async def delete_trip(callback_query: types.CallbackQuery):
    # Получаем идентификатор путешествия из данных коллбэка
    trip_id = callback_query.data.split('_')[2]

    # Удаляем путешествие с указанным trip_id
    await delete_trip_by_id(trip_id)

    # Подтверждаем удаление путешествия с пользователем
    await callback_query.message.edit_text(f"Путешествие удалено успешно.")

    # Ответим на колбэк, чтобы убрать кружок ожидания
    await callback_query.answer()
    await manage_travel_mess(callback_query.message)
@dp.message_handler(state=MakeTravel.Name)
async def process_trip_name(message: types.Message, state: FSMContext):
    trip_name = message.text
    await state.update_data(trip_name=trip_name)

    trip_exists = await check_trip_existence(trip_name)
    if trip_exists:
        await message.reply("Такое путешествие уже существует, попробуйте другое название, пожалуйста.")
    else:
        # После ввода названия путешествия, переходим к вводу первой точки
        await message.reply("Пожалуйста, введите первую точку путешествия:")
        await MakeTravel.Points.set()

@dp.message_handler(state=MakeTravel.Points)
async def process_trip_point(message: types.Message, state: FSMContext):
    # Получаем список точек путешествия из состояния
    data = await state.get_data()

    points = data.get('points', [])

    # Определение координат по названию местоположения
    location = message.text

    location_info = geolocator.geocode(location)
    if location_info:
        latitude = location_info.latitude
        longitude = location_info.longitude


        # Добавляем новую точку путешествия
        points.append((location_info, latitude, longitude))
        await state.update_data(points=points)

        await message.reply(f"Это ваша точка маршрута? {location_info}", reply_markup=right_city_2)
        # await message.reply("Точка путешествия успешно добавлена! 📍 Хотите добавить еще одну?", reply_markup=change)

        # Переходим в состояние ожидания ответа на вопрос о добавлении еще одной точки
        await MakeTravel.Okey_city.set()
    else:
        await message.reply(
            "Указанное местоположение не найдено. Пожалуйста, попробуйте ввести местоположение ещё раз.")

@dp.callback_query_handler(lambda c: c.data == "city_confirm_ch_2", state=MakeTravel.Okey_city)
async def process_location(callback_query: CallbackQuery, state: FSMContext):
    # await callback_query.message.edit_text("Точка путешествия успешно добавлена! 📍")
    await callback_query.message.edit_text("Пожалуйста, введите время начала посещения в формате ГГГГ-ММ-ДД (например, 2024-03-20):")
    await MakeTravel.StartDate.set()

@dp.callback_query_handler(lambda c: c.data == 'city_reenter_ch_2', state=MakeTravel.Okey_city)
async def process_location_not(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    points = data.get('points', [])

    points.pop(len(points) - 1)
    await state.update_data(points=points)
    await callback_query.message.edit_text("Пожалуйста, введите вашу точку маршрута ещё раз.")  # Изменяем сообщение с приглашением ввести название пункта ещё раз
    await state.set_state(MakeTravel.Points)

@dp.message_handler(state=MakeTravel.StartDate)
async def process_start_date(message: types.Message, state: FSMContext):
    start_date_text = message.text.strip()
    try:
        start_date = datetime.strptime(start_date_text, "%Y-%m-%d").date()
    except ValueError:
        await message.reply("Некорректный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД (например, 2024-03-20):")
        return

    await state.update_data(start_date=start_date)
    await message.reply("Пожалуйста, введите время окончания посещения в формате ГГГГ-ММ-ДД (например, 2024-03-25):")
    await MakeTravel.EndDate.set()
@dp.message_handler(state=MakeTravel.EndDate)
async def process_end_date(message: types.Message, state: FSMContext):
    end_date_text = message.text.strip()
    try:
        end_date = datetime.strptime(end_date_text, "%Y-%m-%d").date()
    except ValueError:
        await message.reply("Некорректный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД (например, 2024-03-25):")
        return

    data = await state.get_data()
    trip_name = data.get('trip_name')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    start_date = data.get('start_date')
    visit_date = start_date
    visit_end = end_date

    # Получаем список точек путешествия из состояния и редактируем последний объект
    points = data.get('points', [])
    last_point = points[-1]  # Получаем последнюю точку из списка
    updated_last_point = (*last_point, start_date, end_date)  # Добавляем время начала и окончания
    points[-1] = updated_last_point  # Обновляем последнюю точку в списке
    await state.update_data(points=points)

    await message.reply("Время начала и окончания путешествия успешно установлено!\nХотите добавить еще одну точку или завершить создание путешествия?", reply_markup=change)
    await MakeTravel.MorePoints.set()
@dp.callback_query_handler(lambda c: c.data == 'add_another_point', state=MakeTravel.MorePoints)
async def process_add_another_point(callback_query: CallbackQuery, state: FSMContext):
    # Если пользователь хочет добавить еще одну точку, переходим к вводу
    await callback_query.message.edit_text("Пожалуйста, введите следующую точку путешествия:")
    await state.set_state(MakeTravel.Points)

@dp.callback_query_handler(lambda c: c.data == 'finish_trip_creation', state=MakeTravel.MorePoints)
async def process_finish_trip_creation(callback_query: CallbackQuery, state: FSMContext):
    # Если пользователь больше не хочет добавлять точки, завершаем создание путешествия
    data = await state.get_data()
    trip_name = data.get('trip_name')
    points = data.get('points', [])

    await create_trip_db(callback_query.from_user.id, trip_name)

    # Создание записей о локациях в базе данных
    for point in points:
        location_name, latitude, longitude, start_date, end_date = point
        location_str = location_name.address if isinstance(location_name, Location) else location_name
        await create_location(trip_name, location_str, latitude, longitude, start_date, end_date)

    await callback_query.message.edit_text(f"Путешествие '{trip_name}' успешно создано! 🎉")
    await manage_travel_mess(callback_query.message)
    await state.finish()
#редактирование поездки
@dp.callback_query_handler(lambda c: c.data == 'edit_trip')
async def edit_trip(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # Получаем список путешествий пользователя
    trips_data = await get_user_trips_with_locations(user_id)


    if not trips_data:
        await callback_query.message.edit_text("У вас пока нет созданных путешествий.", reply_markup=back_to_menu_travels_keyboard)
        return

    # Создаем множество уникальных идентификаторов путешествий
    unique_trip_ids = set(trip['trip_id'] for trip in trips_data)

    # Создаем список кнопок для каждого уникального путешествия
    buttons = []
    for trip_id in unique_trip_ids:
        # Находим соответствующее путешествие по его идентификатору
        trip = next((t for t in trips_data if t['trip_id'] == trip_id), None)
        if trip:
            buttons.append(types.InlineKeyboardButton(trip['trip_name'], callback_data=f"edit-trip_{trip['trip_id']}"))

    # Формируем сообщение о путешествиях пользователя
    trip_message = await format_trip_message(trips_data)

    # Отправляем сообщение с информацией о путешествиях и кнопками для выбора путешествия для редактирования
    await callback_query.message.edit_text(trip_message, reply_markup=types.InlineKeyboardMarkup().add(*buttons).add(types.InlineKeyboardButton("Назад ↩️", callback_data="manage_travel")))

    # Ответим на колбэк, чтобы убрать кружок ожидания
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('edit-trip_'))
async def edit_trip(callback_query: types.CallbackQuery):
    # Разбираем данные обратного вызова
    callback_data_parts = callback_query.data.split('_')
    if len(callback_data_parts) != 2:
        await callback_query.answer("Ошибка: неверный формат идентификатора путешествия")
        return

    _, trip_id = callback_data_parts
    print(trip_id)
    # Далее ваша логика обработки идентификатора путешествия

    # Создаем клавиатуру с кнопками для редактирования путешествия
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Редактировать название путешествия", callback_data=f"edit_trip_name_{trip_id}"),
        types.InlineKeyboardButton("Редактировать описание путешествия", callback_data=f"edit_trip_description_{trip_id}"),
        types.InlineKeyboardButton("Добавить точки маршрута", callback_data=f"add_trip_points_{trip_id}"),
        types.InlineKeyboardButton("Удалить точки маршрута", callback_data=f"dell_trip_points_{trip_id}"),
        types.InlineKeyboardButton("Назад ↩️", callback_data="edit_trip")
    )

    await callback_query.message.edit_text("Выберите действие для редактирования путешествия:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('edit_trip_name_'))
async def edit_trip_name(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем идентификатор путешествия из данных колбэка
    trip_id = callback_query.data.split('_')[3]

    # Отправляем сообщение с запросом на новое название путешествия
    await callback_query.message.edit_text("Введите новое название для путешествия:")

    # Устанавливаем состояние ожидания нового названия путешествия
    await EditTravel.EditName.set()

    # Сохраняем идентификатор путешествия в состоянии для дальнейшего использования
    await state.update_data(trip_id=trip_id)


@dp.message_handler(state=EditTravel.EditName)
async def process_edit_trip_name(message: types.Message, state: FSMContext):
    # Получаем новое название из сообщения пользователя
    new_name = message.text

    # Получаем идентификатор путешествия из состояния
    data = await state.get_data()
    trip_id = data.get('trip_id')

    # Вызываем функцию для редактирования названия путешествия
    await edit_trip_mod(trip_id, 'name', new_name)

    # Отправляем пользователю сообщение об успешном редактировании
    await message.reply("Название путешествия успешно отредактировано!")
    await manage_travel_mess(message)
    # Сбрасываем состояние
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith('edit_trip_description_'))
async def edit_trip_description(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем идентификатор путешествия из данных колбэка
    trip_id = callback_query.data.split('_')[3]

    # Отправляем сообщение с запросом на новое описание путешествия
    await callback_query.message.edit_text("Введите новое описание для путешествия:")

    # Устанавливаем состояние ожидания нового описания путешествия
    await EditTravel.EditDescription.set()

    # Сохраняем идентификатор путешествия в состоянии для дальнейшего использования
    await state.update_data(trip_id=trip_id)


@dp.message_handler(state=EditTravel.EditDescription)
async def process_edit_trip_description(message: types.Message, state: FSMContext):
    # Получаем новое описание из сообщения пользователя
    new_description = message.text

    # Получаем идентификатор путешествия из состояния
    data = await state.get_data()
    trip_id = data.get('trip_id')

    # Вызываем функцию для редактирования описания путешествия
    await edit_trip_mod(trip_id, 'description', new_description)

    # Отправляем пользователю сообщение об успешном редактировании
    await message.reply("Описание путешествия успешно отредактировано!")
    await manage_travel_mess(message)
    # Сбрасываем состояние
    await state.finish()

#редактирование точек маршрута ----------------
@dp.callback_query_handler(lambda c: c.data.startswith('add_trip_points_'))
async def add_trip_points(callback_query: types.CallbackQuery, state: FSMContext):
    trip_id = callback_query.data.split('_')[3]

    # Отправляем сообщение с запросом на ввод новой точки маршрута
    await callback_query.message.edit_text("Введите новую точку маршрута:")

    # Устанавливаем состояние ожидания новой точки маршрута
    await AddPoints.EnterPoint.set()

    # Сохраняем идентификатор путешествия в состоянии для дальнейшего использования
    await state.update_data(trip_id=trip_id)


@dp.message_handler(state=AddPoints.EnterPoint)
async def process_add_trip_points(message: types.Message, state: FSMContext):
    # Получаем новую точку маршрута из сообщения пользователя
    new_point = message.text

    # Получаем идентификатор путешествия из состояния
    data = await state.get_data()
    trip_id = data.get('trip_id')

    # Пытаемся найти указанное место
    location_info = geolocator.geocode(new_point)

    if location_info:
        # Если место найдено успешно, спрашиваем пользователя подтверждение
        await message.reply(f"Это ваша точка маршрута? {location_info}", reply_markup=right_city_3)
        await state.update_data(location_info=location_info.address)
        await state.update_data(latitude=location_info.latitude)
        await state.update_data(longitude=location_info.longitude)
        await AddPoints.ConfirmPoint.set()
    else:
        # Если место не найдено, просим пользователя ввести ещё раз
        await message.reply("Указанное местоположение не найдено. Пожалуйста, попробуйте ввести его ещё раз.")


@dp.callback_query_handler(lambda c: c.data == 'city_confirm_ch_3', state=AddPoints.ConfirmPoint)
async def confirm_point(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    location_info = data.get('location_info')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # Получаем идентификатор путешествия из состояния
    trip_id = data.get('trip_id')

    # Обновляем состояние, чтобы запомнить точку маршрута и идентификатор путешествия
    await state.update_data(location_info=location_info)
    await state.update_data(latitude=latitude)
    await state.update_data(longitude=longitude)
    await state.update_data(trip_id=trip_id)

    # Отправляем пользователю запрос на ввод времени начала
    await callback_query.message.edit_text("Введите время начала в формате ГГГГ-ММ-ДД (например, 2024-03-20):")
    await AddPoints.EnterStartDate.set()

    # Ответим на колбэк, чтобы убрать кружок ожидания
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data == 'city_reenter_ch_3', state=AddPoints.ConfirmPoint)
async def reenter_point(callback_query: types.CallbackQuery, state: FSMContext):
    # Просим пользователя ввести местоположение ещё раз
    await callback_query.message.edit_text("Введите новую точку маршрута:")

    # Устанавливаем состояние ожидания новой точки маршрута
    await AddPoints.EnterPoint.set()

    # Сбрасываем данные о предыдущей точке из состояния
    await state.update_data(location_info=None)

    # Ответим на колбэк, чтобы убрать кружок ожидания
    await callback_query.answer()

@dp.message_handler(state=AddPoints.EnterStartDate)
async def process_enter_start_date(message: types.Message, state: FSMContext):
    # Получаем введенное время начала из сообщения пользователя
    start_date_str = message.text

    try:
        # Преобразуем строку времени начала в объект даты
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        # Обновляем состояние, чтобы запомнить время начала
        await state.update_data(start_date=start_date)

        # Отправляем пользователю запрос на ввод времени завершения
        await message.reply("Введите время завершения в формате ГГГГ-ММ-ДД (например, 2024-03-25):")
        await AddPoints.EnterEndDate.set()
    except ValueError:
        # Если введенное время начала имеет неверный формат, просим пользователя ввести ещё раз
        await message.reply("Некорректный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД (например, 2024-03-25):")


@dp.message_handler(state=AddPoints.EnterEndDate)
async def process_enter_end_date(message: types.Message, state: FSMContext):
    # Получаем введенное время завершения из сообщения пользователя
    end_date_str = message.text

    try:
        # Преобразуем строку времени завершения в объект даты
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Получаем данные из состояния
        data = await state.get_data()
        location_info = data.get('location_info')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        trip_id = data.get('trip_id')
        start_date = data.get('start_date')

        # Добавляем новую точку маршрута в базу данных
        await add_trip_point(trip_id, location_info, latitude, longitude, start_date, end_date)

        # Отправляем пользователю сообщение об успешном добавлении точки маршрута
        await message.reply("Новая точка маршрута успешно добавлена!")
        await manage_travel_mess(message=message)
        # Сбрасываем состоя ние
        await state.finish()
    except ValueError:
        # Если введенное время завершения имеет неверный формат, просим пользователя ввести ещё раз
        await message.reply("Некорректный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД (например, 2024-03-25):")


#удаление точек марштрута-----------------------------

@dp.callback_query_handler(lambda c: c.data.startswith('dell_trip_points_'))
async def dell_trip_points(callback_query: types.CallbackQuery):
    trip_id = callback_query.data.split('_')[3]

    # Получаем список точек маршрута для указанного путешествия
    trip_points = await get_trip_points(trip_id)

    if not trip_points:
        await callback_query.message.edit_text("В этом путешествии пока нет точек маршрута.",
                                               reply_markup=types.InlineKeyboardMarkup().add(
                                                   types.InlineKeyboardButton("Назад ↩️", callback_data="edit_trip")))
        return

    # Создаем список кнопок для каждой точки маршрута
    buttons = []
    for point in trip_points:
        buttons.append(
            types.InlineKeyboardButton(point['location_name'], callback_data=f"delete_point_{point['location_id']}"))

    # Отправляем сообщение с информацией о точках маршрута и кнопками для удаления точек
    await callback_query.message.edit_text("Выберите точку маршрута для удаления:",
                                           reply_markup=types.InlineKeyboardMarkup().add(*buttons).add(
                                               types.InlineKeyboardButton("Назад ↩️", callback_data="edit_trip")))

    # Ответим на колбэк, чтобы убрать кружок ожидания
    await callback_query.answer()
@dp.callback_query_handler(lambda c: c.data.startswith('delete_point_'))
async def delete_trip_point(callback_query: types.CallbackQuery):
    # Извлекаем идентификатор точки маршрута из колбэка
    point_id = callback_query.data.split('_')[2]

    try:
        # Выполняем удаление точки маршрута по её идентификатору
        await delete_trip_point_by_id(point_id)

        # Отправляем пользователю сообщение об успешном удалении точки маршрута
        await callback_query.message.edit_text("Точка маршрута успешно удалена!")

    except Exception as e:
        # Обрабатываем возможные ошибки при удалении точки маршрута
        await callback_query.message.edit_text("Ошибка при удалении точки маршрута.")

    # Ответим на колбэк, чтобы убрать кружок ожидания
    await callback_query.answer()
    await manage_travel_mess(message=callback_query.message)
#Просмотр путешествий----------------------------------------------------------------------------------------------------------------------------------------


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'list_trips')
async def list_trips(callback_query: types.CallbackQuery):
    locations = await get_user_trips_with_locations(callback_query.from_user.id)
    await callback_query.message.edit_text(await format_trip_message(locations),reply_markup=back_to_menu_travels_keyboard)




# Обработчик для кнопки "Заметки к путешествию"--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'travel_notes')
async def travel_notes(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали заметки к путешествию.")

# Обработчик для кнопки "Путешествия с друзьями"---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'travel_with_friends')
async def travel_with_friends(callback_query: types.CallbackQuery):
    # Красивое сообщение с использованием emoji
    message_text = "Вы выбрали путешествия с друзьями. 🌍👫🎉\n\n" \
                   "Что вы хотите сделать дальше?"

    # Создание кнопок
    buttons = [
        types.InlineKeyboardButton("Добавить пользователя в путешествие ➕", callback_data="add_user_to_trip"),
        types.InlineKeyboardButton("Просмотреть все путешествия, в которые вы добавлены 🔍", callback_data="view_all_trips"),
        types.InlineKeyboardButton("Назад ↩️", callback_data="show_menu")
    ]
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    for button in buttons:
        keyboard_markup.add(button)
    # Отправка сообщения с кнопками
    await callback_query.message.edit_text(message_text, reply_markup=keyboard_markup)


async def travel_with_friends_mes(message):
    # Красивое сообщение с использованием emoji
    message_text = "Вы выбрали путешествия с друзьями. 🌍👫🎉\n\n" \
                   "Что вы хотите сделать дальше?"

    # Создание кнопок
    buttons = [
        types.InlineKeyboardButton("Добавить пользователя в путешествие ➕", callback_data="add_user_to_trip"),
        types.InlineKeyboardButton("Просмотреть все путешествия, в которые вы добавлены 🔍", callback_data="view_all_trips"),
        types.InlineKeyboardButton("Назад ↩️", callback_data="show_menu")
    ]
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    for button in buttons:
        keyboard_markup.add(button)

    # Отправка сообщения с кнопками
    await message.answer(message_text, reply_markup=keyboard_markup)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'view_all_trips')
async def view_all_trips(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Получаем информацию о путешествиях, в которые добавили пользователя
    joined_trips_info = await get_joined_trips_info(user_id)

    back_button = types.InlineKeyboardButton("Назад ↩️", callback_data="travel_with_friends")

    keyboard_markup = types.InlineKeyboardMarkup(row_width=1).add(back_button)

    if not joined_trips_info:
        await callback_query.message.edit_text("Вы еще не добавлены ни в одно путешествие.", reply_markup=keyboard_markup)
        return

    trips_text= await format_trip_message(joined_trips_info)


    await callback_query.message.edit_text(trips_text, reply_markup=keyboard_markup)
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'add_user_to_trip')
async def add_user_to_trip(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    trips_data = await get_user_trips_with_locations(user_id)

    # Если у пользователя нет путешествий, сообщаем ему об этом
    if not trips_data:
        await callback_query.message.edit_text("У вас нет созданных путешествий. "
                                               "Сначала создайте путешествие, а затем добавьте в него других пользователей.")
        return

    # Создаем список кнопок для выбора путешествия
    unique_trip_ids = set(trip['trip_id'] for trip in trips_data)

    # Создаем список кнопок для каждого уникального путешествия
    buttons = []
    for trip_id in unique_trip_ids:
        # Находим соответствующее путешествие по его идентификатору
        trip = next((t for t in trips_data if t['trip_id'] == trip_id), None)
        if trip:
            buttons.append(types.InlineKeyboardButton(trip['trip_name'], callback_data=f"add-user-to-trip_{trip['trip_id']}"))

    # Добавляем кнопку "Назад"
    back_button = types.InlineKeyboardButton("Назад ↩️", callback_data="travel_with_friends")
    buttons.append(back_button)

    trip_message = await format_trip_message(trips_data)

    # Создаем клавиатуру с кнопками
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(*buttons)
    await callback_query.message.edit_text(
        trip_message,
        reply_markup=keyboard_markup
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('add-user-to-trip_'))
async def add_user_to_trip(callback_query: types.CallbackQuery, state: FSMContext):
    # Извлекаем идентификатор путешествия из callback_data
    trip_id = callback_query.data.split('_')[-1]

    # Сохраняем идентификатор путешествия в состоянии FSM
    await state.update_data(trip_id=trip_id)

    # Отправляем сообщение с запросом никнейма пользователя
    await callback_query.message.edit_text(
        "Введите никнейм пользователя (в формате: @username), которого вы хотите добавить в путешествие.\n\n"
        "Пожалуйста, учтите, что пользователь должен пройти регистрацию в боте, чтобы вы могли его добавить. ✨",
    )
    await AddUserToTrip.Username.set()  # Устанавливаем состояние ожидания сообщения пользователя

@dp.message_handler(state=AddUserToTrip.Username)
async def process_username(message: types.Message, state: FSMContext):
    # Получаем введенный пользователем никнейм
    username = message.text

    # Проверяем наличие символа "@" в начале никнейма
    if not username.startswith("@"):
        await message.reply("Никнейм был введен в неправильном формате. Пожалуйста, введите никнейм пользователя "
                            "в формате: @username.")
        return

    # Проверяем существование пользователя и добавляем его в участники путешествия
    trip_id = (await state.get_data()).get('trip_id')  # Получаем идентификатор путешествия из состояния
    success, error_code = await add_friend_to_trip(username, trip_id)
    if not success:
        error_messages = {
            1: "К сожалению, я не смог найти пользователя с указанным никнеймом. Убедитесь, что ваш друг зарегистрирован в нашем боте. 🤖",
            2: "Этот пользователь уже добавлен в участники этого путешествия. 😊",
            3: "Вы уже являетесь создателем этого путешествия, поэтому автоматически являетесь его участником. 😉",
            4: "Что-то пошло не так. Пожалуйста, попробуйте еще раз или обратитесь к администратору за помощью. 🛠️"
        }
        await message.reply(error_messages.get(error_code, "Произошла неизвестная ошибка."))
        await state.finish()  # Завершаем состояние FSM
        await travel_with_friends_mes(message)
        return
    # Пользователь успешно добавлен в участники путешествия
    await message.reply(f"Пользователь {username} успешно добавлен в участники путешествия! 🎉")
    await state.finish()  # Завершаем состояние FSM
    await travel_with_friends_mes(message)

 # types.InlineKeyboardButton("Просмотреть все путешествия, в которые вы добавлены 🔍", callback_data="view_all_trips")


# Обработчик для кнопки "Прокладывание маршрута путешествия"---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'plan_travel_route')
async def plan_travel_route(callback_query: types.CallbackQuery):
    # Создаем кнопки для прокладывания маршрутов
    travel_route_button = types.InlineKeyboardButton("Прокладывание маршрута путешествия 🗺️", callback_data="travel_route")
    start_route_button = types.InlineKeyboardButton("Построить маршрут до начальной точки путешествия 🏃‍♂️", callback_data="start_route")
    back = types.InlineKeyboardButton("Назад ↩️", callback_data="show_menu")

    # Создаем клавиатуру с кнопками
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(travel_route_button, start_route_button,back)

    # Отправляем текстовое сообщение
    await callback_query.message.edit_text("🌟 Выберите, что вы хотите сделать:", reply_markup=keyboard_markup)


# Обработчик для кнопки "Прокладывание маршрута путешествия"
# Обработчик для кнопки "Прокладывание маршрута путешествия"
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'travel_route')
async def travel_route(callback_query: types.CallbackQuery):
    # Создаем клавиатуру с кнопками для выбора путешествий пользователя или друзей
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        InlineKeyboardButton("Мои путешествия", callback_data="my_trips"),
        InlineKeyboardButton("Путешествия друзей", callback_data="friend_trips"),
        InlineKeyboardButton("Назад ↩️", callback_data="plan_travel_route")
    )

    await callback_query.message.edit_text("Выберите, какие путешествия вас интересуют:", reply_markup=keyboard_markup)

# Обработчики для выбора путешествий пользователя или друзей
@dp.callback_query_handler(lambda callback_query: callback_query.data in ['my_trips', 'friend_trips'])
async def select_trip_type(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    trip_type = callback_query.data

    # Получаем соответствующие путешествия (пользовательские или путешествия друзей)
    if trip_type == 'my_trips':
        trips = await get_user_trip_names_format(user_id)
        message_text = "Выберите путешествие из ваших:"
    else:
        trips = await get_friends_trips_names(user_id)
        message_text = "Выберите путешествие из путешествий ваших друзей:"

    if not trips:
        await callback_query.message.edit_text("Путешествия не найдены. Создайте их или попросите друзей пригласить вас в их путешествие. 🌍🚀",reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Назад ↩️", callback_data="travel_route")))
        return

    # Создаем клавиатуру с кнопками для выбора путешествия
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    for trip in trips:
        keyboard_markup.add(InlineKeyboardButton(trip['trip_name'], callback_data=f"select_trip_{trip['trip_id']}"))
    keyboard_markup.add(InlineKeyboardButton("Назад ↩️", callback_data="travel_route"))

    await callback_query.message.edit_text(message_text, reply_markup=keyboard_markup)



# Обработчик для кнопки "Построить маршрут до начальной точки путешествия"
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'start_route')
async def start_route(callback_query: types.CallbackQuery):
    # Создаем клавиатуру с кнопками для выбора путешествий пользователя или друзей
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(
        InlineKeyboardButton("Мои путешествия", callback_data="my_trips_start"),
        InlineKeyboardButton("Путешествия друзей", callback_data="friend_trips_start"),
        InlineKeyboardButton("Назад ↩️", callback_data="plan_travel_route")
    )

    await callback_query.message.edit_text("Выберите, какие путешествия вас интересуют:", reply_markup=keyboard_markup)

# Обработчики для выбора путешествий пользователя или друзей для построения маршрута до начальной точки
@dp.callback_query_handler(lambda callback_query: callback_query.data in ['my_trips_start', 'friend_trips_start'])
async def select_trip_type_start(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    trip_type = callback_query.data.replace("_start", "")

    # Получаем соответствующие путешествия (пользовательские или путешествия друзей)
    if trip_type == 'my_trips':
        trips = await get_user_trip_names_format(user_id)
        message_text = "Выберите путешествие из ваших:"
    else:
        trips = await get_friends_trips_names(user_id)
        message_text = "Выберите путешествие из путешествий ваших друзей:"

    if not trips:
        await callback_query.message.edit_text("Путешествия не найдены. Создайте их или попросите друзей пригласить вас в их путешествие. 🌍🚀", reply_markup=InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Назад ↩️", callback_data="start_route")))
        return

    # Создаем клавиатуру с кнопками для выбора путешествия
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    for trip in trips:
        keyboard_markup.add(InlineKeyboardButton(trip['trip_name'], callback_data=f"select_trip_{trip['trip_id']}"))
    keyboard_markup.add(InlineKeyboardButton("Назад ↩️", callback_data="start_route"))
    await callback_query.message.edit_text(message_text, reply_markup=keyboard_markup)


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)