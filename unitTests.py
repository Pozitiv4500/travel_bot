import pytest
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message
from aiogram.contrib.testing import MockBot, MockDispatcher

from bot import process_age


# Создаем фикстуры для теста
@pytest.fixture
async def message():
    return types.Message(text="/start", from_user=types.User(id=123, username="test_user", full_name="Test User"))

@pytest.fixture
async def bot():
    return MockBot()

@pytest.fixture
async def dispatcher(bot):
    return MockDispatcher(bot)

# Тест для обработчика команды /start
@pytest.mark.asyncio
async def test_process_age(message, bot, dispatcher):
    # Создаем объект состояния FSMContext
    state = FSMContext(dispatcher)

    # Вызываем обработчик команды /start
    await process_age(message, state=state)

    # Проверяем, что отправлено правильное сообщение о запросе возраста
    assert bot.sent_messages[-1]['text'] == "Сколько тебе лет? (Введите ваш возраст)"