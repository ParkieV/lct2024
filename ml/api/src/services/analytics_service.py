import os
from io import BytesIO
import base64

import pandas as pd
import matplotlib.pyplot as plt


SCRIPT_LOC = os.path.dirname(os.path.realpath(__file__))

def get_history():
    path_contracts = f'{SCRIPT_LOC}/data/Выгрузка контрактов по Заказчику.xlsx'

    contracts = pd.read_excel(path_contracts)

    contracts = contracts[contracts['Статус контракта'] != 'Расторгнут']
    contracts['Срок исполнения с'] = pd.to_datetime(contracts['Срок исполнения с'], format='%d.%m.%Y')
    contracts['Срок исполнения по'] = pd.to_datetime(contracts['Срок исполнения по'], format='%d.%m.%Y')

    contracts = contracts.sort_values(by='Срок исполнения с', ascending=False)

    return contracts

def get_purchases(df, period, summa):

    df['year'] = df['Срок исполнения с'].dt.year
    df['quarter'] = df['Срок исполнения с'].dt.quarter
    df['month'] = df['Срок исполнения с'].dt.month
    df['day'] = df['Срок исполнения с'].dt.day_of_year
    df['day_of_month'] = df['Срок исполнения с'].dt.day
    df['Длительность'] = (df['Срок исполнения по'] - df['Срок исполнения с']).dt.days

    if summa:
        column_to_out = 'Цена ГК, руб.'
        if period == 1:
            df = df.groupby('year')[column_to_out].sum()
        elif period == 2:
            df = df.groupby('quarter')[column_to_out].sum()
        elif period == 3:
            df = df.groupby('month')[column_to_out].sum()

        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df.values, color='#B12725')
        plt.title(f'Статистика по всем закупкам')
        if period == 1:
            plt.xlabel('Год')
            plt.xticks(df.index)
        elif period == 2:
            plt.xlabel('Квартал')
            plt.xticks(df.index)
        elif period == 3:
            plt.xlabel('Месяц')
            plt.xticks(df.index)
        plt.ylabel('Цена')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        plot_image = base64.b64encode(buf.read()).decode('utf-8')

        if df.empty:
            return {
                'state': 'Wrong plot',
                'dataframe': None,
                'plot_image': plot_image
            }

        return {
            'state': 'Success',
            'dataframe': df.to_dict(),
            'plot_image': plot_image
        }
    
    else:
        column_to_out = 'Цена ГК, руб.'

        if period == 1:
            df = df.groupby('year')[column_to_out].count()
        elif period == 2:
            df = df.groupby('quarter')[column_to_out].count()
        elif period == 3:
            df = df.groupby('month')[column_to_out].count()
        
        plt.figure(figsize=(10, 5))
        plt.bar(df.index, df.values, color='#B12725')
        plt.title(f'Статистика по всем закупкам')
        if period == 1:
            plt.xlabel('Год')
            plt.xticks(df.index)
        elif period == 2:
            plt.xlabel('Квартал')
            plt.xticks(df.index)
        elif period == 3:
            plt.xlabel('Месяц')
            plt.xticks(df.index)
        plt.ylabel('Количество')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        plot_image = base64.b64encode(buf.read()).decode('utf-8')

        if df.empty:    
            return {
                'state': 'Wrong plot',
                'dataframe': None,
                'plot_image': plot_image
            }

        return {
            'state': 'Success',
            'dataframe': df.to_dict(),
            'plot_image': plot_image
        }
