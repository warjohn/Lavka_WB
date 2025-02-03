import asyncio
from time import sleep

import aiogram.exceptions
from Tools.scripts.objgraph import printundef
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, InputMediaPhoto, InputFile
from aiogram.types.callback_query import CallbackQuery

import text.text as tt
import routers.utils.data as data
from kb.kb import market_key
from routers.utils.State import ALL_STATE
from routers.utils.Storage import Storage
import kb.kb as kb
from routers.utils.data import msg_image, MainStorage, val_data
from aiogram.utils.media_group import MediaGroupBuilder
import os


router_kat = Router()

global buttons_index_goods # - индекс строки товара
global buttons_index_id_goods # - индекс столбика торва то есть это координаты
global bot_album_id


@router_kat.callback_query(lambda c: True, ALL_STATE.main)
async def qew(clbk: CallbackQuery, state: FSMContext):
    global buttons_index_goods
    global buttons_index_id_goods
    if MainStorage(clbk.from_user.id).market_place == "wb":
        print("wb")
        await data.delet(clbk)
        buttons_index_goods = clbk.data.split('_')[1]
        print(buttons_index_goods)

        folder_path = f"imagesfor_view/kat_{int(buttons_index_goods)}"

        key = next((k for k, v in MainStorage().dict_kat.items() if v == f"kat_{int(buttons_index_goods)}"), None)
        filtered_df = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 0] == key)].reset_index(drop=True)

        print(filtered_df)

        min_file = min(os.listdir(folder_path), key=lambda x: int(x.split('_')[1].split('.')[0]))
        index = min_file.split('_')[1].split('.')[0]
        buttons_index_id_goods = index
        print("index\t", index)
        df = filtered_df.iloc[int(index)]
        print("df\t", df)
        # Проверяем, что индекс существует в filtered_df
        product = df['Товар']
        val_data.val = product
        print("product\t", product)
        price = df['цена']
        print("price\t", price)
        stock = df['Остаток для заказа с кэшбеком']
        print("stock\t", stock)
        compensation = df['% компенсации']
        print("compensation\t", compensation)
        MainStorage(clbk.from_user.id).way = df['Способ продвижения']
        MainStorage(clbk.from_user.id).key = key
        MainStorage(clbk.from_user.id).goods_index = int(index)

        # Формируем строку с вашим текстом и подставляем значения
        result_string = f"Название товара: {product}\nСтоимость на сайте: {price} руб.\nОстаток для заказа с кэшбеком: {stock}\nКомпенсация: {compensation}% в течение 15 дней после получения товара.."

        min_file_path = os.path.join(folder_path, min_file)
        file = FSInputFile(min_file_path)

        bot_msg = await clbk.bot.send_photo(
            clbk.message.chat.id,
            photo=file,
            reply_markup=kb.choose_way(clbk.from_user.id),
            caption=result_string,
        )
        data.msg_data.msg_id = bot_msg.message_id
        await state.set_state(ALL_STATE.anketa)
    else:
        print("ozon")
        await data.delet(clbk)
        buttons_index_goods = clbk.data.split('_')[1]
        print(buttons_index_goods)

        folder_path = f"imagesfor_view_ozon/kat_{int(buttons_index_goods)}"

        key = next((k for k, v in MainStorage().dict_kat_ozon.items() if v == f"kat_{int(buttons_index_goods)}"), None)
        filtered_df = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 0] == key)].reset_index(drop=True)

        print(filtered_df)

        min_file = min(os.listdir(folder_path), key=lambda x: int(x.split('_')[1].split('.')[0]))
        index = min_file.split('_')[1].split('.')[0]
        buttons_index_id_goods = index
        print("index\t", index)
        df = filtered_df.iloc[int(index)]
        print("df\t", df)
        # Проверяем, что индекс существует в filtered_df
        product = df['Товар']
        val_data.val = product
        print("product\t", product)
        price = df['цена']
        print("price\t", price)
        stock = df['Остаток для заказа с кэшбеком']
        print("stock\t", stock)
        compensation = df['% компенсации']
        print("compensation\t", compensation)
        MainStorage(clbk.from_user.id).way = df['Способ продвижения']
        MainStorage(clbk.from_user.id).key = key
        MainStorage(clbk.from_user.id).goods_index = int(index)


        # Формируем строку с вашим текстом и подставляем значения
        result_string = f"Название товара: {product}\nСтоимость на сайте: {price} руб.\nОстаток для заказа с кэшбеком: {stock}\nКомпенсация: {compensation}% в течение 15 дней после получения товара.."

        min_file_path = os.path.join(folder_path, min_file)
        file = FSInputFile(min_file_path)

        bot_msg = await clbk.bot.send_photo(
            clbk.message.chat.id,
            photo=file,
            reply_markup=kb.choose_way(clbk.from_user.id),
            caption=result_string,
        )
        data.msg_data.msg_id = bot_msg.message_id
        await state.set_state(ALL_STATE.anketa)


