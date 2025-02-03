import asyncio

import aiogram.exceptions
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.types.callback_query import CallbackQuery
from pandas.plotting import table

import text.text as tt
import routers.utils.data as data
from kb.kb import number_key
from routers.utils.State import ALL_STATE, Anketa_state_key, Anketa_state_other
from routers.utils.Storage import Storage
import kb.kb as kb
from routers.utils.checker import InactivityChecker
from routers.utils.data import delet, val_data, delet_msg, MainStorage
import os

router_anketa = Router()
TABLE_NAME = "Lavka"


@router_anketa.callback_query(F.data == "key_word", ALL_STATE.anketa)
async def start(clbk: CallbackQuery, state: FSMContext):
    check = InactivityChecker(useername=clbk.from_user.username)
    check.update_activity(clbk.from_user.id)
    await delet(clbk)
    if MainStorage(clbk.from_user.id).market_place == "wb":
        market = "WILDBERRIES"
        filtered_df = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 0] == MainStorage(clbk.from_user.id).key)].reset_index(drop=True)
        filtered_df = filtered_df.iloc[int(MainStorage(clbk.from_user.id).goods_index)]
        Storage.download_examples(TABLE_NAME, MainStorage(clbk.from_user.id).market_place, filtered_df['пример фото'], int(MainStorage(clbk.from_user.id).goods_index))
    else:
        market = "OZON"
        filtered_df = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 0] == MainStorage(clbk.from_user.id).key)].reset_index(drop=True)
        filtered_df = filtered_df.iloc[int(MainStorage(clbk.from_user.id).goods_index)]
        Storage.download_examples(TABLE_NAME, MainStorage(clbk.from_user.id).market_place, filtered_df['пример фото'], int(MainStorage(clbk.from_user.id).goods_index))
    print("filtered_df", filtered_df)
    if filtered_df['Количество'] == "0":
        bot_msg = await clbk.message.answer(text="""
        <b>Товар закончился:</b> К сожалению, на сегодня кешбэки данного товара все розданы, попробуйте зайти завтра или нажмите на кнопку ниже и выберите другой товар или магазин, либо попробуйте позже, возможно, кто-то из пользователей откажется от покупки товара.
        """,
                                            reply_markup=kb.market_key)
        data.msg_data.msg_id = bot_msg.message_id
        await state.set_state(ALL_STATE.market)
        MainStorage.clear_instance(clbk.from_user.id)
        return

    Storage.add_data("Lavka", MainStorage(clbk.from_user.id).market_place, val_data.val, clbk.from_user.id, clbk.from_user.username)

    bot_msg = await clbk.message.answer_photo(
        FSInputFile(f"temp_images/image_example_{int(MainStorage(clbk.from_user.id).goods_index)}.jpg"),
        caption = f"""В поисковой строке {market} введите “{filtered_df['Запрос для продвижения']}” и фильтр “{filtered_df['Фильтры (не обязательное поле)']}” и пришлите скрин, где виден запрос и наш товар. \n\nПример правильного скриншота☝️\nПостарайтесь в одном скриншоте зафиксировать всю информацию)\n\nНайдите товар в течение 15 минут. Если не отправляете скриншот, бот приостанавливает работу.
                    """)
    os.remove(f"temp_images/image_example_{int(MainStorage(clbk.from_user.id).goods_index)}.jpg")
    await state.set_state(Anketa_state_key.one)

