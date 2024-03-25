from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    Name = State()
    Age = State()
    City = State()
    Location = State()
    ConfirmLocation = State()
    Bio = State()

class ChangeUser(StatesGroup):
    Bio = State()
    Age = State()
    Location = State()
    Final = State()

class MakeTravel(StatesGroup):
    Name= State()
    Points=State()
    MorePoints= State()
    Okey_city=State()
    StartDate=State()
    EndDate=State()

class EditTravel(StatesGroup):
    EditName = State()
    EditDescription = State()

class AddPoints(StatesGroup):
    EnterPoint=State()
    ConfirmPoint=State()
    EnterStartDate=State()
    EnterEndDate=State()

class AddUserToTrip(StatesGroup):
    Username = State()
    ChooseTrip=State()

class NoteCreation(StatesGroup):
    EnterNote = State()
    ChooseNotePrivacy=State()

class WeatherForecastState(StatesGroup):
    date = State()

class Road_to_Trip(StatesGroup):
    Placment=State()