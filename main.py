        # -*- coding: utf-8 -*-
import asyncio
import logging
import threading

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.client.bot import DefaultBotProperties

import config as cfg


from routers.router_start import router_start
from routers.router_admin import router_admin
from routers.router_kat import router_kat
from routers.router_anketa import router_anketa
from routers.router_market import router_market
from routers.utils.checker import InactivityChecker


async def start_bot():
    bot = Bot(token=cfg.bot_toke, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router_start)
    dp.include_router(router_market)
    dp.include_router(router_admin)
    dp.include_router(router_kat)
    dp.include_router(router_anketa)
    dp.message.middleware(ChatActionMiddleware())


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

def run_inactivity_checker():
    inactivity_checker = InactivityChecker()
    asyncio.run(inactivity_checker.check_inactivity())



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,  # Уровень логирования
        format='%(asctime)s - %(levelname)s - %(message)s',  # Формат логов
        handlers=[
            logging.FileHandler('bot.log'),  # Запись логов в файл
            logging.StreamHandler()  # Вывод логов в консоль
        ]
    )
    # Запускаем проверку неактивности в отдельном потоке
    checker_thread = threading.Thread(target=run_inactivity_checker)
    checker_thread.start()
    # Запускаем бота
    asyncio.run(start_bot())