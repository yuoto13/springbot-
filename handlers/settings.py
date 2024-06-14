from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

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

async def delete_last_settings_message(chat_id: int, state: FSMContext):
    data = await state.get_data()
    last_settings_message_id = data.get('last_settings_message_id')
    if last_settings_message_id:
        await bot.delete_message(chat_id, last_settings_message_id)
        await state.update_data(last_settings_message_id=None)

def register_settings_handlers(dp):
    dp.callback_query.register(handle_settings_buttons, lambda callback_query: callback_query.data in ["change_city", "send_location", "back_to_menu", "toggle_notifications"])