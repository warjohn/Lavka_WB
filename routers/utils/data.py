import csv
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import asyncio
import aiogram.exceptions
import pandas as pd
from typing_extensions import override

class UserStorageMeta(type):
    _instances = {}         # Словарь для хранения экземпляров по user_id
    _global_instance = None  # Общий экземпляр для всех

    def __call__(cls, user_id=None, *args, **kwargs):
        # Если user_id не указан, используем или создаем общий экземпляр
        if user_id is None:
            if cls._global_instance is None:
                cls._global_instance = super().__call__(*args, **kwargs)
            return cls._global_instance
        else:
            # Если user_id указан, создаем или возвращаем экземпляр для него
            if user_id not in cls._instances:
                # Создаем новый экземпляр
                instance = super().__call__(*args, **kwargs)
                # Сохраняем экземпляр в _instances
                cls._instances[user_id] = instance
            return cls._instances[user_id]

    @classmethod
    def clear_instance(cls, user_id=None):
        """Удаляет экземпляр класса для указанного user_id или общий экземпляр, если user_id не задан."""
        if user_id is None:
            cls._global_instance = None
        elif user_id in cls._instances:
            del cls._instances[user_id]


class MainStorage(metaclass=UserStorageMeta):
    alL_table : pd.DataFrame = field(default_factory=pd.DataFrame)
    alL_table_ozon : pd.DataFrame = field(default_factory=pd.DataFrame)
    columns_onetothre : pd.DataFrame = field(default_factory=pd.DataFrame)
    columns_onetothre_ozon : pd.DataFrame = field(default_factory=pd.DataFrame)
    dict_kat: dict
    dict_kat_ozon : dict
    market_place : str
    kat_index : str
    goods_index : int
    value_goods: str
    way : str
    key : str
    active_flag : str = 'yes'
    new_user_data : list

    def __getattr__(self, name):
        # При отсутствии атрибута в экземпляре user_id получаем его из _global_instance
        global_instance = type(self)._global_instance
        if global_instance and hasattr(global_instance, name):
            return getattr(global_instance, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")





class Messega_data:
    """Data class for storing and updating message ID"""

    def __init__(self, msg_id):
        self.msg_id = msg_id  # Устанавливаем начальный msg_id

    def __setattr__(self, key, value):
        if key == "msg_id":
            super().__setattr__(key, value)  # Обновляем msg_id
        else:
            raise AttributeError(f"Cannot set {key}, only msg_id is allowed")

    def __getattr__(self, item):
        if item == "msg_id":
            return super().__getattribute__(item)  # Возвращаем msg_id
        else:
            raise AttributeError(f"{item} не найдено")

class Messega_image:
    """Data class for storing and updating a list of message IDs"""

    def __init__(self, msg_id_list=None):
        if msg_id_list is None:
            self.msg_id_list = []  # Инициализируем пустой список, если не передан
        elif isinstance(msg_id_list, list):
            self.msg_id_list = msg_id_list  # Устанавливаем переданный список
        else:
            raise TypeError("msg_id_list should be a list")

    def add_msg_id(self, msg_id):
        """Добавляет новый msg_id в список"""
        self.msg_id_list.append(msg_id)

    def get_msg_id_list(self):
        """Возвращает весь список msg_id"""
        return self.msg_id_list

class Value_data:
    """Data class for storing and updating message ID"""

    def __init__(self, val):
        self.val = val  # Устанавливаем начальный msg_id

    def __setattr__(self, key, value):
        if key == "val":
            super().__setattr__(key, value)  # Обновляем msg_id
        else:
            raise AttributeError(f"Cannot set {key}, only msg_id is allowed")

    def __getattr__(self, item):
        if item == "val":
            return super().__getattribute__(item)  # Возвращаем val
        else:
            raise AttributeError(f"{item} не найдено")

class MessageHistory:
    """Класс для хранения истории сообщений."""

    def __init__(self):
        self._msg_id = 0
        self.messages = {}  # Словарь для хранения сообщений

    def add_message(self, sender, message):
        """Добавляет сообщение в словарь, очищая текст от лишних символов."""
        cleaned_message = message.strip().replace('\n', '')  # Убираем пробелы и символы новой строки
        self.messages[self._msg_id] = {'time': datetime.now(),
                                       'sender': sender,
                                       'message': cleaned_message}
        self._msg_id += 1  # Увеличиваем msg_id для следующего сообщения

    def get_messages(self):
        """Возвращает все сообщения."""
        temp_output = ""
        for entry in self.messages.values():
            temp_output += f"{entry['time']} - {entry['sender']} написал: {entry['message']}\n"
        return temp_output

    def clear_messages(self):
        """Очищает словарь сообщений."""
        self.messages.clear()
        print("Сообщения очищены.")



# Пример использования
msg_image = Messega_image()
msg_data = Messega_data(msg_id=0)
val_data = Value_data(val='')

# delet last msgs

async def delet(clbk):
    previous_msg = msg_data.msg_id
    chat_id = clbk.message.chat.id
    try:
        await clbk.bot.delete_message(chat_id, previous_msg)
    except aiogram.exceptions.TelegramBadRequest:
        pass

async def delet_msg(msg):
    previous_msg = msg_data.msg_id
    chat_id = msg.chat.id
    try:
        await msg.bot.delete_message(chat_id, previous_msg)
    except aiogram.exceptions.TelegramBadRequest:
        pass

