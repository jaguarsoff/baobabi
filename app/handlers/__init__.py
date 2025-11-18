from aiogram import Dispatcher, Router
from .main import router as main_router

def setup_handlers(dp: Dispatcher):
    dp.include_router(main_router)