@router_anketa.callback_query(F.data == "throw_the_other", ALL_STATE.anketa)
async def start_w(clbk: CallbackQuery, state: FSMContext):
    check = InactivityChecker(useername=clbk.from_user.username)
    check.update_activity(clbk.from_user.id)
    await delet(clbk)

    if MainStorage(clbk.from_user.id).market_place == "wb":
        market = "WILDBERRIES"
        filtered_df = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 0] == MainStorage(clbk.from_user.id).key)].reset_index(drop=True)
        filtered_df = filtered_df.iloc[int(MainStorage(clbk.from_user.id).goods_index)]
        Storage.download_examples(TABLE_NAME,  "wb_admin", filtered_df['пример фото'], int(MainStorage(clbk.from_user.id).goods_index))

    else:
        market = "OZON"
        filtered_df = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 0] == MainStorage(clbk.from_user.id).key)].reset_index(drop=True)
        filtered_df = filtered_df.iloc[int(MainStorage(clbk.from_user.id).goods_index)]
        Storage.download_examples(TABLE_NAME,  "ozon_admin", filtered_df['пример фото'], int(MainStorage(clbk.from_user.id).goods_index))

    Storage.add_data("Lavka", MainStorage(clbk.from_user.id).market_place, val_data.val, clbk.from_user.id, clbk.from_user.username)
    bot_msg = await clbk.message.answer_photo(
        FSInputFile(f"temp_images/image_example_{int(MainStorage(clbk.from_user.id).goods_index)}.jpg"),
        caption = f"""В поисковой строке {market} введите “{filtered_df['Запрос для продвижения']}” и фильтр “{filtered_df['Фильтры (не обязательное поле)']}” и пришлите скрин, где виден запрос и товар конкурента, который выделен на скриншоте.\n\nПример правильного скриншота (выделять карточку конкурента не нужно)☝️\n\nНайдите товар в течение 15 минут. Если не отправляете скриншот, бот приостанавливает работу.
""")
    os.remove(f"temp_images/image_example_{int(MainStorage(clbk.from_user.id).goods_index)}.jpg")
    await state.set_state(Anketa_state_other.one)

#fun_1

@router_anketa.message(F.photo, Anketa_state_key.one)
async def one(msg: Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            local_oath = await download_image(msg)
            print('local_oath', local_oath)
            image_url = f"https://drive.google.com/uc?id={Storage.upload_file(local_path=local_oath)}"
            print(val_data.val)

            Storage.add_image(table_name=TABLE_NAME, sheet_name=MainStorage(msg.from_user.id).market_place, image_url=image_url,
                                  user_id=msg.from_user.id, product_name=val_data.val, column_index=4)
            print(msg.photo)
            print("true")
            os.remove(local_oath)
            if MainStorage(msg.from_user.id).market_place == "wb":
                filtered_df = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 0] == MainStorage(msg.from_user.id).key)].reset_index(
                    drop=True)
                filtered_df = filtered_df.iloc[int(MainStorage(msg.from_user.id).goods_index)]
            else:
                filtered_df = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 0] == MainStorage(msg.from_user.id).key)].reset_index(
                    drop=True)
                filtered_df = filtered_df.iloc[int(MainStorage(msg.from_user.id).goods_index)]
            bot_msg = await msg.answer(
                text=f"""Отлично, спасибо! Зайдите в эту карточку товара, пролистайте вниз и среди рекомендуемых товаров выберите и напишите артикул найденного товара: найти его можно в характеристиках товара (под названием игры нажмите ссылку “о товаре”)""")
            await state.set_state(Anketa_state_key.betwen)
        else:
            await msg_qwe(msg, state)

@router_anketa.message(F.photo, Anketa_state_other.one)
async def one(msg: Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            local_oath = await download_image(msg)
            print('local_oath', local_oath)
            image_url = f"https://drive.google.com/uc?id={Storage.upload_file(local_path=local_oath)}"
            print(val_data.val)

            Storage.add_image(table_name=TABLE_NAME, sheet_name=MainStorage(msg.from_user.id).market_place, image_url=image_url,
                                  user_id=msg.from_user.id, product_name=val_data.val, column_index=4)
            print(msg.photo)
            print("true")
            os.remove(local_oath)
            if MainStorage(msg.from_user.id).market_place == "wb":
                filtered_df = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 0] == MainStorage(msg.from_user.id).key)].reset_index(
                    drop=True)
                filtered_df = filtered_df.iloc[int(MainStorage(msg.from_user.id).goods_index)]
                Storage.download_examples(TABLE_NAME,  "wb_admin", filtered_df['пример фото'], int(MainStorage(msg.from_user.id).goods_index))
            else:
                filtered_df = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 0] == MainStorage(msg.from_user.id).key)].reset_index(
                    drop=True)
                filtered_df = filtered_df.iloc[int(MainStorage(msg.from_user.id).goods_index)]
                Storage.download_examples(TABLE_NAME,  "ozon_admin", filtered_df['пример фото'], int(MainStorage(msg.from_user.id).goods_index))
            bot_msg = await msg.answer_photo(
                FSInputFile(f"temp_images/image_example_{int(MainStorage(msg.from_user.id).goods_index)}.jpg"),
                caption=f"""Отлично, спасибо! Зайдите в эту карточку товара, пролистайте вниз и среди рекомендуемых товаров выберите и напишите артикул найденного товара: найти его можно в характеристиках товара (под названием игры нажмите ссылку “о товаре”)""")
            os.remove(f"temp_images/image_example_{int(MainStorage(msg.from_user.id).goods_index)}.jpg")
            await state.set_state(Anketa_state_key.betwen)
        else:
            await msg_qwe(msg, state)


