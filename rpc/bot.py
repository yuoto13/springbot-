from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from services.location import get_city_by_location

async def cmd_start(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Прогноз на сегодня", callback_data="forecast_today")],
        [InlineKeyboardButton(text="📅 Прогноз на 3 дня", callback_data="forecast_three_days")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
    ])
    sent_message = await message.answer("Какой прогноз вы хотели бы получить?", reply_markup=kb)
    await state.update_data(main_menu_message_id=sent_message.message_id, last_forecast_message_id=None, notifications='Отключена')

async def handle_location(message: types.Message, state: FSMContext):
    location = message.location
    city = await get_city_by_location(location.latitude, location.longitude)
    if city:
        await state.update_data(location_city=city, user_id=message.from_user.id)
        await message.answer(f"Город определен: {city}")
        await show_main_menu(message, state)
    else:
        await message.answer("Не удалось определить город по геопозиции. Пожалуйста, введите город вручную.")

def register_main_menu_handlers(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_location, lambda message: message.location is not None)