import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token="7281434100:AAFHmMLCWjiCOAdwxTiGAB6qJczWPIemwhM")

# Диспетчер
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

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
