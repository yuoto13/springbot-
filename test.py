import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta, timezone
import test_config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=test_config.BOT_TOKEN)

# Диспетчер
dp = Dispatcher(storage=MemoryStorage())

# Маппинг месяцев на русском языке
months = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
    7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}

# Функция для форматирования даты на русском языке
def format_date(date):
    return f"{date.day} {months[date.month]}"

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить геопозицию", request_location=True)]
        ],
        resize_keyboard=True
    )
    await message.answer("Пожалуйста, отправьте свою геопозицию для получения прогноза погоды.", reply_markup=kb)
    await state.update_data(main_menu_message_id=None, last_forecast_message_id=None, notifications='Отключена')

# Хэндлер для получения геопозиции
@dp.message(lambda message: message.location is not None)
async def handle_location(message: types.Message, state: FSMContext):
    geolocator = Nominatim(user_agent="weather_bot")
    location = message.location
    try:
        location_info = geolocator.reverse((location.latitude, location.longitude), language="ru")
        city = location_info.raw['address'].get('city', location_info.raw['address'].get('town', ''))
        if city:
            await state.update_data(location_city=city, user_id=message.from_user.id)
            await message.answer(f"Город определен: {city}")
            await show_main_menu(message, state)
        else:
            await message.answer("Не удалось определить город по геопозиции. Пожалуйста, введите город вручную.")
    except Exception as e:
        logging.error(f"Exception occurred while fetching location: {e}")
        await message.answer("Ошибка при определении геопозиции. Пожалуйста, введите город вручную.")

async def show_main_menu(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Прогноз на сегодня", callback_data="forecast_today")],
        [InlineKeyboardButton(text="📅 Прогноз на 3 дня", callback_data="forecast_three_days")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
    ])
    sent_message = await message.answer("Какой прогноз вы хотели бы получить?", reply_markup=kb)
    await state.update_data(main_menu_message_id=sent_message.message_id)

# Хэндлеры для инлайн-кнопок прогнозов и настроек
@dp.callback_query(lambda callback_query: callback_query.data in ["forecast_today", "forecast_three_days", "settings"])
async def handle_forecast_and_settings_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_main_menu(callback_query.message.chat.id, state)
    if callback_query.data == "forecast_today":
        await forecast_today(callback_query.message, state)
    elif callback_query.data == "forecast_three_days":
        await forecast_three_days(callback_query.message, state)
    elif callback_query.data == "settings":
        await settings(callback_query.message, state)

async def delete_main_menu(chat_id: int, state: FSMContext):
    data = await state.get_data()
    main_menu_message_id = data.get('main_menu_message_id')
    if main_menu_message_id:
        await bot.delete_message(chat_id, main_menu_message_id)
        await state.update_data(main_menu_message_id=None)

async def delete_last_forecast(chat_id: int, state: FSMContext):
    data = await state.get_data()
    last_forecast_message_id = data.get('last_forecast_message_id')
    if last_forecast_message_id:
        await bot.delete_message(chat_id, last_forecast_message_id)
        await state.update_data(last_forecast_message_id=None)

async def delete_last_settings_message(chat_id: int, state: FSMContext):
    data = await state.get_data()
    last_settings_message_id = data.get('last_settings_message_id')
    if last_settings_message_id:
        await bot.delete_message(chat_id, last_settings_message_id)
        await state.update_data(last_settings_message_id=None)

async def forecast_today(message: types.Message, state: FSMContext):
    await delete_last_forecast(message.chat.id, state)
    data = await state.get_data()
    city = data.get('location_city')
    if not city:
        await message.answer("Пожалуйста, отправьте свою геопозицию или укажите город вручную.")
        await show_main_menu(message, state)
        return
    
    weather = await get_weather(city, 1)
    if weather:
        sent_message = await message.answer(weather)
        await state.update_data(last_forecast_message_id=sent_message.message_id)
    else:
        await message.answer("Не удалось получить прогноз погоды. Пожалуйста, попробуйте позже.")
    await show_main_menu(message, state)

async def forecast_three_days(message: types.Message, state: FSMContext):
    await delete_last_forecast(message.chat.id, state)
    data = await state.get_data()
    city = data.get('location_city')
    if not city:
        await message.answer("Пожалуйста, отправьте свою геопозицию или укажите город вручную.")
        await show_main_menu(message, state)
        return
    
    weather = await get_weather(city, 3)
    if weather:
        sent_message = await message.answer(weather)
        await state.update_data(last_forecast_message_id=sent_message.message_id)
    else:
        await message.answer("Не удалось получить прогноз погоды. Пожалуйста, попробуйте позже.")
    await show_main_menu(message, state)

