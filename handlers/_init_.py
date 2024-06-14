from aiogram import Dispatcher
from .main_menu import register_main_menu_handlers
from .forecast import register_forecast_handlers
from .settings import register_settings_handlers

def register_handlers(dp: Dispatcher):
    register_main_menu_handlers(dp)
    register_forecast_handlers(dp)
    register_settings_handlers(dp)