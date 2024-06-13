import asyncio
import aiogram
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = ("7281434100:AAFHmMLCWjiCOAdwxTiGAB6qJczWPIemwhM")
dp = Dispatcher()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def command_start_handler(message: Message):
    await message.answer("Привет! Я бот, который может отправить тебе текущую погоду. "
                         "Нажми кнопку ниже, чтобы отправить мне свою геопозицию и узнать погоду в этом месте.")

async def main():
    await dp.start_polling(skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())