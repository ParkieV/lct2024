import re
import os
import base64
from io import BytesIO

import numpy as np
import pandas as pd
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import Ridge
from thefuzz import process
import matplotlib.pyplot as plt
from typing import Tuple
from statsmodels.tsa.arima.model import ARIMA

from api.src.services.text_service import Dataset
from api.src.configurations.models import model as MODEL, tokenizer as TOKENIZER


SCRIPT_LOC = os.path.dirname(os.path.realpath(__file__))

def get_embeddings(texts):
    inputs = TOKENIZER(texts, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = MODEL(**inputs)

    embeddings = outputs.last_hidden_state[:, 0, :]
    embeddings = torch.nn.functional.normalize(embeddings)
    return embeddings


def find_similar_leftover(user_pick: str) -> Tuple[int, str, str]:
    df_reference = pd.read_excel(f'{SCRIPT_LOC}/data/processed_names.xlsx')
    df_leftovers = pd.read_excel(f'{SCRIPT_LOC}/data/concat_leftovers.xlsx')

    kpgz = df_reference[df_reference['Название СТЕ'] == user_pick]['КПГЗ'].values[0]
    goods = df_leftovers['Name processed'].tolist()

    results = process.extract(kpgz, goods, limit=10)
    most_similars = [result[0] for result in results]

    filtered_df = df_leftovers[df_leftovers['Name processed'].isin(most_similars)]
    embeddings_list = filtered_df['embeddings'].apply(lambda x : [float(x) for x in x.replace("[", "").replace ("]", "").split(',')])
    product_embeddings = list(embeddings_list)
    help_embedding = get_embeddings([user_pick])

    similarities = cosine_similarity(help_embedding, product_embeddings).flatten()
    filtered_df['similarity'] = similarities
    filtered_df = filtered_df.sort_values(by='similarity', ascending=False)

    if filtered_df.iloc[0]['similarity'] > 0.77:

        most_similar = filtered_df.head(1)['Name processed'].iloc[0]

        leftover_name = df_leftovers[df_leftovers['Name processed'] == most_similar]['Name'].values[0]
        code = int(df_leftovers[df_leftovers['Name processed'] == most_similar]['Code1'].iloc[0])
        return code, kpgz, leftover_name
    
    else:
        return (404, kpgz, "No similar leftovers found")



class PurchaseHistory:

    def __init__(self, name: str, voc: pd.DataFrame, contracts: pd.DataFrame) -> None:

        self.voc_rows = pd.DataFrame(voc.loc[voc['Название СТЕ'] == name])
        self.contracts = contracts

    def get_purchases(self, include_rk: bool=True, include_kpgz: bool=True) -> pd.DataFrame:

        self.kpgz_contracts = self.contracts.copy()

        if include_kpgz:
            kpgz = self.voc_rows['КПГЗ код'].values[0]
            self.kpgz_contracts = self.contracts.loc[self.contracts['Конечный код КПГЗ'].str.contains(kpgz).fillna(False)]

        if include_rk:
            rks = self.voc_rows['Реестровый номер в РК'].values
            self.kpgz_contracts = self.kpgz_contracts.loc[self.kpgz_contracts['Реестровый номер в РК'].isin(rks)]

        return self.kpgz_contracts

    def drop_cancelled(self):

        self.kpgz_contracts = self.kpgz_contracts[self.kpgz_contracts['Статус контракта'] != 'Расторгнут']

    def generate_features(self):

        contracts_cleaned = self.kpgz_contracts.copy()
        contracts_cleaned = contracts_cleaned[contracts_cleaned['Статус контракта'] != 'Расторгнут']
        contracts_cleaned['Срок исполнения с'] = pd.to_datetime(contracts_cleaned['Срок исполнения с'], format='%d.%m.%Y')
        contracts_cleaned['Срок исполнения по'] = pd.to_datetime(contracts_cleaned['Срок исполнения по'], format='%d.%m.%Y')
        contracts_cleaned['year'] = contracts_cleaned['Срок исполнения с'].dt.year
        contracts_cleaned['quarter'] = contracts_cleaned['Срок исполнения с'].dt.quarter
        contracts_cleaned['month'] = contracts_cleaned['Срок исполнения с'].dt.month
        contracts_cleaned['day'] = contracts_cleaned['Срок исполнения с'].dt.day_of_year
        contracts_cleaned['Длительность'] = (contracts_cleaned['Срок исполнения по'] - contracts_cleaned['Срок исполнения с']).dt.days

        self.kpgz_contracts = contracts_cleaned.copy()

        return self.kpgz_contracts

    def check_regular_purchase(self):

        num_rk = len(self.kpgz_contracts['Реестровый номер в РК'].unique())

        if num_rk >= 2:
            return True # Регулярная

        else:
            return False # Нерегулярная

    def normalize_spgz(self):

        contracts_dataset = Dataset(self.kpgz_contracts.copy(), text_col='Наименование СПГЗ')
        contracts_dataset.prepare_dataset()
        self.normalized_spgz_contracts = contracts_dataset.data.copy()

        return self.normalized_spgz_contracts

    def normalize_ste(self):

        voc_dataset = Dataset(self.voc_rows.copy(), text_col='Название СТЕ')
        voc_dataset.prepare_dataset(voc_dataset)
        self.normalized_ste_voc = voc_dataset.data.copy()

        return self.normalized_ste_voc

    def rank_ste_spgz(self):

        contract_embeds = []
        for sent in self.normalized_spgz_contracts['Наименование СПГЗ']:
            embed = get_embeddings([sent.lower()])
            contract_embeds.append(embed)

        contract_embeds_df = pd.DataFrame(contract_embeds, index=self.normalized_spgz_contracts.index)
        contracts_merged = pd.merge(self.normalized_spgz_contracts, contract_embeds_df, left_index=True, right_index=True)

        query_embed = get_embeddings([self.normalized_ste_voc['Название СТЕ'].values[0]])

        cosine_similarities = []
        for row in range(len(contracts_merged)):
            sent = contract_embeds_df.iloc[row].values
            cos = cosine_similarity(sent.reshape(1, -1), query_embed.reshape(1, -1))[0][0]
            cosine_similarities.append(cos)

        result = pd.DataFrame({'sent': self.normalized_spgz_contracts['Наименование СПГЗ'].values,
                               'cos': np.array(cosine_similarities)})

        return result.sort_values(by=['cos'], ascending=False)

    def fit_lr(self, target):

        model = Ridge(alpha=0.05)
        model.fit()


class PurchaseHistory:

    def __init__(self, name: str, voc: pd.DataFrame, contracts: pd.DataFrame) -> None:

        self.voc_rows = pd.DataFrame(voc.loc[voc['Название СТЕ'] == name])
        self.contracts = contracts

    def get_purchases(self, include_rk: bool=True, include_kpgz: bool=True) -> pd.DataFrame:

        self.kpgz_contracts = self.contracts.copy()

        if include_kpgz:
            kpgz = self.voc_rows['КПГЗ код'].values[0]
            self.kpgz_contracts = self.contracts.loc[self.contracts['Конечный код КПГЗ'].str.contains(kpgz).fillna(False)]

        if include_rk:
            rks = self.voc_rows['Реестровый номер в РК'].values
            self.kpgz_contracts = self.kpgz_contracts.loc[self.kpgz_contracts['Реестровый номер в РК'].isin(rks)]

        return self.kpgz_contracts

    def drop_cancelled(self):

        self.kpgz_contracts = self.kpgz_contracts[self.kpgz_contracts['Статус контракта'] != 'Расторгнут']

    def generate_features(self):

        contracts_cleaned = self.kpgz_contracts.copy()
        contracts_cleaned = contracts_cleaned[contracts_cleaned['Статус контракта'] != 'Расторгнут']
        contracts_cleaned['Срок исполнения с'] = pd.to_datetime(contracts_cleaned['Срок исполнения с'], format='%d.%m.%Y')
        contracts_cleaned['Срок исполнения по'] = pd.to_datetime(contracts_cleaned['Срок исполнения по'], format='%d.%m.%Y')
        contracts_cleaned['year'] = contracts_cleaned['Срок исполнения с'].dt.year
        contracts_cleaned['quarter'] = contracts_cleaned['Срок исполнения с'].dt.quarter
        contracts_cleaned['month'] = contracts_cleaned['Срок исполнения с'].dt.month
        contracts_cleaned['day'] = contracts_cleaned['Срок исполнения с'].dt.day_of_year
        contracts_cleaned['day_of_month'] = contracts_cleaned['Срок исполнения с'].dt.day
        contracts_cleaned['Длительность'] = (contracts_cleaned['Срок исполнения по'] - contracts_cleaned['Срок исполнения с']).dt.days

        self.kpgz_contracts = contracts_cleaned.copy()

        return self.kpgz_contracts

    def check_regular_purchase(self):

        num_rk = len((self.kpgz_contracts['year'].astype('str') + self.kpgz_contracts['quarter'].astype('str')).unique())

        if num_rk >= 3:
            return True # Регулярная

        else:
            return False # Нерегулярная

    def normalize_spgz(self):

        contracts_dataset = Dataset(self.kpgz_contracts.copy(), text_col='Наименование СПГЗ')
        contracts_dataset.prepare_dataset()
        self.normalized_spgz_contracts = contracts_dataset.data.copy()

        return self.normalized_spgz_contracts

    def normalize_ste(self):

        voc_dataset = Dataset(self.voc_rows.copy(), text_col='Название СТЕ')
        voc_dataset.prepare_dataset(voc_dataset)
        self.normalized_ste_voc = voc_dataset.data.copy()

        return self.normalized_ste_voc

    def rank_ste_spgz(self):

        contract_embeds = []
        for sent in self.normalized_spgz_contracts['Наименование СПГЗ']:
            embed = get_embeddings([sent.lower()])
            contract_embeds.append(embed)

        contract_embeds_df = pd.DataFrame(contract_embeds, index=self.normalized_spgz_contracts.index)
        contracts_merged = pd.merge(self.normalized_spgz_contracts, contract_embeds_df, left_index=True, right_index=True)

        query_embed = get_embeddings([self.normalized_ste_voc['Название СТЕ'].values[0]])

        cosine_similarities = []
        for row in range(len(contracts_merged)):
            sent = contract_embeds_df.iloc[row].values
            cos = cosine_similarity(sent.reshape(1, -1), query_embed.reshape(1, -1))[0][0]
            cosine_similarities.append(cos)

        result = pd.DataFrame({'sent': self.normalized_spgz_contracts['Наименование СПГЗ'].values,
                               'cos': np.array(cosine_similarities)})

        return result.sort_values(by=['cos'], ascending=False)

#
#
# Класс для работы с выбранным товаром
#
#
class UserPickMLService:
    def __init__(self, user_pick):
        self.user_pick = user_pick
        self.code, self.kpgz, self.leftover_name = find_similar_leftover(user_pick)

    def get_leftover_info(self):
        path_to_data = f'{SCRIPT_LOC}/data'

        if self.code == 404:
            return {'1Q2022|остаток кон|балансовая стоимость': 0, '1Q2022|остаток кон|количество': 0, '1Q2022|остаток кон|остаточная стоимость':0,
            '2Q2022|остаток кон|балансовая стоимость':0, '2Q2022|остаток кон|количество':0, '2Q2022|остаток кон|остаточная стоимость':0,
            '3Q2022|остаток кон|балансовая стоимость':0, '3Q2022|остаток кон|количество':0, '3Q2022|остаток кон|остаточная стоимость':0,
            '4Q2022|остаток кон|балансовая стоимость':0, '4Q2022|остаток кон|количество':0, '4Q2022|остаток кон|остаточная стоимость':0}

        df =  pd.read_excel(f'{path_to_data}/Остатки {self.code}.xlsx')

        columns_to_out = [
            '1Q2022|остаток кон|балансовая стоимость', '1Q2022|остаток кон|количество', '1Q2022|остаток кон|остаточная стоимость',
            '2Q2022|остаток кон|балансовая стоимость', '2Q2022|остаток кон|количество', '2Q2022|остаток кон|остаточная стоимость',
            '3Q2022|остаток кон|балансовая стоимость', '3Q2022|остаток кон|количество', '3Q2022|остаток кон|остаточная стоимость',
            '4Q2022|остаток кон|балансовая стоимость', '4Q2022|остаток кон|количество', '4Q2022|остаток кон|остаточная стоимость']

        df = df[df['Name'] == self.leftover_name][columns_to_out].sum()

        leftover_info = df.to_dict()

        return leftover_info

    def get_leftover_info_plot(self):

        path_to_data = f'{SCRIPT_LOC}/data'

        if self.code == 404:
            df = pd.DataFrame({'1Q2022|остаток кон|балансовая стоимость': [0], '1Q2022|остаток кон|количество': [0], '1Q2022|остаток кон|остаточная стоимость':[0],
            '2Q2022|остаток кон|балансовая стоимость':[0], '2Q2022|остаток кон|количество':[0], '2Q2022|остаток кон|остаточная стоимость':[0],
            '3Q2022|остаток кон|балансовая стоимость':[0], '3Q2022|остаток кон|количество':[0], '3Q2022|остаток кон|остаточная стоимость':[0],
            '4Q2022|остаток кон|балансовая стоимость':[0], '4Q2022|остаток кон|количество':[0], '4Q2022|остаток кон|остаточная стоимость':[0]})
        else:

            df =  pd.read_excel(f'{path_to_data}/Остатки {self.code}.xlsx')
            print(self.code)
            
            columns_to_out = [
                '1Q2022|остаток кон|балансовая стоимость', '1Q2022|остаток кон|количество', '1Q2022|остаток кон|остаточная стоимость',
                '2Q2022|остаток кон|балансовая стоимость', '2Q2022|остаток кон|количество', '2Q2022|остаток кон|остаточная стоимость',
                '3Q2022|остаток кон|балансовая стоимость', '3Q2022|остаток кон|количество', '3Q2022|остаток кон|остаточная стоимость',
                '4Q2022|остаток кон|балансовая стоимость', '4Q2022|остаток кон|количество', '4Q2022|остаток кон|остаточная стоимость'
            ]

            df = df[df['Name'] == self.leftover_name][columns_to_out].sum()

        columns_to_out = ['1Q2022|остаток кон|количество', '2Q2022|остаток кон|количество',
              '3Q2022|остаток кон|количество', '4Q2022|остаток кон|количество']
        column_names = ['1Q2022', '2Q2022', '3Q2022', '4Q2022']

        plt.figure(figsize=(10, 5))
        bars = plt.bar(column_names, df[columns_to_out].values[0], color='#B12725') 
        plt.title(f'Остатки на складе\n{self.user_pick}')
        plt.xlabel('Квартал')
        plt.ylabel('Количество')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

        plt.show()

        # Save the plot to a BytesIO buffer
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Encode the image in Base64
        plot_image = base64.b64encode(buf.read()).decode('utf-8')

        # Convert the dataframe to JSON
        dataframe_json = df[['4Q2022|остаток кон|балансовая стоимость', '4Q2022|остаток кон|количество', '4Q2022|остаток кон|остаточная стоимость']].to_dict()

        if self.code == 404:
            return {
                'state': 'Wrong plot',
                'dataframe': None,
                'plot_image': plot_image
            }
        
        return {
            'state': 'Success',
            'dataframe': dataframe_json,
            'plot_image': plot_image
        }
    
    def check_regular(self) -> bool:
        path_contracts = f'{SCRIPT_LOC}/data/Выгрузка контрактов по Заказчику.xlsx'
        path_voc = f'{SCRIPT_LOC}/data/КПГЗ ,СПГЗ, СТЕ.xlsx'

        contracts = pd.read_excel(path_contracts)
        voc = pd.read_excel(path_voc)

        ph = PurchaseHistory(self.user_pick, voc, contracts)

        ph.get_purchases(include_rk=True, include_kpgz=True)
        ph.drop_cancelled()

        return ph.check_regular_purchase()
    
    def get_history(self, n: int):
        path_contracts = f'{SCRIPT_LOC}/data/Выгрузка контрактов по Заказчику.xlsx'
        path_voc = f'{SCRIPT_LOC}/data/КПГЗ ,СПГЗ, СТЕ.xlsx'

        contracts = pd.read_excel(path_contracts)
        voc = pd.read_excel(path_voc)

        ph = PurchaseHistory(self.user_pick, voc, contracts)

        ph.get_purchases(include_rk=True, include_kpgz=True)
        ph.drop_cancelled()

        output_df = ph.generate_features().sort_values(by='Срок исполнения с', ascending=False).head(n)
        return output_df

    def get_credit_debit(self, summa: bool):

        if self.code == 404:
            df = pd.DataFrame({'1Q2022|остаток кон|кредит|сумма': [0], '2Q2022|остаток кон|кредит|сумма': [0],
                               '3Q2022|остаток кон|кредит|сумма': [0], '4Q2022|остаток кон|кредит|сумма': [0],
                               '1Q2022|остаток кон|дебет|сумма': [0], '2Q2022|остаток кон|дебет|сумма': [0],
                               '3Q2022|остаток кон|дебет|сумма': [0], '4Q2022|остаток кон|дебет|сумма': [0],
                               '1Q2022|остаток кон|кредит|кол-во': [0], '2Q2022|остаток кон|кредит|кол-во': [0],
                               '3Q2022|остаток кон|кредит|кол-во': [0], '4Q2022|остаток кон|кредит|кол-во': [0],
                               '1Q2022|остаток кон|дебет|кол-во': [0], '2Q2022|остаток кон|дебет|кол-во': [0],
                               '3Q2022|остаток кон|дебет|кол-во': [0], '4Q2022|остаток кон|дебет|кол-во': [0]})
        else:
            df = pd.read_excel(f'{SCRIPT_LOC}/data/all_debit_credit.xlsx')
            df = df[df['Name'] == self.leftover_name].sum()

        if summa:


            credit_columns_to_out = ['1Q2022|остаток кон|кредит|сумма', '2Q2022|остаток кон|кредит|сумма', 
                                    '3Q2022|остаток кон|кредит|сумма', '4Q2022|остаток кон|кредит|сумма']
                    
            debit_columns_to_out = ['1Q2022|остаток кон|дебет|сумма', '2Q2022|остаток кон|дебет|сумма',
                                '3Q2022|остаток кон|дебет|сумма', '4Q2022|остаток кон|дебет|сумма']
            
            credit_df = df[credit_columns_to_out]
            debit_df = df[debit_columns_to_out]

            # Flatten the values if they are not 1-dimensional
            credit_values = credit_df.values.flatten()
            debit_values = debit_df.values.flatten()


            plt.figure(figsize=(10, 5))
            plt.bar(['1Q2022', '2Q2022', '3Q2022', '4Q2022'], credit_values, color='#B12725', label='Кредит')
            plt.bar(['1Q2022', '2Q2022', '3Q2022', '4Q2022'], debit_values, color='#2B7A78', label='Дебет')
            plt.title(f'Оборотно-сальдовая ведомость\n Сумма {self.leftover_name}')
            plt.xlabel('Квартал')
            plt.ylabel('Сумма')
            plt.legend()

            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            plot_image = base64.b64encode(buf.read()).decode('utf-8')

            if self.code == 404:
                return {
                    'state': 'Wrong plot',
                    'credit': None,
                    'debit': None,
                    'plot_image': plot_image
                }
            return {
                'state': 'Success',
                'credit': credit_df.to_dict(),
                'debit': debit_df.to_dict(),
                'plot_image': plot_image
            }
        
        else:

            credit_columns_to_out = ['1Q2022|остаток кон|кредит|кол-во', '2Q2022|остаток кон|кредит|кол-во', 
                                     '3Q2022|остаток кон|кредит|кол-во', '4Q2022|остаток кон|кредит|кол-во']
            
            debit_columns_to_out = ['1Q2022|остаток кон|дебет|кол-во', '2Q2022|остаток кон|дебет|кол-во',
                                    '3Q2022|остаток кон|дебет|кол-во', '4Q2022|остаток кон|дебет|кол-во']
            
            credit_df = df[credit_columns_to_out]
            debit_df = df[debit_columns_to_out]

            # Flatten the values if they are not 1-dimensional
            credit_values = credit_df.values.flatten()
            debit_values = debit_df.values.flatten()

            plt.figure(figsize=(10, 5))
            plt.bar(['1Q2022', '2Q2022', '3Q2022', '4Q2022'], credit_values, color='#B12725', label='Кредит')
            plt.bar(['1Q2022', '2Q2022', '3Q2022', '4Q2022'], debit_values, color='#2B7A78', label='Дебет')
            plt.title(f'Оборотно-сальдовая ведомость\n Количество {self.leftover_name}')
            plt.xlabel('Квартал')
            plt.ylabel('Количество')
            plt.legend()
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            plt.show()

            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            plot_image = base64.b64encode(buf.read()).decode('utf-8')

            if self.code == 404:
                return {
                    'state': 'Wrong plot',
                    'credit': None,
                    'debit': None,
                    'plot_image': plot_image
                }
            return {
                'state': 'Success',
                'credit': credit_df.to_dict(),
                'debit': debit_df.to_dict(),
                'plot_image': plot_image
            }
        
    def check_regular(self) -> bool:
        path_contracts = f'{SCRIPT_LOC}/data/Выгрузка контрактов по Заказчику.xlsx'
        path_voc = f'{SCRIPT_LOC}/data/КПГЗ ,СПГЗ, СТЕ.xlsx'

        contracts = pd.read_excel(path_contracts)
        voc = pd.read_excel(path_voc)

        ph = PurchaseHistory(self.user_pick, voc, contracts)

        ph.get_purchases(include_rk=True, include_kpgz=True)
        ph.generate_features()
        ph.drop_cancelled()

        return ph.check_regular_purchase()
    
    def get_purchase_stats(self, period: int, summa: bool):

        df = self.get_history(100)

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
            plt.title(f'Статистика закупок\n{self.user_pick}')
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
            plt.title(f'Статистика закупок\n{self.user_pick}')
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
        
    def get_forecast(self, period):
        if self.check_regular() == False:
            return {'state': 'Not regular', 'prediction': 0, 'plot_image': str()}

        df = self.get_history(100)

        if period == 1:
            df = df.groupby('year')['Оплачено, руб.'].sum()
            model = ARIMA(df, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=1)
            next_period = df.index[-1] + 1
            df.loc[next_period] = forecast.values[0]

        elif period == 2:
            df = df.groupby(['year', 'quarter'])['Оплачено, руб.'].sum()
            model = ARIMA(df, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=1)
            last_year, last_quarter = df.index[-1]
            next_period = (last_year, last_quarter % 4 + 1) if last_quarter < 4 else (last_year + 1, 1)
            df.loc[next_period] = forecast.values[0]

        elif period == 3:
            df = df.groupby(['year', 'month'])['Оплачено, руб.'].sum()
            model = ARIMA(df, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=1)
            last_year, last_month = df.index[-1]
            next_period = (last_year, last_month % 12 + 1) if last_month < 12 else (last_year + 1, 1)
            df.loc[next_period] = forecast.values[0]

        plt.figure(figsize=(10, 5))
        if period == 1:
            plt.plot(df.index[:-1], df.values[:-1], color='#B12725', label='История')
            plt.plot([df.index[-2], df.index[-1]], [df.values[-2], df.values[-1]], 'o--', color='#2B7A78', label='Прогноз')
            plt.xlabel('Год')
            plt.xticks(df.index)

        elif period == 2:
            actual_index = [f'{year}-Q{quarter}' for year, quarter in df.index[:-1]]
            forecast_index = [f'{year}-Q{quarter}' for year, quarter in [df.index[-2], df.index[-1]]]
            plt.plot(actual_index, df.values[:-1], color='#B12725', label='История')
            plt.plot(forecast_index, df.values[-2:], 'o--', color='#2B7A78', label='Прогноз')
            plt.xlabel('Квартал')
            plt.xticks(actual_index + [forecast_index[-1]], rotation=45)

        elif period == 3:
            actual_index = [f'{year}-{month:02d}' for year, month in df.index[:-1]]
            forecast_index = [f'{year}-{month:02d}' for year, month in [df.index[-2], df.index[-1]]]
            plt.plot(actual_index, df.values[:-1], color='#B12725', label='История')
            plt.plot(forecast_index, df.values[-2:], 'o--', color='#2B7A78', label='Прогноз')
            plt.xlabel('Месяц')
            plt.xticks(actual_index + [forecast_index[-1]], rotation=45)

        plt.title(f'Прогноз закупок\n{self.user_pick}')
        plt.ylabel('Цена')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        plot_image = base64.b64encode(buf.read()).decode('utf-8')

        return {
            'state': 'Success',
            'prediction': float(forecast.values[0]),
            'plot_image': plot_image
        }
    
    def get_user_pick_info(self):
        df = pd.read_excel(f'{SCRIPT_LOC}/data/КПГЗ ,СПГЗ, СТЕ.xlsx')
        df = df[df['Название СТЕ'] == self.user_pick]

        spgz_code = str(df['СПГЗ код'].values[0])
        spgz_name = str(df['СПГЗ'].values[0])

        return {
            'STE': self.user_pick,
            'SPGZ_code': spgz_code,
            'SPGZ_name': spgz_name
        }