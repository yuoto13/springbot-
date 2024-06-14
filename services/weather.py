import aiohttp
import logging
from datetime import datetime
from rpc.config import WEATHER_API_KEY

# Маппинг месяцев на русском языке
months = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
    7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}

# Функция для форматирования даты на русском языке
def format_date(date):
    return f"{date.day} {months[date.month]}"

async def get_weather(city: str, days: int):
    if days == 1:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        url_forecast = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    else:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
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