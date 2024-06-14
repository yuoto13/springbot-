from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from services.weather import get_weather, format_weather_today, format_weather_three_days

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

def register_forecast_handlers(dp):
    dp.callback_query.register(handle_forecast_and_settings_buttons, lambda callback_query: callback_query.data in ["forecast_today", "forecast_three_days", "settings"])