from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

async def cmd_start(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Прогноз на сегодня", callback_data="forecast_today")],
        [InlineKeyboardButton(text="📅 Прогноз на 3 дня", callback_data="forecast_three_days")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
    ])
    sent_message = await message.answer("Какой прогноз вы хотели бы получить?", reply_markup=kb)
    await state.update_data(main_menu_message_id=sent_message.message_id, last_forecast_message_id=None, notifications='Отключена')

def register_main_menu_handlers(dp):
    dp.message.register(cmd_start, Command("start"))
