# routers/utils/inactivity_checker.py
import asyncio
from datetime import datetime, timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Bot, Dispatcher
import text.text as tt
from routers.utils.State import ALL_STATE
import kb.kb as kb
import routers.utils.data as data
from routers.utils.data import MainStorage


class InactivityChecker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.inactivity_limit = kwargs.get('inactivity_limit', timedelta(minutes=15))
            cls.user_status = {}
            cls._instance.user_activity = {}
        return cls._instance

    def __init__(self, useername = None):
        self.username = useername


    def update_activity(self, user_id):
        """Обновляет время последнего действия пользователя."""
        self.user_activity[user_id] = datetime.now()

    def is_user_inactive(self, user_id):
        """Возвращает True, если пользователь неактивен, иначе False."""
        last_activity = self.user_activity.get(user_id)
        if last_activity:
            current_time = datetime.now()
            return current_time - last_activity > self.inactivity_limit
        return True  # Если пользователь еще не взаимодействовал, считаем его неактивным

    async def check_inactivity(self):
        """Фоновая задача для проверки времени простоя пользователей."""
        while True:
            current_time = datetime.now()
            for user_id, last_activity in list(self.user_activity.items()):
                time_inactive = current_time - last_activity > self.inactivity_limit

                if time_inactive and self.user_status.get(user_id, True):
                    # Пользователь стал неактивным
                    self.user_status[user_id] = False
                    print(f"Пользователь {user_id} неактивен.")
                elif not time_inactive and not self.user_status.get(user_id, False):
                    # Пользователь снова стал активным
                    self.user_status[user_id] = True
                    print(f"Пользователь {user_id} активен.")
                    # Можно добавить логику для активации или обработки активности пользователя
            await asyncio.sleep(0.05)  # Проверка каждые n секунд
