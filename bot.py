import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from keyboards import Location_keyboard
from geopy.geocoders import Nominatim


from config import BOT_TOKEN
from models import db_start

from statesform import Registration
# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Устанавливаем токен вашего бота


# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot,storage=MemoryStorage())

geolocator = Nominatim(user_agent="travel_bot")

async def on_startup(_):
    await db_start()




# Хэндлер на сообщения с возрастом пользователя
@dp.message_handler(commands=['start'], state=None)
async def process_age(message: types.Message, state: FSMContext):
    # Получаем имя пользователя из профиля
    name = message.from_user.full_name
    await state.update_data(name=name)  # Сохраняем имя пользователя в состоянии
    await message.reply(
        f"Доброго полудня, {name}! Я помогу тебе организовать твоё путешествие. Для начала давай узнаем о тебе немного больше.")
    await message.answer(f"Сколько тебе лет? (Введите ваш возраст)")
    await state.set_state(Registration.Age)

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

        await state.update_data(latitude=latitude, longitude=longitude)
        await state.finish()
        await message.reply("Спасибо! Мы сохранили информацию о вас.")
    else:
        # Если пользователь отправил текст, проверяем, является ли он названием города
        city = message.text
        location = geolocator.geocode(city)
        if location:
            latitude = location.latitude
            longitude = location.longitude

            keyboard = types.InlineKeyboardMarkup()
            button_yes = types.InlineKeyboardButton(text="Всё верно", callback_data="city_confirm")
            button_no = types.InlineKeyboardButton(text="Неверно", callback_data="city_reenter")
            keyboard.add(button_yes, button_no)
            await state.update_data(latitude=latitude, longitude=longitude)
            await state.set_state(Registration.ConfirmLocation)
            await message.reply(f"Это ваш населенный пункт? {location}", reply_markup=keyboard)
        else:
            # Город не найден, отправляем сообщение с кнопками "Всё верно" и "Наверное"
            await message.reply("Ваш населенный пункт не найден. Пожалуйста, попробуйте ввести название вашего населенного пункта ещё раз.")

# Хэндлер для кнопки "Всё верно"
@dp.callback_query_handler(lambda c: c.data == 'city_confirm', state=Registration.ConfirmLocation)
async def confirm_city(callback_query: CallbackQuery, state: FSMContext):

    await state.set_state(Registration.Bio)  # Завершаем текущее состояние
    await callback_query.message.edit_text("Пожалуйста, расскажите нам немного о себе! Напишите немного о себе: кем вы являетесь, чем увлекаетесь, какие у вас интересы? Спасибо!")  # Изменяем сообщение с подтверждением

# Хэндлер для кнопки "Наверное"
@dp.callback_query_handler(lambda c: c.data == 'city_reenter', state=Registration.ConfirmLocation)
async def reenter_city(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Пожалуйста, введите название вашего населенного пункта ещё раз.")  # Изменяем сообщение с приглашением ввести название пункта ещё раз
    await state.set_state(Registration.Location)

# Хэндлер на сообщения с биографией пользователя
@dp.message_handler(state=Registration.Bio)
async def process_bio(message: types.Message, state: FSMContext):
    bio = message.text
    await state.update_data(bio=bio)  # Сохраняем биографию пользователя в состоянии
    await state.finish()
    await message.reply("Спасибо.")

if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)