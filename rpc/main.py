import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token="7281434100:AAFHmMLCWjiCOAdwxTiGAB6qJczWPIemwhM")
dp = Dispatcher()

# Хэндлер на команду
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Создаем кнопку и клавиатуру для запроса геолокации
    button_location = KeyboardButton(text="Запросить геолокацию", request_location=True)
    location_kb = ReplyKeyboardMarkup(keyboard=[[button_location]], resize_keyboard=True)
    
    await message.answer("Привет! Я бот, который может отправить тебе текущую погоду. "
                         "Нажми кнопку ниже, чтобы отправить мне свою геопозицию и узнать погоду в этом месте.",
                         reply_markup=location_kb)

# Хэндлер для получения геолокации
@dp.message(lambda message: message.location is not None)
async def handle_location(message: types.Message):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(f"{message.location.latitude}, {message.location.longitude}")
    city = location.raw['address'].get('city', '')

    # Создаем кнопки для подтверждения города
    buttons = [
        InlineKeyboardButton(text="Да", callback_data=f"confirm_city:{city}"),
        InlineKeyboardButton(text="Нет", callback_data="deny_city")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

    await message.answer(f"Вы находитесь в городе {city}, верно?", reply_markup=keyboard)
    

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())