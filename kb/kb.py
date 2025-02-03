from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, CallbackGame

from routers.utils.data import MainStorage

admin = [
    [InlineKeyboardButton(text = "Загрузить", callback_data = "load")],
]
admin_key = InlineKeyboardMarkup(inline_keyboard = admin, resize_keyboard=True, one_time_keyboard=True)

admin_1 = [
    [InlineKeyboardButton(text = "Подтверждаю", callback_data = "all_right")],
    [InlineKeyboardButton(text = "изменить данные", callback_data = "not_all_right")]
]
admin_1_key = InlineKeyboardMarkup(inline_keyboard = admin_1, resize_keyboard=True, one_time_keyboard=True)

change = [
    [InlineKeyboardButton(text = 'Номер', callback_data = "number")],
    [InlineKeyboardButton(text = 'Банк', callback_data = "bank")],
    [InlineKeyboardButton(text = 'ФИО', callback_data = "fio")],
]
change_key = InlineKeyboardMarkup(inline_keyboard = change, resize_keyboard=True, one_time_keyboard=True)


def choose_way(id_u):
    if MainStorage(id_u).way == "ключ":
        anketa = [
            [InlineKeyboardButton(text="⬅️", callback_data="prev"),
            InlineKeyboardButton(text="➡️", callback_data="next")],
            [InlineKeyboardButton(text = "Выбрать", callback_data = "key_word")],
            [InlineKeyboardButton(text="Вернуться в категории", callback_data="back_to_kat")],
        ]
        anketa_key = InlineKeyboardMarkup(inline_keyboard = anketa, resize_keyboard=True, one_time_keyboard=True)
        return anketa_key
    else:
        anketa = [
            [InlineKeyboardButton(text="⬅️", callback_data="prev"),
            InlineKeyboardButton(text="️️️➡️", callback_data="next")],
            [InlineKeyboardButton(text = "Выбрать", callback_data = "throw_the_other")],
            [InlineKeyboardButton(text="Вернуться в категории", callback_data="back_to_kat")],

        ]
        anketa_key = InlineKeyboardMarkup(inline_keyboard=anketa, resize_keyboard=True, one_time_keyboard=True)
        return anketa_key

back = [
    [InlineKeyboardButton(text = "Назад", callback_data = "back")]
]
back_key = InlineKeyboardMarkup(inline_keyboard = back, resize_keyboard=True, one_time_keyboard=True)

menu = [
    [InlineKeyboardButton(text = "В первую ступень меню", callback_data = "top_back")]
]
menu_key = InlineKeyboardMarkup(inline_keyboard = menu, resize_keyboard=True, one_time_keyboard=True)

get = [
    [InlineKeyboardButton(text = "Получил", callback_data = "get")]
]
get_key = InlineKeyboardMarkup(inline_keyboard = get, resize_keyboard=True, one_time_keyboard=True)

market = [
    [InlineKeyboardButton(text = "WB", callback_data = "wb")],
    [InlineKeyboardButton(text = "Ozon", callback_data = "ozon")]
]
market_key = InlineKeyboardMarkup(inline_keyboard = market, resize_keyboard=True, one_time_keyboard=True)


katalog = [
    [InlineKeyboardButton(text = "Каталог", callback_data = "katalog")],
    [InlineKeyboardButton(text = "Назад", callback_data = "back")]
]
katalog_key = InlineKeyboardMarkup(inline_keyboard = katalog, resize_keyboard=True, one_time_keyboard=True)


numder = [
    [KeyboardButton(text = "Отправить номер", request_contact=True)]
]
number_key = ReplyKeyboardMarkup(keyboard = numder, resize_keyboard=True, one_time_keyboard=True)