@router_anketa.message(F.photo, Anketa_state_key.one)
async def one_k(msg: Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            local_oath = await download_image(msg)
            print('local_oath', local_oath)
            image_url = f"https://drive.google.com/uc?id={Storage.upload_file(local_path=local_oath)}"
            print(val_data.val)
            Storage.add_image(table_name= TABLE_NAME,sheet_name= MainStorage(msg.from_user.id).market_place,image_url= image_url,user_id= msg.from_user.id,product_name= val_data.val, column_index = 4)
            print(msg.photo)
            print("true")
            os.remove(local_oath)

            bot_msg = await msg.answer(text = """Отлично, спасибо! Теперь найдите артикул товара и отправьте его нам. Найти его можно в характеристиках товара (под названием игры нажмите ссылку “о товаре”)\nОтправьте артикул в течение 15 минут. Если не отправляете, бот приостанавливает работу.
    """)
            await state.set_state(Anketa_state_key.betwen)
        else:
            await msg_qwe(msg, state)

@router_anketa.message(F.text, Anketa_state_key.betwen)
async def check_airticle(msg : Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            await delet_msg(msg)
            if not msg.text.isdigit():
                await msg.answer("Введите пожалуйста артикул товара цифрами")
                return
            if MainStorage(msg.from_user.id).market_place == "wb":
                filtered_df = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 0] == MainStorage(msg.from_user.id).key)].reset_index(
                    drop=True)
                filtered_df = filtered_df.iloc[int(MainStorage(msg.from_user.id).goods_index)]
            else:
                filtered_df = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 0] == MainStorage(msg.from_user.id).key)].reset_index(
                    drop=True)
                filtered_df = filtered_df.iloc[int(MainStorage(msg.from_user.id).goods_index)]
            if int(filtered_df['Артикул товара']) == int(msg.text):
                bot_msg = await msg.answer(text = """Прекрасно! Задержитесь, пожалуйста, на минутку в карточке товара, полистайте фото и отзывы ( это важно😊). Теперь положите товар в корзину, оформите заказ. Как только завершите, пришлите скриншот с подтверждением оформления заказа.\nЗакажите товар в течение 15 минут. Если не отправляете скриншот, бот приостанавливает работу.
                                                    """)
                data.msg_data.msg_id = bot_msg.message_id
            else:
                bot_msg = await msg.answer(text="""К сожалению, вы нашли не тот товар. Пожалуйста, посмотрите внимательно на фото и найдите товар с именно такой картинкой. Отправьте артикул товара.""")
                data.msg_data.msg_id = bot_msg.message_id
                return
            await state.set_state(Anketa_state_key.two)
        else:
            await msg_qwe(msg, state)

