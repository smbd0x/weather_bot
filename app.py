import asyncio

from bot.middlewares.logging import LoggingMiddleware
from data.database import create_tables
from loader import bot, dp
from bot.handlers import routers
from logger import bot_logger


async def main():
    for r in routers:
        dp.include_router(r)
    dp.update.middleware(LoggingMiddleware())
    await create_tables()
    await dp.start_polling(bot)

if __name__ == '__main__':
    bot_logger.info('Запуск бота')
    try:
        asyncio.run(main())
    except Exception as e:
        bot_logger.exception(f'Ошибка при запуске бота: {e}')
