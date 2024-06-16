import os
import asyncio
from io import BytesIO
from pathlib import PurePath
import re

import pandas as pd
import numpy as np
from fastapi import HTTPException, status
from functools import reduce


engines = {
        '.xlsx': 'openpyxl',
        '.xls': 'xlrd'
    }

async def bytes_to_pandas(data: bytes, file_extension: str):
    io = BytesIO(data)

    if file_extension == '.csv':
        return pd.read_csv(io)

    if file_extension not in engines:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f'Файлы с расширением {file_extension} не поддерживаются')

    return pd.read_excel(io, engine=engines[file_extension]) # type: ignore


def _parser_kvartal_year(string: str):
    kvartal = int(re.search(r"\d* квартал", string).group().split(" ")[0]) # type: ignore
    year = int(re.search(r"\d* г.", string).group().split(" ")[0]) # type: ignore

    return kvartal, year

def _create_column_names(df: pd.DataFrame, date_encode) -> None:
    new_column_names: list[int | str] = ['Code1', 'Code2', 'Code3', 'Name']
    # создание столбцов
    offset = 4
    df_column_parts = [date_encode, "остаток нач", "дебет", "сумма"]
    for i in range(12):
        if i % 2 == 0:
            df_column_parts[3] = "сумма"
        elif i % 2 == 1:
            df_column_parts[3] = "кол-во"
        if (i % 4) // 2 == 0:
            df_column_parts[2] = "дебет"
        elif (i % 4) // 2 == 1:
            df_column_parts[2] = "кредит"
        if (i // 4) == 0:
            df_column_parts[1] = "остаток нач"
        elif (i // 4) == 1:
            df_column_parts[1] = "оборот"
        elif (i // 4) == 2:
            df_column_parts[1] = "остаток кон"

        new_column_names.append('|'.join(df_column_parts))
    df.columns = new_column_names


def _is_number(s):
    """ Returns True if string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False


async def _create_kvartal_dataframe(data: bytes, file_extension: str) -> pd.DataFrame:
    data_df = await bytes_to_pandas(data, file_extension)
    goods_row: list = [-1, -1, -1, ""]

    # Установка даты для столбцов
    print(data_df.iat[0,0])
    date_data = _parser_kvartal_year(data_df.iat[0,0])
    date_encode = f"{date_data[0]}Q{date_data[1]}"

    rows = []
    fake_strings = ["Кузнецов М. С. -",
                       "Итого",
                       "Исполнитель",
                       "Главный бухгалтер",
                       "(уполномоченное лицо)",
                       "Руководитель"]

    # Загрузка значений
    first_column = data_df.iloc[:, 0]
    for i in range(len(first_column)):
        if _is_number(first_column[i]) and pd.notna(first_column[i]):
            number = float(first_column[i])
            # Установка кодов
            if int(number) == float(number):
                goods_row[0]=float(number)
            elif int(number*10) == float(number*10):
                goods_row[1]=float(number)
            elif int(number*100) == float(number*100):
                goods_row[2]=float(number)
        elif isinstance(first_column[i], str) and i > 14:
            #установка значений
            if first_column[i] not in fake_strings and pd.notna(first_column[i]):
                goods_row[3] = first_column[i]

                # \dQ\d{4}|остаток нач|дебет|сумма
                goods_row.append(np.nan if pd.isna(data_df.iat[i, 10]) else float(data_df.iat[i, 10]))
                # \dQ\d{4}|остаток нач|дебет|кол-во
                goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 10]) else float(data_df.iat[i+1, 10]))
                # \dQ\d{4}|остаток нач|кредит|сумма
                goods_row.append(np.nan if pd.isna(data_df.iat[i, 11]) else float(data_df.iat[i, 11]))
                # \dQ\d{4}|остаток нач|кредит|кол-во
                goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 11]) else float(data_df.iat[i+1, 11]))
                if len(data_df.columns) == 16:
                    # \dQ\d{4}|оборот|дебет|сумма
                    goods_row.append(np.nan if pd.isna(data_df.iat[i, 12]) else float(data_df.iat[i, 12]))
                    # \dQ\d{4}|оборот|дебет|кол-во
                    goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 12]) else float(data_df.iat[i+1, 12]))
                    # \dQ\d{4}|оборот|кредит|сумма
                    goods_row.append(np.nan if pd.isna(data_df.iat[i, 13]) else float(data_df.iat[i, 13]))
                    # \dQ\d{4}|оборот|кредит|кол-во
                    goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 13]) else float(data_df.iat[i+1, 13]))
                    # \dQ\d{4}|остаток кон|дебет|сумма
                    goods_row.append(np.nan if pd.isna(data_df.iat[i, 14]) else float(data_df.iat[i, 14]))
                    # \dQ\d{4}|остаток кон|дебет|кол-во
                    goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 14]) else float(data_df.iat[i+1, 14]))
                    # \dQ\d{4}|остаток кон|кредит|сумма
                    goods_row.append(np.nan if pd.isna(data_df.iat[i, 15]) else float(data_df.iat[i, 15]))
                    # \dQ\d{4}|остаток кон|кредит|кол-во
                    goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 15]) else float(data_df.iat[i+1, 15]))
                else:
                    # \dQ\d{4}|остаток кон|дебет|сумма
                    goods_row.append(np.nan if pd.isna(data_df.iat[i, 14]) else float(data_df.iat[i, 14]))
                    # \dQ\d{4}|остаток кон|дебет|кол-во
                    goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 14]) else float(data_df.iat[i+1, 14]))
                    # \dQ\d{4}|остаток кон|кредит|сумма
                    goods_row.append(np.nan if pd.isna(data_df.iat[i, 15]) else float(data_df.iat[i, 15]))
                    # \dQ\d{4}|остаток кон|кредит|кол-во
                    goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 15]) else float(data_df.iat[i+1, 15]))
                    # \dQ\d{4}|остаток кон|дебет|сумма
                    goods_row.append(np.nan if pd.isna(data_df.iat[i, 16]) else float(data_df.iat[i, 16]))
                    # \dQ\d{4}|остаток кон|дебет|кол-во
                    goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 16]) else float(data_df.iat[i+1, 16]))
                    # \dQ\d{4}|остаток кон|кредит|сумма
                    goods_row.append(np.nan if pd.isna(data_df.iat[i, 17]) else float(data_df.iat[i, 17]))
                    # \dQ\d{4}|остаток кон|кредит|кол-во
                    goods_row.append(np.nan if pd.isna(data_df.iat[i+1, 17]) else float(data_df.iat[i+1, 17]))

                rows.append(tuple(goods_row))
                goods_row = goods_row[:3] +[""]


    df = pd.DataFrame(rows, columns=range(16))
    _create_column_names(df, date_encode)

    df = df.groupby(['Code1', 'Code2', 'Code3', 'Name']).sum()
    return df.sort_values(['Code3', "Name"])


async def import_saldo(dir_path: str):
    filenames = next(os.walk(dir_path), (None, None, []))[2]
    dfs = []

    i=1
    for filename in filenames:
        print(f"{dir_path}/{filename}")

        if PurePath(filename).suffix in engines.keys():
            with open(f"{dir_path}/{filename}", "rb") as file:
                df = await _create_kvartal_dataframe(file.read(), PurePath(filename).suffix)
                df = df.reset_index()

                # tcols = list(df.columns)
                # print(tcols[:5])
                # wdf = df[tcols[1:4] + tcols[:1] + tcols[4:]]
                df.to_excel(f"{dir_path}/dfs/df{i}.xlsx",index=False)

                i += 1
                dfs.append(df)

    dfs1, dfs2 = dfs[:4], dfs[4:]

    results = [reduce(lambda left, right: pd.merge(left, right, on=['Code1', 'Code2', 'Code3', 'Name'], how='outer'), dfs1),
              reduce(lambda left, right: pd.merge(left, right, on=['Code1', 'Code2', 'Code3', 'Name'], how='outer'), dfs2)]

    # cols = list(ans_df.columns)
    # ans_df = ans_df[cols[1:4] + cols[:1] + cols[4:]]
    return map(lambda x: x.sort_values(['Code3', "Name"]), results)


if __name__=="__main__":
    dir_path = os.path.abspath("data/saldo")
    result = asyncio.run(import_saldo(dir_path))
    for i, df in enumerate(result):
        if not df.empty:
            df.to_excel(f"{dir_path}/dfs/final{i + 1}.xlsx", index=False)
            print("Success!")
        else:
            print("Mdya")


    # df = pd.read_csv(f"{dir_path}/dfs/final.csv")
    # print(df)
