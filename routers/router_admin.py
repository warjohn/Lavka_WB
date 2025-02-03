import asyncio

import aiogram.exceptions
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, MessageAutoDeleteTimerChanged
from aiogram.types.callback_query import CallbackQuery
from aiogram.utils.chat_member import ADMINS
from oauth2client.client import save_to_well_known_file
from pyasn1_modules.rfc7906 import aa_keyWrapAlgorithm
from pydantic.v1.validators import anystr_strip_whitespace

import text.text as tt
import routers.utils.data as data
from kb.kb import admin_1_key
from routers.router_kat import router_kat
from routers.utils.State import ALL_STATE
from routers.utils.Storage import Storage
import kb.kb as kb
import os
import shutil

router_admin = Router()


@router_admin.message(Command('admin'))
async def main_fun(msg: Message, state: FSMContext):
    bot_msg = await msg.answer(tt.text_admin)
    await state.set_state(ALL_STATE.admin)

    data.msg_data.msg_id = bot_msg.message_id


@router_admin.message(F.text, ALL_STATE.admin)
async def verify(msg: Message, state: FSMContext):
    await data.delet_msg(msg)
    if str(msg.text) == '5500':
        bot_msg = await msg.answer(tt.text_to_all, reply_markup=kb.admin_key)
        await state.set_state(ALL_STATE.all_rules)

    else:
        await msg.answer(tt.text_uncor_password)
        await state.clear()
        bot_msg = await msg.answer(tt.start_text, reply_markup=Storage.create_keyboards_start())
        await state.set_state(ALL_STATE.main)

    data.msg_data.msg_id = bot_msg.message_id

@router_admin.callback_query(F.data == "load", ALL_STATE.all_rules)
async def load(clbk: CallbackQuery, state : FSMContext):
    print("qewqweqwqweqweqew ")
    await data.delet(clbk)
    Storage.download("Lavka", "wb_admin")
    bot_msg = await clbk.message.answer("Текста и изображения загружены")
    data.msg_data.msg_id = bot_msg.message_id

@router_admin.callback_query(F.data == 'verify', ALL_STATE.all_rules)
async def checking(clbk: CallbackQuery, state: FSMContext):
    await data.delet(clbk)
    bot_msg = await clbk.message.answer("Наберите пожалуйста id пользователя из таблицы таким образов (id, Верно) только без скобок и с 1 запятой ТОЛЬКО в этом случае я смогу этому пользователю отправить его данные на проверку")
    data.msg_data.msg_id = bot_msg.message_id
    await state.set_state(ALL_STATE.admin_user)

