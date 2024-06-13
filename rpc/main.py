import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token="7281434100:AAFHmMLCWjiCOAdwxTiGAB6qJczWPIemwhM")

# Диспетчер
dp = Dispatcher(storage=MemoryStorage())

# Хэндлер на команду /start
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
async def handle_location(message: types.Message, state: FSMContext):
    geolocator = Nominatim(user_agent="WeatherBot")
    try:
        location = geolocator.reverse(f"{message.location.latitude}, {message.location.longitude}")
        address = location.raw.get('address', {})
        city = address.get('city', '') or address.get('town', '') or address.get('village', '')

        if city:
            await state.update_data(location_city=city)  # Сохраняем город в состоянии пользователя
            await message.answer(f"Вы находитесь в городе {city}, верно? Ответьте 'да' или 'нет'.")
        else:
            await message.answer("Не удалось определить город по геолокации. Попробуйте снова.")
    except (GeocoderTimedOut, Exception) as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Не удалось определить город по геолокации. Попробуйте снова.")

# Хэндлер для подтверждения города
@dp.message(lambda message: message.text.lower() in ["да", "нет"])
async def confirm_city(message: types.Message, state: FSMContext):
    data = await state.get_data()
    city = data.get('location_city')

    if city:
        if message.text.lower() == "да":
            await message.answer(f"Запрашиваю погоду для города {city}...")
            city_en = await get_city_in_english(city)
            if city_en:
                await send_weather(message, city_en)
            else:
                await message.answer("Не удалось преобразовать название города. Попробуйте ввести название города вручную.")
                await state.update_data(location_city=None)  # Очистим сохраненный город для повторного ввода
        else:
            await message.answer("Пожалуйста, введите название вашего города вручную.")
            await state.update_data(location_city=None)  # Очистим сохраненный город для повторного ввода
    else:
        await message.answer("Не удалось найти информацию о городе. Попробуйте отправить геолокацию снова или введите название города вручную.")

# Хэндлер для ручного ввода названия города
@dp.message(lambda message: True)
async def manual_city_entry(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'location_city' in data and data['location_city']:
        # Если город уже есть в состоянии, это значит, что пользователь отвечает на подтверждение
        return
    
    city = message.text
    await state.update_data(location_city=city)
    await message.answer(f"Запрашиваю погоду для города {city}...")
    city_en = await get_city_in_english(city)
    if city_en:
        await send_weather(message, city_en)
    else:
        await message.answer("Не удалось преобразовать название города. Проверьте правильность названия города и попробуйте снова.")

async def get_city_in_english(city: str) -> str:
    geolocator = Nominatim(user_agent="WeatherBot")
    try:
        location = geolocator.geocode(city, language='en')
        if location:
            return location.raw.get('display_name', '').split(',')[0]
        else:
            return None
    except (GeocoderTimedOut, Exception) as e:
        logging.error(f"Error occurred while converting city name: {e}")
        return None

async def send_weather(message: types.Message, city: str):
    weather_api_key = "e9476e0cee748144c1aafdb81884c5e5"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric&lang=ru"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                logging.info(f"OpenWeather API response status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    logging.info(f"OpenWeather API response data: {data}")
                    weather_description = data['weather'][0]['description']
                    temperature = data['main']['temp']
                    await message.answer(f"Сейчас в городе {city} {weather_description}, температура {temperature}°C.")
                else:
                    error_message = await response.text()
                    logging.error(f"Error from OpenWeather API: {error_message}")
                    await message.answer("Не удалось получить погоду для указанного города. Проверьте правильность названия города и попробуйте снова.")
        except Exception as e:
            logging.error(f"Exception occurred while fetching weather: {e}")
            await message.answer("Произошла ошибка при запросе погоды. Попробуйте позже.")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())