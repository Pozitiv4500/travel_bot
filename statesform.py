from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    Name = State()
    Age = State()
    City = State()
    Location = State()
    ConfirmLocation = State()
    Bio = State()