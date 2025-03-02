import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import admin_handlers, user_handlers, trade_handlers
from database.models.models import Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "7163945677:AAGp4pLAc-rXM_QB6K0Q34n0dZ0Dfo5S3cU"

async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(trade_handlers.router)

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())