async def settings(message: types.Message, state: FSMContext):
    await delete_last_settings_message(message.chat.id, state)
    data = await state.get_data()
    city = data.get('location_city', 'Не указан')
    notifications = data.get('notifications', 'Отключена')

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить город", callback_data="change_city")],
        [InlineKeyboardButton(text="Отправить геопозицию", callback_data="send_location")],
        [InlineKeyboardButton(text=f"{'Отключить' if notifications == 'Включена' else 'Включить'} рассылку", callback_data="toggle_notifications")],
        [InlineKeyboardButton(text="Вернуться назад", callback_data="back_to_menu")]
    ])

    sent_message = await message.answer(f"Ваши текущие настройки:\nГород: {city}\nРассылка: {notifications}", reply_markup=kb)
    await state.update_data(last_settings_message_id=sent_message.message_id)

# Обработчики для кнопок настроек
@dp.callback_query(lambda callback_query: callback_query.data in ["change_city", "send_location", "back_to_menu", "toggle_notifications"])
async def handle_settings_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_last_settings_message(callback_query.message.chat.id, state)
    if callback_query.data == "change_city":
        await callback_query.message.answer("Пожалуйста, введите название вашего города.")
    elif callback_query.data == "send_location":
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📍 Отправить геопозицию", request_location=True)]
            ],
            resize_keyboard=True
        )
        await callback_query.message.answer("Отправьте свою геопозицию.", reply_markup=kb)
    elif callback_query.data == "toggle_notifications":
        data = await state.get_data()
        notifications = data.get('notifications', 'Отключена')
        new_status = 'Включена' if notifications == 'Отключена' else 'Отключена'
        await state.update_data(notifications=new_status)
        await callback_query.message.answer(f"Рассылка {new_status.lower()}а.")
        await settings(callback_query.message, state)
    elif callback_query.data == "back_to_menu":
        await show_main_menu(callback_query.message, state)

# Хэндлер для изменения города
@dp.message(lambda message: message.text is not None)
async def handle_city_change(message: types.Message, state: FSMContext):
    await delete_last_settings_message(message.chat.id, state)
    city = message.text
    user_id = message.from_user.id
    await state.update_data(location_city=city, user_id=user_id)
    await message.answer(f"Город изменен на {city}.")
    await show_main_menu(message, state)

async def get_weather(city: str, days: int):
    if days == 1:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={test_config.WEATHER_API_KEY}&units=metric&lang=ru"
        url_forecast = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={test_config.WEATHER_API_KEY}&units=metric&lang=ru"
    else:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={test_config.WEATHER_API_KEY}&units=metric&lang=ru"
        url_forecast = None
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if days == 1 and url_forecast:
                        async with session.get(url_forecast) as response_forecast:
                            if response_forecast.status == 200:
                                data_forecast = await response_forecast.json()
                                return format_weather_today(data, data_forecast)
                            else:
                                logging.error(f"Error from OpenWeather API (forecast): {response_forecast.status}")
                                return None
                    else:
                        return format_weather_three_days(data)
                else:
                    logging.error(f"Error from OpenWeather API: {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Exception occurred while fetching weather: {e}")
            return None