@router_anketa.message(F.photo, Anketa_state_key.two)
async def one_k(msg: Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            local_oath = await download_image(msg)
            print('local_oath', local_oath)
            image_url = f"https://drive.google.com/uc?id={Storage.upload_file(local_path=local_oath)}"
            print(val_data.val)
            if MainStorage(msg.from_user.id).market_place == "wb":
                matched_row = MainStorage().alL_table[(MainStorage().alL_table.iloc[:, 1] == val_data.val)]
            else:
                matched_row = MainStorage().alL_table_ozon[(MainStorage().alL_table_ozon.iloc[:, 1] == val_data.val)]
            print("matched_row", matched_row.index[0])
            Storage.update_table(matched_row.index[0], 'Количество')
            Storage.add_image(table_name= TABLE_NAME,sheet_name= MainStorage(msg.from_user.id).market_place,image_url= image_url,user_id= msg.from_user.id,product_name= val_data.val, column_index = 5)
            print(msg.photo)
            print("true")
            os.remove(local_oath)
            bot_msg = await msg.answer(text = 'Спасибо! Для перевода по СБП введите ваш номер телефона либо нажмите на кнопку "Отправить номер"✅Внизу кнопка отправить номер', reply_markup = number_key)
            await state.set_state(Anketa_state_key.three)
        else:
            await msg_qwe(msg, state)

@router_anketa.message(F.text, Anketa_state_key.three)
@router_anketa.message(F.contact, Anketa_state_key.three)
async def number(msg : Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            Storage.add_data_personal(str(msg.from_user.id))
            if msg.contact.phone_number:
                Storage.add_number(str(msg.from_user.id), str(msg.contact.phone_number), 2)
            else:
                Storage.add_number(str(msg.from_user.id), str(msg.text), 2)
            bot_msg = await msg.answer("Ваш банк", reply_markup = ReplyKeyboardRemove())
            await state.set_state(Anketa_state_key.four)
        else:
            await msg_qwe(msg, state)


@router_anketa.message(F.text, Anketa_state_key.four)
async def bank(msg: Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            Storage.add_number(str(msg.from_user.id), str(msg.text), 3)
            bot_msg = await msg.answer("Напишите ваши Фамилию Имя Отчество одним сообщением")
            await state.set_state(Anketa_state_key.five)
        else:
            await msg_qwe(msg, state)


@router_anketa.message(F.text, Anketa_state_key.five)
async def bank(msg: Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            Storage.add_number(str(msg.from_user.id), str(msg.text), 4)
            bot_msg = await msg.answer("""Отлично, ваши реквизиты зафиксированы\nКак только получите заказ жмите кнопку "Получил"\n\nВАЖНО! Датой выкупа товара является дата отправки QR кода полученного товара.\n<b>❗Пожалуйста, не нажимайте на кнопку,</b> пока не получите товар, иначе настройки бота собьются и бот не сможет перевести вам кэшбек❗\n\nЕсли, все же, настройки сбились, обратитесь за помощью к ..
    """, reply_markup = kb.get_key)
            await state.set_state(Anketa_state_key.six)
        else:
            await msg_qwe(msg, state)

@router_anketa.callback_query(F.data == "get", Anketa_state_key.six)
async def get_goods(clbk: CallbackQuery, state: FSMContext):
        check = InactivityChecker(useername=clbk.from_user.username)
        check.update_activity(clbk.from_user.id)
        if MainStorage(clbk.from_user.id).market_place == "wb":
            bot_msg = await clbk.message.answer_photo(
                FSInputFile("qr_images/78c507fba6fa0e17863c12552d87d22b.png"),
                caption=f"""Пришлите фото с разрезанным Qr кодом Вайлдберриз (по нему мы узнаем, выкуплен ли товар и не было ли возврата)\nПример корректного фото ☝️""")
        else:
            bot_msg = await clbk.message.answer_photo(
                FSInputFile("qr_images/qr-code.png"),
                caption=f"""Пришлите фото с разрезанным Qr кодом Озона (по нему мы узнаем, выкуплен ли товар и не было ли возврата)\nПример корректного фото ☝️""")
        await state.set_state(Anketa_state_key.seven)


@router_anketa.message(F.photo, Anketa_state_key.seven)
async def qr_photo(msg: Message, state: FSMContext):
        check = InactivityChecker(useername=msg.from_user.username)
        check.update_activity(msg.from_user.id)
        qwe = check.user_status[msg.from_user.id]
        if qwe == True:
            local_oath = await download_image(msg)
            print('local_oath', local_oath)
            image_url = f"https://drive.google.com/uc?id={Storage.upload_file(local_path=local_oath)}"
            print(val_data.val)
            Storage.add_image(table_name= TABLE_NAME,sheet_name= MainStorage(msg.from_user.id).market_place,image_url= image_url,user_id= msg.from_user.id,product_name= val_data.val, column_index = 6)
            print(msg.photo)
            print("true")
            os.remove(local_oath)
            qwe = Storage.get_data_user(str(msg.from_user.id))
            bot_msg = await msg.answer(text=f"""Прекрасно!\nВам будет осуществлена выплата не позднее …...2024\nВаш номер: {qwe[1]}\nБанк: {qwe[2]}\nФИО: {qwe[3]}\n\nПодтверждаете? 
                """, reply_markup=kb.admin_1_key)

            await state.set_state(Anketa_state_key.nine)
        else:
            await msg_qwe(msg, state)


@router_anketa.callback_query(F.data == "not_all_right", Anketa_state_key.ten)
@router_anketa.callback_query(F.data == "all_right", Anketa_state_key.ten)
@router_anketa.callback_query(F.data, Anketa_state_key.nine)
async def corecction(clbk: CallbackQuery, state: FSMContext):
    print("state.get_state()", await state.get_state())
    if await state.get_state() == "Anketa_state_key:nine":
        if clbk.data == "all_right":
            Storage.add_number(str(clbk.from_user.id), "Подтверждено", 5)
            await clbk.message.answer("Спасибо что выбрали нас!)\nВ скором времени наши администраторы проверят ваши данные и если все хорошо отправят кешбэк")
        else:
            bot_msg = await clbk.message.answer("Введите новые данные таким образом -> номер телефона, банк, ФИО")
    else:
        if clbk.data == "all_right":
            MainStorage(clbk.from_user.id).new_user_data.insert(0, str(clbk.from_user.id))
            MainStorage(clbk.from_user.id).new_user_data.append("Подтверждено")
            Storage.update_row(str(clbk.from_user.id), MainStorage(clbk.from_user.id).new_user_data)
            await clbk.message.answer("Спасибо что выбрали нас!)\nВ скором времени наши администраторы проверят ваши данные и если все хорошо отправят кешбэк")
        else:
            bot_msg = await clbk.message.answer("Введите новые данные таким образом -> номер телефона, банк, ФИО")

    await state.set_state(Anketa_state_key.ten)

@router_anketa.message(F.text, Anketa_state_key.ten)
async def change(msg : Message, state : FSMContext):
     MainStorage(msg.from_user.id).new_user_data = msg.text.split(',')
     bot_msg = await msg.answer(text=f"""Прекрасно!\nВам будет осуществлена выплата не позднее …...2024\nВаш номер: {MainStorage(msg.from_user.id).new_user_data[0]}\nБанк: {MainStorage(msg.from_user.id).new_user_data[1]}\nФИО: {MainStorage(msg.from_user.id).new_user_data[2]}\n\nПодтверждаете? 
         """, reply_markup=kb.admin_1_key)






async def download_image(msg: Message):
    file_info = await msg.bot.get_file(msg.photo[-1].file_id)  # Получаем наибольший размер изображения
    file_path = file_info.file_path

        # Скачиваем файл
    file = await msg.bot.download_file(file_path)

    # Сохраняем локально
    local_path = f"downloads/{msg.photo[-1].file_id}.jpg"
    os.makedirs("downloads", exist_ok=True)
    with open(local_path, 'wb') as f:
        f.write(file.read())
    print("local_path \t", local_path)
    return local_path

async def msg_qwe(msg, state):
    await msg.answer(text = "Видим, что вы не определились с выбором. Я приостановлю бот, чтобы вы не занимали очередь.\nЕсли вы решите купить наши товары с кешбэком, вы всегда можете перейти к каталогу товаров и выбрать нужный.")
    bot_msg = await msg.answer(tt.start_text_2, reply_markup=kb.market_key)
    await state.set_state(ALL_STATE.market)
    data.msg_data.msg_id = bot_msg.message_id