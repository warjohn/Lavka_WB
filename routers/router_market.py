import asyncio

import aiogram.exceptions
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.types.callback_query import CallbackQuery

import kb.kb
import text.text as tt
import routers.utils.data as data
from routers.utils.State import ALL_STATE
from routers.utils.Storage import Storage
from routers.utils.data import MainStorage

router_market = Router()

@router_market.callback_query(F.data, ALL_STATE.market)
async def choose(clbk: CallbackQuery, state: FSMContext):
    try:
        for i in data.msg_image.get_msg_id_list():
            try:
                await clbk.bot.delete_message(clbk.message.chat.id, i)
            except aiogram.exceptions.TelegramBadRequest as e:
                pass
        data.msg_image.get_msg_id_list().clear()
    except aiogram.exceptions.TelegramBadRequest as e:
        print(e)
    await data.delet(clbk)
    if clbk.data == 'wb':
        MainStorage(clbk.from_user.id).market_place = str(clbk.data)
        bot_msg = await clbk.message.answer("КАТАЛОГ ТОВАРОВ", reply_markup = kb.kb.katalog_key)
        data.msg_data.msg_id = bot_msg.message_id
    else:
        MainStorage(clbk.from_user.id).market_place = str(clbk.data)
        bot_msg = await clbk.message.answer("КАТАЛОГ ТОВАРОВ", reply_markup = kb.kb.katalog_key)
        data.msg_data.msg_id = bot_msg.message_id
    await state.set_state(ALL_STATE.kat)

@router_market.callback_query(F.data == "back_to_kat", ALL_STATE.anketa)
@router_market.callback_query(F.data == "katalog", ALL_STATE.kat)
async def main_menu(clbk: CallbackQuery, state: FSMContext):
    await data.delet(clbk)
    bot_msg = await clbk.message.answer(tt.text_kat, reply_markup=Storage.create_keyboards_start(clbk.from_user.id))
    await state.set_state(ALL_STATE.main)
    data.msg_data.msg_id = bot_msg.message_id