@router_kat.callback_query(F.data == "next", ALL_STATE.anketa)
@router_kat.callback_query(F.data == "prev", ALL_STATE.anketa)
async def eqw(clbk: CallbackQuery, state: FSMContext):
    global buttons_index_id_goods
    if MainStorage(clbk.from_user.id).market_place == "wb":

        print(buttons_index_id_goods) #id картинки
        print(buttons_index_goods) #id категории

        if clbk.data == "next":
            folder_path = f"imagesfor_view/kat_{buttons_index_goods}"
            image_files = [f for f in os.listdir(folder_path) if f.startswith("image_") and f.endswith(".jpg")]

            if not image_files:
                Flag = False

            image_indices = sorted(int(f.split('_')[1].split('.')[0]) for f in image_files)
            print(image_indices)
            if len(image_indices) == 1:
                filename = f"image_{image_indices[0]}.jpg"
                next_image_path = os.path.join(folder_path, filename)
                await clbk.answer("В этой категории только 1 товар, в ближайшее время появятся новые - следите за обновалениями")
                return
            else:
                current_position = image_indices.index(int(buttons_index_id_goods))
                print(current_position)
                # Переход к следующему (или первому, если конец списка)
                try:
                    next_value = image_indices[current_position + 1]
                    print("next_value", next_value)
                except IndexError as e:
                    next_value = image_indices[0]
                # Если текущий индекс не найден, начинаем с самого первого
                print(next_value)
                filename = f"image_{next_value}.jpg"

                print("\t\t\t\t\t\t\tfilename  ", filename)
                next_image_path = os.path.join(folder_path, filename)

            key = next((k for k, v in MainStorage().dict_kat.items() if v == f"kat_{int(buttons_index_goods)}"), None)
            filtered_df = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 0] == key)].reset_index(drop=True)
            df = filtered_df.iloc[int(next_value)]

            if df['Количество'] == "0":
                bot_msg = await clbk.message.answer(text = """
                <b>Товар закончился:</b> К сожалению, на сегодня кешбэки данного товара все розданы, попробуйте зайти завтра или нажмите на кнопку ниже и выберите другой товар или магазин, либо попробуйте позже, возможно, кто-то из пользователей откажется от покупки товара.
                """,
                reply_markup=kb.market_key)
                data.msg_data.msg_id = bot_msg.message_id
                await state.set_state(ALL_STATE.market)
                return
            else:

                min_file = filename
                index = min_file.split('_')[1].split('.')[0]
                buttons_index_id_goods = index
                print("index\t", index)
                df = filtered_df.iloc[int(index)]
                print("df\t", df)
                # Проверяем, что индекс существует в filtered_df
                product = df['Товар']
                val_data.val = product
                print("product\t", product)
                price = df['цена']
                print("price\t", price)
                stock = df['Остаток для заказа с кэшбеком']
                print("stock\t", stock)
                compensation = df['% компенсации']
                print("compensation\t", compensation)
                MainStorage(clbk.from_user.id).way = df['Способ продвижения']
                MainStorage(clbk.from_user.id).key = key
                MainStorage(clbk.from_user.id).goods_index = int(index)
                # Формируем строку с вашим текстом и подставляем значения
                result_string = f"Название товара: {product}\nСтоимость на сайте: {price} руб.\nОстаток для заказа с кэшбеком: {stock}\nКомпенсация: {compensation}% в течение 15 дней после получения товара.."

                min_file_path = os.path.join(folder_path, min_file)
                file = InputMediaPhoto(media = FSInputFile(min_file_path), caption = result_string)

                await clbk.bot.edit_message_media(media = file, chat_id = clbk.message.chat.id, message_id = data.msg_data.msg_id, reply_markup = kb.choose_way(clbk.from_user.id))

        else:
            folder_path = f"imagesfor_view/kat_{buttons_index_goods}"
            image_files = [f for f in os.listdir(folder_path) if f.startswith("image_") and f.endswith(".jpg")]

            if not image_files:
                Flag = False

            image_indices = sorted(int(f.split('_')[1].split('.')[0]) for f in image_files)
            print(image_indices)
            if len(image_indices) == 1:
                filename = f"image_{image_indices[0]}.jpg"
                next_image_path = os.path.join(folder_path, filename)
                await clbk.answer("В этой категории только 1 товар, в ближайшее время появятся новые - следите за обновалениями")
                return
            else:
                current_position = image_indices.index(int(buttons_index_id_goods))
                print(current_position)
                # Переход к следующему (или первому, если конец списка)
                try:
                    next_value = image_indices[current_position - 1]
                    print("next_value", next_value)
                except IndexError as e:
                    next_value = image_indices[0]
                # Если текущий индекс не найден, начинаем с самого первого
                print(next_value)
                filename = f"image_{next_value}.jpg"

                print("\t\t\t\t\t\t\tfilename  ", filename)
                next_image_path = os.path.join(folder_path, filename)

            key = next((k for k, v in MainStorage().dict_kat.items() if v == f"kat_{int(buttons_index_goods)}"), None)
            filtered_df = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 0] == key)].reset_index(drop=True)
            df = filtered_df.iloc[int(next_value)]

            if df['Количество'] == 0:
                bot_msg = await clbk.message.answer(text = """
                <b>Товар закончился:</b> К сожалению, на сегодня кешбэки данного товара все розданы, попробуйте зайти завтра или нажмите на кнопку ниже и выберите другой товар или магазин, либо попробуйте позже, возможно, кто-то из пользователей откажется от покупки товара.
                """,
                reply_markup=kb.market_key)
                data.msg_data.msg_id = bot_msg.message_id
                await state.set_state(ALL_STATE.market)
                return
            else:

                min_file = filename
                index = min_file.split('_')[1].split('.')[0]
                buttons_index_id_goods = index
                print("index\t", index)
                df = filtered_df.iloc[int(index)]
                print("df\t", df)
                # Проверяем, что индекс существует в filtered_df
                product = df['Товар']
                val_data.val = product
                print("product\t", product)
                price = df['цена']
                print("price\t", price)
                stock = df['Остаток для заказа с кэшбеком']
                print("stock\t", stock)
                compensation = df['% компенсации']
                print("compensation\t", compensation)
                MainStorage(clbk.from_user.id).way = df['Способ продвижения']
                MainStorage(clbk.from_user.id).key = key
                MainStorage(clbk.from_user.id).goods_index = int(index)
                # Формируем строку с вашим текстом и подставляем значения
                result_string = f"Название товара: {product}\nСтоимость на сайте: {price} руб.\nОстаток для заказа с кэшбеком: {stock}\nКомпенсация: {compensation}% в течение 15 дней после получения товара.."

                min_file_path = os.path.join(folder_path, min_file)
                file = InputMediaPhoto(media = FSInputFile(min_file_path), caption = result_string)

                await clbk.bot.edit_message_media(media = file, chat_id = clbk.message.chat.id, message_id = data.msg_data.msg_id, reply_markup = kb.choose_way(clbk.from_user.id))

    else:
        print(buttons_index_id_goods)  # id картинки
        print(buttons_index_goods)  # id категории

        if clbk.data == "next":
            folder_path = f"imagesfor_view_ozon/kat_{buttons_index_goods}"
            image_files = [f for f in os.listdir(folder_path) if f.startswith("image_") and f.endswith(".jpg")]

            if not image_files:
                Flag = False

            image_indices = sorted(int(f.split('_')[1].split('.')[0]) for f in image_files)
            print(image_indices)
            if len(image_indices) == 1:
                filename = f"image_{image_indices[0]}.jpg"
                next_image_path = os.path.join(folder_path, filename)
                await clbk.answer(
                    "В этой категории только 1 товар, в ближайшее время появятся новые - следите за обновалениями")
                return
            else:
                current_position = image_indices.index(int(buttons_index_id_goods))
                print(current_position)
                # Переход к следующему (или первому, если конец списка)
                try:
                    next_value = image_indices[current_position + 1]
                    print("next_value", next_value)
                except IndexError as e:
                    next_value = image_indices[0]
                # Если текущий индекс не найден, начинаем с самого первого
                print(next_value)
                filename = f"image_{next_value}.jpg"

                print("\t\t\t\t\t\t\tfilename  ", filename)
                next_image_path = os.path.join(folder_path, filename)

            key = next((k for k, v in MainStorage().dict_kat_ozon.items() if v == f"kat_{int(buttons_index_goods)}"), None)
            filtered_df = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 0] == key)].reset_index(drop=True)
            df = filtered_df.iloc[int(next_value)]

            if df['Количество'] == 0:
                bot_msg = await clbk.message.answer(text="""
                        <b>Товар закончился:</b> К сожалению, на сегодня кешбэки данного товара все розданы, попробуйте зайти завтра или нажмите на кнопку ниже и выберите другой товар или магазин, либо попробуйте позже, возможно, кто-то из пользователей откажется от покупки товара.
                        """,
                                                    reply_markup=kb.market_key)
                data.msg_data.msg_id = bot_msg.message_id
                await state.set_state(ALL_STATE.market)
            else:

                min_file = filename
                index = min_file.split('_')[1].split('.')[0]
                buttons_index_id_goods = index
                print("index\t", index)
                df = filtered_df.iloc[int(index)]
                print("df\t", df)
                # Проверяем, что индекс существует в filtered_df
                product = df['Товар']
                val_data.val = product
                print("product\t", product)
                price = df['цена']
                print("price\t", price)
                stock = df['Остаток для заказа с кэшбеком']
                print("stock\t", stock)
                compensation = df['% компенсации']
                print("compensation\t", compensation)
                MainStorage(clbk.from_user.id).way = df['Способ продвижения']
                MainStorage(clbk.from_user.id).key = key
                MainStorage(clbk.from_user.id).goods_index = int(index)
                # Формируем строку с вашим текстом и подставляем значения
                result_string = f"Название товара: {product}\nСтоимость на сайте: {price} руб.\nОстаток для заказа с кэшбеком: {stock}\nКомпенсация: {compensation}% в течение 15 дней после получения товара.."

                min_file_path = os.path.join(folder_path, min_file)
                file = InputMediaPhoto(media=FSInputFile(min_file_path), caption=result_string)

                await clbk.bot.edit_message_media(media=file, chat_id=clbk.message.chat.id,
                                                  message_id=data.msg_data.msg_id, reply_markup=kb.choose_way(clbk.from_user.id))

        else:
            folder_path = f"imagesfor_view_ozon/kat_{buttons_index_goods}"
            image_files = [f for f in os.listdir(folder_path) if f.startswith("image_") and f.endswith(".jpg")]

            if not image_files:
                Flag = False

            image_indices = sorted(int(f.split('_')[1].split('.')[0]) for f in image_files)
            print(image_indices)
            if len(image_indices) == 1:
                filename = f"image_{image_indices[0]}.jpg"
                next_image_path = os.path.join(folder_path, filename)
                await clbk.answer(
                    "В этой категории только 1 товар, в ближайшее время появятся новые - следите за обновалениями")
                return
            else:
                current_position = image_indices.index(int(buttons_index_id_goods))
                print(current_position)
                # Переход к следующему (или первому, если конец списка)
                try:
                    next_value = image_indices[current_position - 1]
                    print("next_value", next_value)
                except IndexError as e:
                    next_value = image_indices[0]
                # Если текущий индекс не найден, начинаем с самого первого
                print(next_value)
                filename = f"image_{next_value}.jpg"

                print("\t\t\t\t\t\t\tfilename  ", filename)
                next_image_path = os.path.join(folder_path, filename)

            key = next((k for k, v in MainStorage().dict_kat_ozon.items() if v == f"kat_{int(buttons_index_goods)}"), None)
            filtered_df = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 0] == key)].reset_index(drop=True)
            df = filtered_df.iloc[int(next_value)]

            if df['Количество'] == 0:
                bot_msg = await clbk.message.answer(text="""
                        <b>Товар закончился:</b> К сожалению, на сегодня кешбэки данного товара все розданы, попробуйте зайти завтра или нажмите на кнопку ниже и выберите другой товар или магазин, либо попробуйте позже, возможно, кто-то из пользователей откажется от покупки товара.
                        """,
                                                    reply_markup=kb.market_key)
                data.msg_data.msg_id = bot_msg.message_id
                await state.set_state(ALL_STATE.market)
            else:

                min_file = filename
                index = min_file.split('_')[1].split('.')[0]
                buttons_index_id_goods = index
                print("index\t", index)
                df = filtered_df.iloc[int(index)]
                print("df\t", df)
                # Проверяем, что индекс существует в filtered_df
                product = df['Товар']
                val_data.val = product
                print("product\t", product)
                price = df['цена']
                print("price\t", price)
                stock = df['Остаток для заказа с кэшбеком']
                print("stock\t", stock)
                compensation = df['% компенсации']
                print("compensation\t", compensation)
                MainStorage(clbk.from_user.id).way = df['Способ продвижения']
                MainStorage(clbk.from_user.id).key = key
                MainStorage(clbk.from_user.id).goods_index = int(index)
                # Формируем строку с вашим текстом и подставляем значения
                result_string = f"Название товара: {product}\nСтоимость на сайте: {price} руб.\nОстаток для заказа с кэшбеком: {stock}\nКомпенсация: {compensation}% в течение 15 дней после получения товара.."

                min_file_path = os.path.join(folder_path, min_file)
                file = InputMediaPhoto(media=FSInputFile(min_file_path), caption=result_string)

                await clbk.bot.edit_message_media(media=file, chat_id=clbk.message.chat.id,
                                                  message_id=data.msg_data.msg_id, reply_markup=kb.choose_way(clbk.from_user.id))



