import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from app.config import settings
from app.database import database, engine, metadata, get_session
from app.handlers import setup_handlers

logging.basicConfig(level=logging.INFO)

async def on_startup(bot: Bot):
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await database.connect()
    logging.info('Database connected')
    # notify admin bot is up
    if settings.admin_id:
        try:
            await bot.send_message(chat_id=settings.admin_id, text='Poizon bot started.')
        except Exception:
            pass

async def on_shutdown(bot: Bot):
    await database.disconnect()

async def main():
    bot = Bot(token=settings.bot_token, parse_mode='HTML')
    dp = Dispatcher()
    setup_handlers(dp)
    await on_startup(bot)
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(bot)

if __name__ == '__main__':
    asyncio.run(main())
