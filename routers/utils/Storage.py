import csv
import sys

from pydoc import classify_class_attrs
import shutil
import googleapiclient
import requests
from pydantic_core.core_schema import call_schema

import config as cc
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import os
from routers.utils.data import MainStorage
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive



class Storage:

    """main storage class for all data"""

    def __init__(self):
        pass

    @classmethod
    def create_keyboards_start(cls, id):
        try:
            # Подключаемся к таблице
            if MainStorage(id).market_place == "wb":
                table = MainStorage().dict_kat
                print("table_wb", table)
            else:
                table = MainStorage().dict_kat_ozon
                print("table_ozon", table)

            keyboard = InlineKeyboardBuilder()

            # Создаем кнопки для каждого уникального значения в первом столбце
            for key, value in table.items():
                keyboard.row(InlineKeyboardButton(text=str(key), callback_data=str(value)))

            return keyboard.as_markup()
        except AttributeError:
            return InlineKeyboardBuilder().row(InlineKeyboardButton(text="Администратор не загрузид данные((", callback_data='mt')).as_markup()

    @classmethod
    def create_keyboards_from_row(cls, data):
        try:
            # Подключаемся к таблице
            table = MainStorage().columns_onetothre
            key = next((k for k, v in MainStorage().dict_kat.items() if v == data), None)
            # Фильтрация DataFrame для текущей категории kat
            filtered_df = MainStorage().columns_onetothre[
                (MainStorage().columns_onetothre.iloc[:, 0] == key)
            ].reset_index(drop=True)

            column = filtered_df.iloc[:, 1]
            print("column", column)
            keyboard = InlineKeyboardBuilder()

            # Создаем кнопки для каждого значения в строке
            for i, value in enumerate(column):
                keyboard.row(InlineKeyboardButton(text=str(value), callback_data=f'row_{i}'))

            keyboard.row(InlineKeyboardButton(text = "Назад в меню", callback_data = "back"))
            return keyboard.as_markup()
        except IndexError:
            return InlineKeyboardBuilder().row(
                InlineKeyboardButton(text="Нет данных по этому индексу", callback_data='error')).as_markup()
        except AttributeError:
            return InlineKeyboardBuilder().row(
                InlineKeyboardButton(text="Администратор не загрузил данные((", callback_data='mt')).as_markup()

    @classmethod
    def add_data(cls, table_name, sheet_name, values, user_id, nickname):
        sheet = cls.__init_table(table_name, sheet_name)
        print("sheet", sheet)
        # Получаем все значения из листа gspread
        existing_values = sheet.get_all_records()
        print("existing_values", existing_values)

        # Находим первую пустую строку, начиная с 2-й (пропуская заголовки)
        row_to_insert = len(existing_values) + 2  # Изначально предполагаем, что добавим в конец

        # Проверяем строки начиная со 2-й, чтобы найти первую пустую строку
        for i in range(1, len(existing_values)):
            if not any(existing_values[i]):  # Если вся строка пустая
                row_to_insert = i + 2  # Устанавливаем строку для вставки (индекс с учетом заголовков)
                break

        # Записываем данные в ячейки
        sheet.update(f'A{row_to_insert}', [[values, user_id, nickname]])

    @classmethod
    def add_image(cls, table_name, sheet_name, user_id, product_name, image_url, column_index=None):
        # Инициализация таблицы через gspread
        sheet = cls.__init_table(table_name, sheet_name)

        # Получаем все значения из листа gspread
        existing_values = sheet.get_all_values()

        # Преобразуем в DataFrame
        df = pd.DataFrame(existing_values[1:], columns=existing_values[0])  # Первая строка - заголовки

        print(df)

        # Убираем лишние пробелы и приводим к строкам значения столбцов 'id' и 'goods'
        df['id'] = df['id'].astype(str).str.strip()
        df['goods'] = df['goods'].astype(str).str.strip()

        print(df['id'])
        print(df['goods'])

        # Приводим также user_id и product_name к строкам и убираем пробелы
        user_id = str(user_id).strip()
        product_name = str(product_name).strip()

        print("user_id", user_id)
        print("product_name", product_name)

        # Ищем строку по user_id и product_name
        row_to_update = df[(df['id'] == user_id) & (df['goods'] == product_name)]

        print(row_to_update)

        if not row_to_update.empty:
            row_index = row_to_update.index[-1]  # Индекс строки, которую будем обновлять
            print("row_index", row_index)

            if column_index is not None:
                # Проверяем, не выходит ли колонка за пределы существующих
                if column_index > len(df.columns):
                    # Добавляем новую колонку, если выбранный индекс выходит за пределы
                    next_col = f'column_{len(df.columns) + 1}'
                    df[next_col] = None  # Добавляем новую колонку
                    df.at[row_index, next_col] = image_url
                else:
                    # Вставляем изображение в указанную колонку
                    df.iat[row_index, column_index - 1] = image_url  # -1, потому что индексация с 0
            else:
                # Если индекс столбца не передан, ищем первый пустой столбец
                for col in df.columns:
                    if pd.isna(df.at[row_index, col]):  # Проверяем, если колонка пустая
                        df.at[row_index, col] = image_url
                        break
                else:
                    # Если нет пустой ячейки, добавляем в следующую колонку
                    next_col = f'column_{len(df.columns) + 1}'
                    df[next_col] = None  # Добавляем новую колонку
                    df.at[row_index, next_col] = image_url

            # Теперь обновляем Google Таблицу с изменёнными данными
            sheet.update([df.columns.values.tolist()] + df.values.tolist())  # Загрузить обратно
        else:
            print("Пользователь или товар не найдены.")


    @classmethod
    def add_payments(cls, table_name, sheet_name, user_id, product_name, text, column_index=None):
        # Инициализация таблицы через gspread
        sheet = cls.__init_table(table_name, sheet_name)
        print("sheet", sheet)

        # Получаем все значения из листа gspread
        existing_values = sheet.get_all_values()
        print("existing_values", existing_values)

        # Преобразуем в DataFrame
        df = pd.DataFrame(existing_values[1:], columns=existing_values[0])  # Первая строка - заголовки
        print("DataFrame", df)

        # Убираем лишние пробелы и приводим к строкам значения столбцов 'id' и 'goods'
        df['id'] = df['id'].astype(str).str.strip()
        df['goods'] = df['goods'].astype(str).str.strip()

        # Приводим также user_id и product_name к строкам и убираем пробелы
        user_id = str(user_id).strip()
        product_name = str(product_name).strip()
        print("user_id", user_id)
        print("product_name", product_name)

        # Ищем строку по user_id и product_name
        row_to_update = df[(df['id'] == user_id) & (df['goods'] == product_name)]

        if not row_to_update.empty:
            row_index = row_to_update.index[0]  # Индекс строки, которую будем обновлять
            print("row_index", row_index)

            if column_index is not None:
                # Проверяем, не выходит ли колонка за пределы существующих
                if column_index > len(df.columns):
                    # Добавляем новую колонку, если выбранный индекс выходит за пределы
                    next_col = f'column_{len(df.columns) + 1}'
                    df[next_col] = None  # Добавляем новую колонку
                    df.at[row_index, next_col] = text
                else:
                    # Вставляем изображение в указанную колонку
                    df.iat[row_index, column_index - 1] = text  # -1, потому что индексация с 0
            else:
                # Если индекс столбца не передан, ищем первый пустой столбец
                for col in df.columns:
                    if pd.isna(df.at[row_index, col]):  # Проверяем, если колонка пустая
                        df.at[row_index, col] = text
                        break
                else:
                    # Если нет пустой ячейки, добавляем в следующую колонку
                    next_col = f'column_{len(df.columns) + 1}'
                    df[next_col] = None  # Добавляем новую колонку
                    df.at[row_index, next_col] = text

            # Теперь обновляем Google Таблицу с изменёнными данными
            sheet.update([df.columns.values.tolist()] + df.values.tolist())  # Загрузить обратно
        else:
            print("Пользователь или товар не найдены.")

    @classmethod
    def _init_table(cls, table_name, sheet_name):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "data/data.json", scope)
        print("qweqweq_1")
        client = gspread.authorize(creds)
        print("client", client)
        spreadsheet = client.open(table_name)
        print("spreadsheet", spreadsheet)
        worksheets = spreadsheet.worksheets()
        print("Доступные листы:")
        for sheet in worksheets:
            print(sheet.title)
        selected_sheet = spreadsheet.worksheet(sheet_name)
        data = selected_sheet.get_all_records()
        df = pd.DataFrame(data)
        print(df)
        MainStorage().set_dataframe(df)

    @classmethod
    def __init_table(cls, table_name, sheet_name):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            r"data/data.json", scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open(table_name)
        worksheets = spreadsheet.worksheets()
        print("Доступные листы:")
        for sheet in worksheets:
            print(sheet.title)
        selected_sheet = spreadsheet.worksheet(sheet_name)

        return selected_sheet

    @classmethod
    def _init_drive(cls):
        # Области доступа для Google Drive
        scope = ["https://www.googleapis.com/auth/drive"]

        # Загружаем учетные данные из файла
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "data/data.json", scope)
        drive_service = build('drive', 'v3', credentials=creds)
        return drive_service

    @classmethod
    def upload_file(cls, local_path, folder_id="1gqfaQVFJa4x4xJYuM0Dng-bfaMraIZ8c"):
        # Инициализация Google Drive API
        drive_service = cls._init_drive()

        # Метаданные файла, который будет загружен
        file_metadata = {'name': os.path.basename(local_path)}

        # Если указан идентификатор папки, добавляем его в метаданные
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # Создаем объект MediaFileUpload для загрузки файла
        media = MediaFileUpload(local_path, mimetype='image/jpeg')

        try:
            # Загружаем файл на Google Drive
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')
            print(f"Файл успешно загружен на Google Drive. ID: {file_id}")
            return file_id

        except Exception as error:
            print(f"Произошла ошибка при загрузке файла: {error}")
            return None

    @classmethod
    def cheker(cls, table_name=None, sheet_name=None, user_id=None):
        # Инициализация первой таблицы
        sheet = cls.__init_table("Lavka", "chose")
        existing_values = sheet.get_all_records()

        # Преобразование данных в DataFrame
        df = pd.DataFrame(existing_values)
        print("df", df)

        # Получение списка товаров по id пользователя (2 столбик - индекс 1)
        lst = list(df[df.iloc[:, 1] == int(user_id)].iloc[:, 0])

        # Инициализация второй таблицы
        sheet_2 = cls.__init_table(table_name, sheet_name)
        existing_values_2 = sheet_2.get_all_records()

        # Преобразование второй таблицы в DataFrame
        df_2 = pd.DataFrame(existing_values_2)

        # Получение артикула товара по имени (1 столбик - индекс 0, 2 столбик - индекс 1)
        article = list(df_2[df_2.iloc[:, 0] == lst[-1]].iloc[:, 1])

        # Возврат последнего артикула
        return int(article[-1])

    @classmethod
    def download(cls, table_name, sheet_name):
        scope = ["https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            r'data/data.json', scopes=scope)
        drive_service = build('drive', 'v3', credentials=creds)

        # Загрузка таблицы в DataFrame
        table = cls.__init_table(table_name, sheet_name)
        table_ozon = cls.__init_table("Lavka", "ozon_admin")

        existing_values = table.get_all_records()
        df = pd.DataFrame(existing_values)

        existing_values_ozon = table_ozon.get_all_records()
        df_ozon = pd.DataFrame(existing_values_ozon)



        # Сохранение данных в MainStorage()
        MainStorage().alL_table = df
        MainStorage().alL_table_ozon = df_ozon
        MainStorage().columns_onetothre = df.iloc[:, 0:3]
        MainStorage().columns_onetothre_ozon = df_ozon.iloc[:, 0:3]

        # Путь к основной папке
        main_folder_path = "imagesfor_view"
        main_folder_path_ozon = "imagesfor_view_ozon"

        # Очистка основной папки
        for item in os.listdir(main_folder_path):
            item_path = os.path.join(main_folder_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Удалена директория: {item_path}")

        for item in os.listdir(main_folder_path_ozon):
            item_path = os.path.join(main_folder_path_ozon, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Удалена директория: {item_path}")

        # Создание уникальных индексов для значений первого столбика
        unique_kats = MainStorage().columns_onetothre.iloc[:, 0].unique()
        kat_index_map = {kat: f"kat_{i}" for i, kat in enumerate(unique_kats)}

        # Создание уникальных индексов для значений первого столбика
        unique_kat_ozon = MainStorage().columns_onetothre_ozon.iloc[:, 0].unique()
        kat_index_m_ozon = {kat: f"kat_{i}" for i, kat in enumerate(unique_kat_ozon)}

        MainStorage().dict_kat = kat_index_map
        MainStorage().dict_kat_ozon = kat_index_m_ozon
        print(MainStorage().dict_kat)

        # Основной цикл для обработки изображений wb
        for i, val in enumerate(MainStorage().columns_onetothre.values.tolist()):
            kat, goods, url = val
            folder_name = kat_index_map[kat]  # Назначение уникального индекса для kat

            # Формирование пути папки с использованием уникального имени
            folder_path = os.path.join(main_folder_path, folder_name)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            # Фильтрация DataFrame для текущей категории kat
            filtered_df = MainStorage().columns_onetothre[
                (MainStorage().columns_onetothre.iloc[:, 0] == kat)
            ].reset_index(drop=True)


            # Поиск строки в отфильтрованном DataFrame, соответствующей goods и url
            matched_row = filtered_df[
                (filtered_df.iloc[:, 1] == goods) & (filtered_df.iloc[:, 2] == url)
            ]

            # Проверяем, нашли ли совпадение
            if not matched_row.iloc[:, 2].empty:
                filtered_index = matched_row.index[0]  # Получение индекса строки в отфильтрованном DataFrame

                try:
                    file_id = url.split('/d/')[1].split('/')[0]
                    request = drive_service.files().get_media(fileId=file_id)
                    file_path = f'image_{filtered_index}.jpg'
                    image_path = os.path.join(folder_path, file_path)

                    # Сохранение файла на диск
                    with open(image_path, 'wb') as f:
                        downloader = googleapiclient.http.MediaIoBaseDownload(f, request)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                            print(f"Загрузка: {int(status.progress() * 100)}% для индекса {filtered_index}")

                except Exception as e:
                    print(f"Ошибка загрузки для URL {url}: {e}")
                    continue

        # Основной цикл для обработки изображений ozon
        for i, val in enumerate(MainStorage().columns_onetothre_ozon.values.tolist()):
            kat, goods, url = val
            folder_name = kat_index_m_ozon[kat]  # Назначение уникального индекса для kat

            # Формирование пути папки с использованием уникального имени
            folder_path = os.path.join(main_folder_path_ozon, folder_name)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            # Фильтрация DataFrame для текущей категории kat
            filtered_df = MainStorage().columns_onetothre_ozon[
                (MainStorage().columns_onetothre_ozon.iloc[:, 0] == kat)
            ].reset_index(drop=True)


            # Поиск строки в отфильтрованном DataFrame, соответствующей goods и url
            matched_row = filtered_df[
                (filtered_df.iloc[:, 1] == goods) & (filtered_df.iloc[:, 2] == url)
            ]

            # Проверяем, нашли ли совпадение
            if not matched_row.iloc[:, 2].empty:
                filtered_index = matched_row.index[0]  # Получение индекса строки в отфильтрованном DataFrame

                try:
                    file_id = url.split('/d/')[1].split('/')[0]
                    request = drive_service.files().get_media(fileId=file_id)
                    file_path = f'image_{filtered_index}.jpg'
                    image_path = os.path.join(folder_path, file_path)

                    # Сохранение файла на диск
                    with open(image_path, 'wb') as f:
                        downloader = googleapiclient.http.MediaIoBaseDownload(f, request)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                            print(f"Загрузка: {int(status.progress() * 100)}% для индекса {filtered_index}")

                except Exception as e:
                    print(f"Ошибка загрузки для URL {url}: {e}")
                    continue


        print("Изображения успешно загружены!")

    @classmethod
    def download_examples(cls, table_name, sheet_name, url, index):
        scope = ["https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            r'data/data.json', scopes=scope)
        drive_service = build('drive', 'v3', credentials=creds)
        folder_path = 'temp_images'
        try:
            file_id = url.split('/d/')[1].split('/')[0]
            request = drive_service.files().get_media(fileId=file_id)
            file_path = f'image_example_{index}.jpg'
            image_path = os.path.join(folder_path, file_path)

            # Сохранение файла на диск
            with open(image_path, 'wb') as f:
                downloader = googleapiclient.http.MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Загрузка: {int(status.progress() * 100)}% для индекса {index}")

        except Exception as e:
            print(f"Ошибка загрузки для URL {url}: {e}")

    @classmethod
    def add_number(cls, search_value, new_value, column : int, table_name = "Lavka", sheet_name = "user_data"):
        sheet = cls.__init_table(table_name, sheet_name)
        column_data = sheet.col_values(1)[1:]

        try:
            # Находим индекс строки, где значение в первом столбце совпадает с search_value
            row_index = column_data.index(search_value) + 2  # gspread использует индексацию с 1
            # Обновляем значение в третьем столбце для найденной строки
            sheet.update_cell(row_index, column, new_value)
            print(f"Значение в строке {row_index} обновлено на '{new_value}' в третьем столбце")
        except ValueError:
            print(f"Значение '{search_value}' не найдено в первом столбце")

    @classmethod
    def update_row(cls, search_value, new_row_values, table_name="Lavka", sheet_name="user_data"):
        # Инициализация таблицы и листа
        sheet = cls.__init_table(table_name, sheet_name)
        column_data = sheet.col_values(1)[1:]  # Получаем значения первого столбца, пропуская заголовок

        try:
            # Находим индекс строки, где значение в первом столбце совпадает с search_value
            row_index = column_data.index(search_value) + 2  # gspread использует индексацию с 1
            # Обновляем всю строку по найденному индексу
            sheet.update(f"A{row_index}", [new_row_values])
            print(f"Строка {row_index} обновлена на значения {new_row_values}")
        except ValueError:
            print(f"Значение '{search_value}' не найдено в первом столбце")

    @classmethod
    def get_data_user(cls, id, table_name = "Lavka", sheet_name = "user_data"):
        sheet = cls.__init_table(table_name, sheet_name)
        column_data = sheet.col_values(1)[1:]

        try:
            # Находим индекс строки, где значение в первом столбце совпадает с search_value
            row_index = column_data.index(id) + 2  # gspread использует индексацию с 1
            # Обновляем значение в третьем столбце для найденной строки
            row_values = sheet.row_values(row_index)
            return row_values
        except ValueError:
            print(f"Значение  не найдено в первом столбце")

    @classmethod
    def add_data_personal(cls, id, table_name = "Lavka", sheet_name = "user_data"):
        sheet = cls.__init_table(table_name, sheet_name)

        # Получаем все значения из листа gspread
        values = sheet.get_all_values()

        # Находим первую пустую строку, начиная с 2-й (пропуская заголовки)
        row_to_insert = len(values) + 1  # Изначально предполагаем, что добавим в конец

        # Проверяем строки начиная со 2-й, чтобы найти первую пустую строку
        for i in range(1, len(values)):
            if not any(values[i]):  # Если вся строка пустая
                row_to_insert = i + 1  # Устанавливаем строку для вставки
                break

        # Записываем данные в ячейки
        sheet.update(f'A{row_to_insert}',[ [str(id)]])  # Заполняем данные

    @classmethod
    def update_table(cls, row_index, column_name, table_name = 'Lavka', sheet_name = 'wb_admin'):
            sheet = cls.__init_table(table_name, sheet_name)
            df = MainStorage().alL_table
            # 2. Проверяем, существует ли нужная ячейка и является ли её значение числом
            if column_name in df.columns and 0 <= row_index < len(df):

                # Приводим значение к целому числу и проверяем тип
                try:
                    # Приводим значение к int
                    current_value = int(float(df.at[row_index, column_name]))
                    print(f"Текущее значение: {current_value}")  # Выводим текущее значение

                    # Уменьшаем значение на 1
                    df.at[row_index, column_name] = int(current_value - 1)  # Приводим новое значение к int
                    print(f"Новое значение после уменьшения: {df.at[row_index, column_name]}")  # Выводим новое значение

                except (ValueError, TypeError):
                    print("Значение в ячейке не является числом или не может быть приведено к целому числу")
                    return
            else:
                print("Некорректный индекс строки или имя столбца")
                return

            sheet.clear()

            # 5. Выгружаем обновленные данные в Google Таблицу
            sheet.update([df.columns.values.tolist()] + df.values.tolist())
            print("Данные успешно обновлены в Google Таблице.")

            table = cls.__init_table(table_name, sheet_name)
            existing_values = table.get_all_records()
            df = pd.DataFrame(existing_values)

            # Сохранение данных в MainStorage()
            MainStorage().alL_table = df
            print("Новые данные занесены в таблицу бота")

