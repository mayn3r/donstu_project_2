import asyncio
import json
import os

import config

from tortoise import Tortoise, run_async
from loguru import logger
# from cache3 import SafeCache

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ErrorEvent
from aiogram.filters import ExceptionTypeFilter

from app.handlers import routers
from app.middlewares import middlewares


logger.debug('Starting..')

bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher()

# Add middleware
for middleware in middlewares:
    #outer
    dp.message.middleware(middleware())


@dp.error(ExceptionTypeFilter(json.decoder.JSONDecodeError), F.update.message.as_("message"))
async def handle_my_custom_exception(event: ErrorEvent, message: Message) -> None:
    logger.error("json.decoder.JSONDecodeError")


async def init_db() -> None:
    """Инициализация базы данных"""
    logger.debug('Инициализация базы данных..')
    
    await Tortoise.init(
        db_url="sqlite://database/users.db",
        modules={
            'models': ['app.models']
        }
    )

    # Generate the schema
    await Tortoise.generate_schemas()
    logger.info('Tortoise inited!')



async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    logger.debug("Webhook has been deleted")
    
    dp.include_routers(*routers)

    logger.debug('Bot started!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        run_async(init_db())
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.error('Ctrl+C / KeyboardInterrupt')
        asyncio.new_event_loop().run_until_complete(Tortoise.close_connections())