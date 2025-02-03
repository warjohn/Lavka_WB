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

router_start = Router()



@router_start.message(Command('start'))
async def main_fun(msg: Message, state: FSMContext):
    data.MainStorage.clear_instance(msg.from_user.id)
    await msg.answer(tt.start_text)
    data.MainStorage(msg.from_user.id)
    bot_msg = await msg.answer(tt.start_text_2, reply_markup=kb.kb.market_key)
    await state.set_state(ALL_STATE.market)
    data.msg_data.msg_id = bot_msg.message_id


@router_start.callback_query(F.data == "back", ALL_STATE.kat)
@router_start.callback_query(F.data == "back", ALL_STATE.market)
@router_start.callback_query(F.data == "back", ALL_STATE.first_good)
async def main_fun_rt(clbk: CallbackQuery, state: FSMContext):
    data.MainStorage.clear_instance(clbk.from_user.id)
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
    data.MainStorage(clbk.from_user.id)
    bot_msg = await clbk.message.answer(tt.start_text, reply_markup=kb.kb.market_key)
    await state.set_state(ALL_STATE.market)

    data.msg_data.msg_id = bot_msg.message_id