def format_weather_today(data, forecast_data):
    current_temp = round(data['main']['temp'])
    temp_max = round(data['main']['temp_max'])
    temp_min = round(data['main']['temp_min'])
    description = data['weather'][0]['description'].capitalize()
    wind_speed = data['wind']['speed']
    wind_direction = get_wind_direction(data['wind']['deg'])
    humidity = data['main']['humidity']
    pressure = round(data['main']['pressure'] * 0.750062)  # Преобразование гПа в мм рт. ст.
    sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
    sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')

    # Фаза Луны (можно использовать дополнительный API или библиотеку для точного расчета)
    moon_phase = "Первая четверть"

    # Прогноз на утро, день и вечер
    morning_temp, afternoon_temp, evening_temp = get_forecast_temps(forecast_data)

    icon_mapping = {
        '01d': '☀️', '01n': '🌕',
        '02d': '⛅', '02n': '⛅',
        '03d': '☁️', '03n': '☁️',
        '04d': '☁️', '04n': '☁️',
        '09d': '🌧', '09n': '🌧',
        '10d': '🌦', '10n': '🌦',
        '11d': '⛈', '11n': '⛈',
        '13d': '❄️', '13n': '❄️',
        '50d': '🌫', '50n': '🌫'
    }
    weather_icon = icon_mapping.get(data['weather'][0]['icon'], '🌤')

    weather_message = (
        f"Сегодня, {format_date(datetime.now())}\n"
        f"{weather_icon} +{temp_max}°...+{temp_min}°, {description}\n"
        f"Вероятность осадков: {data.get('pop', 0)*100}%\n\n"
        f"Сейчас: {weather_icon} +{current_temp}°, ↙️ {wind_speed} м/с\n\n"
        f"Утром: ☁️ +{morning_temp}°\n"
        f"Днем: ☀️ +{afternoon_temp}°\n"
        f"Вечером: ☀️ +{evening_temp}°\n"
        f"Влажность: {humidity}%\n"
        f"Ветер: {wind_direction}, {wind_speed} м/с\n"
        f"Давление: {pressure} мм рт. ст.\n\n"
        f"Луна: {moon_phase}\n"
        f"Восход: {sunrise}\n"
        f"Закат: {sunset}\n"
    )

    return weather_message

def get_wind_direction(degree):
    directions = ['Северный', 'Северо-Восточный', 'Восточный', 'Юго-Восточный', 'Южный', 'Юго-Западный', 'Западный', 'Северо-Западный']
    ix = round(degree / (360. / len(directions)))
    return directions[ix % len(directions)]

def get_forecast_temps(forecast_data):
    morning_temp = None
    afternoon_temp = None
    evening_temp = None

    for forecast in forecast_data['list']:
        forecast_time = datetime.fromtimestamp(forecast['dt']).hour
        temp = round(forecast['main']['temp'])

        if 6 <= forecast_time < 12 and morning_temp is None:
            morning_temp = temp
        elif 12 <= forecast_time < 18 and afternoon_temp is None:
            afternoon_temp = temp
        elif 18 <= forecast_time < 24 and evening_temp is None:
            evening_temp = temp

    return morning_temp, afternoon_temp, evening_temp

def format_weather_three_days(data):
    return format_weather_general(data, 3)

def format_weather_general(data, days):
    if days == 1:
        forecasts = [data]
    else:
        forecasts = data['list'][:days*8:8]  # данные на каждые 3 часа, берем 8 записей для 3 дней

    weather_message = ""
    for i, forecast in enumerate(forecasts):
        date = datetime.fromtimestamp(forecast['dt']).strftime('%d %B')
        temp_max = round(forecast['main']['temp_max'])
        temp_min = round(forecast['main']['temp_min'])
        description = forecast['weather'][0]['description'].capitalize()
        icon = forecast['weather'][0]['icon']

        day_mapping = {0: 'Сегодня', 1: 'Завтра', 2: 'Послезавтра'}
        day_name = day_mapping.get(i, date)

        icon_mapping = {
            '01d': '☀️', '01n': '🌕',
            '02d': '⛅', '02n': '⛅',
            '03d': '☁️', '03n': '☁️',
            '04d': '☁️', '04n': '☁️',
            '09d': '🌧', '09n': '🌧',
            '10d': '🌦', '10n': '🌦',
            '11d': '⛈', '11n': '⛈',
            '13d': '❄️', '13n': '❄️',
            '50d': '🌫', '50n': '🌫'
        }
        weather_icon = icon_mapping.get(icon, '🌤')

        weather_message += (f"{day_name}, {format_date(datetime.fromtimestamp(forecast['dt']))}\n"
                            f"{weather_icon} +{temp_max}°...+{temp_min}°, {description}\n"
                            f"Вероятность осадков: {forecast.get('pop', 0)*100}%\n\n")

    return weather_message

async def weather_updates():
    while True:
        await check_weather_updates()
        await asyncio.sleep(4 * 3600)  # Проверка каждые 4 часа

async def check_weather_updates():
    data = await dp.storage.get_data()
    for chat_id, user_data in data.items():
        city = user_data.get('location_city')
        notifications = user_data.get('notifications', 'Отключена')
        if city and notifications == 'Включена':
            weather_update = await get_weather(city, 1)
            if weather_update:
                await bot.send_message(chat_id, weather_update)

# Запуск процесса поллинга новых апдейтов
async def main():
    asyncio.create_task(weather_updates())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
