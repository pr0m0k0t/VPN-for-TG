import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.client_handlers import client_router
from config.settings import BOT_TOKEN
from services.requests import *

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    # Регистрируем роутеры
    dp.include_router(client_router)

    # Запускаем бота
    await dp.start_polling(bot)

async def startup(dispatcher: Dispatcher):
    asyncio.create_task(check_expired_users())
    asyncio.create_task(remind_expired_users())
    asyncio.create_task(remind_about_expiry())
    print('Starting up...')

async def shutdown(dispatcher: Dispatcher):
    print('Shutting down...')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

