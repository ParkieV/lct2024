import re
import os

import numpy as np
import pandas as pd
import torch
import nltk
import json

from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from sklearn.linear_model import Ridge
from nltk.stem.snowball import SnowballStemmer
from pymystem3 import Mystem
from thefuzz import process


reference_model = None
leftovers_model = None
sales_model = None
script_loc = os.path.dirname(os.path.realpath(__file__))
tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased")


class Dataset:

    def __init__(self, data, text_col):

        self.data = data
        self.text_col = text_col
        self.data[text_col] = self.data[text_col].str.lower()
        self.drop_empty()

        self.russian_stopwords = set(stopwords.words('russian'))
        self.stemmer = SnowballStemmer('russian')
        self.mystem = Mystem()

        _ = nltk.download('stopwords')

    @staticmethod
    def delete_punct(text):

        punc_list = [".",";",":","!","?","/","\\","#","@","$","&",")","(","'","\"", "*", "-", "№", "`", "+", "|", "[", "]", "{", "}", "_"]
        for punc in punc_list:
            text = text.replace(punc, ' ', -1)
        
        return text
    
    @staticmethod
    def replace_commas(text):
        digits = '0123456789'
        
        if text[0] == ',':
             text = text[1:]
        
        if text[-1] == ',':
             text = text[:-1]
             
        if (',' in text):

            parts = text.split(',')
            for i in range(len(parts) - 1):
                if( parts[i] and parts[i+1]) and (parts[i][-1] in digits) and (parts[i+1][0] in digits):
                    parts[i] += ','
                else:
                    parts[i] += ' '

            return ''.join(parts)

        else:
             return text
    
    @staticmethod
    def add_spaces(text):
        # разделяет пробелом слова и числа

        result = ''
        for i in range(len(text) - 1):
            if text[i].isdigit() and text[i+1].isalpha():
                result += text[i] + ' '
            elif text[i].isalpha() and text[i+1].isdigit():
                result += text[i] + ' '
            else:
                result += text[i]

        result += text[-1]  # добавляем последний символ
        
        text = re.sub(r'\s+', ' ', result) # заменяет подряд идущие пробелы на один пробел
        return text
    
    @staticmethod
    def delete_big_nums(text):
        # удаляет числа больше 4 знаков
        text = re.sub(r'\b\d{3,}\b', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    
    @staticmethod
    def remove_russian_stopwords(text, russian_stopwords):
        
        # убирает ненужные слова
        text_without_stopwords = [word for word in text.split() if word.lower() not in russian_stopwords]
        return ' '.join(text_without_stopwords)

    @staticmethod
    def stem_russian_text(text, stemmer):
    
        stemmed_text = ' '.join([stemmer.stem(word) for word in text.split()])
        return stemmed_text

    @staticmethod
    def lemmatize_russian_text(text, mystem):

        lemmatized_text = ''.join(mystem.lemmatize(text)).strip()
        return lemmatized_text

    def lower(self):

        self.data = self.data.applymap(lambda x: str(x).lower() if pd.notnull(x) else x)

    def drop_empty(self):

        self.data = self.data[self.data[self.text_col].str.strip() != '']

    def process_russian_series(self, series, process_russian_text_type):

        result_series = series.copy()

        if process_russian_text_type == 'lemmatizer':
            result_series = result_series.apply(lambda x: Dataset.lemmatize_russian_text(x, self.mystem))
        
        elif process_russian_text_type == 'stemmer':
             result_series = result_series.apply(lambda x: Dataset.stem_russian_text(x, self.mystem))
        
        else:
             return "incorrect type"
        
        return result_series

    def process_russian_sentence(self, sentence, process_russian_text_type):

        result_sentence = ''

        if process_russian_text_type == 'lemmatizer':
            result_sentence = Dataset.lemmatize_russian_text(sentence, self.mystem)
        
        elif process_russian_text_type == 'stemmer':
             result_sentence = Dataset.stem_russian_text(sentence, self.stemmer)
        
        else:
             return "incorrect type"
        
        return result_sentence
    
    def prepare_dataset(self,
                        delete_punct=True,
                        replace_commas=True,
                        add_spaces=False,
                        delete_big_nums=True,
                        remove_russian_stopwords=True,
                        process_russian_text_type=None) -> None:
        
        if delete_punct:
            self.data[self.text_col] = self.data[self.text_col].apply(Dataset.delete_punct)

        if replace_commas:
            self.data[self.text_col] = self.data[self.text_col].apply(Dataset.replace_commas)

        if add_spaces:
            self.data[self.text_col] = self.data[self.text_col].apply(Dataset.add_spaces)

        if delete_big_nums:
            self.data[self.text_col] = self.data[self.text_col].apply(Dataset.delete_big_nums)

        if remove_russian_stopwords:
            self.data[self.text_col] = self.data[self.text_col].apply(lambda x: Dataset.remove_russian_stopwords(x, self.russian_stopwords))
        
        if process_russian_text_type:
            self.data[self.text_col] = self.process_russian_series(self.data[self.text_col], process_russian_text_type=process_russian_text_type)
        
        self.drop_empty()

    def prepare_sentence(self,
                         sentence: str,
                         delete_punct=True,
                         replace_commas=True,
                         add_spaces=False,
                         delete_big_nums=True,
                         remove_russian_stopwords=True,
                         process_russian_text_type=None):
        
        sentence = sentence.lower()
        
        if delete_punct:
            sentence = Dataset.delete_punct(sentence)

        if replace_commas:
            sentence = Dataset.replace_commas(sentence)

        if add_spaces:
            sentence = Dataset.add_spaces(sentence)

        if delete_big_nums:
            sentence = Dataset.delete_big_nums(sentence)

        if remove_russian_stopwords:
            sentence = Dataset.remove_russian_stopwords(sentence, self.russian_stopwords)
        
        if process_russian_text_type:
            sentence = self.process_russian_sentence(sentence, process_russian_text_type=process_russian_text_type)

        return sentence


class PromptMatching:
    def __init__(self, path_to_data, original_column, processed_column, embeddings_column=None):
        self.df = pd.read_excel(path_to_data)

        self.original_column = original_column
        self.processed_column = processed_column
        self.embeddings_column = embeddings_column

        self.preprocessor = Dataset(self.df, text_col=processed_column)

    def get_embeddings(self, texts):
        inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)

        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings

    def match(self, user_prompt, top_n):

        goods = self.df[self.processed_column].tolist()

        self.preprocessor.prepare_dataset(process_russian_text_type='lemmatizer')
        self.df = self.preprocessor.data.copy()
        user_prompt = self.preprocessor.prepare_sentence(user_prompt, process_russian_text_type='lemmatizer')

        results = process.extract(user_prompt, goods, limit=top_n)
        most_similar = [result[0] for result in results]

        self.df = self.df[self.df[self.processed_column].isin(most_similar)]
        product_embeddings = self.get_embeddings(self.df[self.embeddings_column].tolist())

        help_embedding = self.get_embeddings([user_prompt])

        similarities = cosine_similarity(help_embedding, product_embeddings).flatten()
        self.df['similarity'] = similarities
        self.df = self.df.sort_values(by='similarity', ascending=False)

        return {'values': self.df[self.original_column].to_list()}
    

class FindLeftovers:
    def __init__(self, reference_df: str, concat_leftovers_df: str):
        
        self.reference_df = pd.read_excel(reference_df)
        self.concat_leftovers_df = pd.read_excel(concat_leftovers_df)
        self.kpgz = None

        self.leftover_name = ''
        self.code = 0
        self.preprocessor = Dataset(self.concat_leftovers_df, text_col='Name processed')

    @staticmethod
    def find_kpgz(df, user_pick) -> str:
        kpgz = df[df['Название СТЕ'] == user_pick]['КПГЗ'].values[0]

        return kpgz
    
    @staticmethod
    def get_embeddings(texts):
        inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)

        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings
    
    def find_similar_leftover(self, user_choice):
        goods = self.concat_leftovers_df['Name processed'].tolist()
        kpgz = self.find_kpgz(self.reference_df, user_choice)

        results = process.extract(kpgz, goods, limit=10)
        most_similars = [result[0] for result in results]

        filtered_df = self.concat_leftovers_df[self.concat_leftovers_df['Name processed'].isin(most_similars)]
        embeddings_list = filtered_df['embeddings'].apply(lambda x : [float(x) for x in x.replace("[", "").replace ("]", "").split(',')])
        product_embeddings = list(embeddings_list)
        help_embedding = self.get_embeddings([user_choice])

        similarities = cosine_similarity(help_embedding, product_embeddings).flatten()
        filtered_df['similarity'] = similarities
        filtered_df = filtered_df.sort_values(by='similarity', ascending=False)

        if filtered_df.iloc[0]['similarity'] > 0.77:

            most_similar = filtered_df.head(1)['Name processed'].iloc[0]

            self.leftover_name = self.concat_leftovers_df[self.concat_leftovers_df['Name processed'] == most_similar]['Name'].values[0]
            self.code = int(self.concat_leftovers_df[self.concat_leftovers_df['Name processed'] == most_similar]['Code1'].iloc[0])

        else:
            self.code = 404
            self.leftover_name = user_choice

    def leftover_info(self, path_to_data):
        if self.code == 0:
            raise Exception("Not fitted on previous method! Call find_similar_leftovers()")
        
        if self.code == 404:
            return {'4Q2022|остаток кон|балансовая стоимость': 0, '4Q2022|остаток кон|количество': 0, '4Q2022|остаток кон|остаточная стоимость': 0}
        
        df =  pd.read_excel(f'{path_to_data}/Остатки {self.code}.xlsx')

        columns_to_out = ['4Q2022|остаток кон|балансовая стоимость', '4Q2022|остаток кон|количество', '4Q2022|остаток кон|остаточная стоимость']

        df = df[df['Name'] == self.leftover_name][columns_to_out].sum()

        return df.to_dict()


def embed_bert_cls(text, model, tokenizer):
    t = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**{k: v.to(model.device) for k, v in t.items()})
    embeddings = model_output.last_hidden_state[:, 0, :]
    embeddings = torch.nn.functional.normalize(embeddings)
    return embeddings[0].cpu().numpy()


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
            embed = embed_bert_cls(sent.lower(), model, tokenizer)
            contract_embeds.append(embed)

        contract_embeds_df = pd.DataFrame(contract_embeds, index=self.normalized_spgz_contracts.index)
        contracts_merged = pd.merge(self.normalized_spgz_contracts, contract_embeds_df, left_index=True, right_index=True)

        query_embed = embed_bert_cls(self.normalized_ste_voc['Название СТЕ'].values[0], model, tokenizer)

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


def matching_service_reference(prompt: str, top_n):
    output = reference_model.match(prompt, top_n)

    return output


def get_leftovers(prompt: str):
        
    leftovers_model.find_similar_leftover(prompt)
    return leftovers_model.leftover_info(script_loc + '/data/')


def is_regular(user_pick: str):
    path_contracts = f'{script_loc}/data/Выгрузка контрактов по Заказчику.xlsx'
    path_voc = f'{script_loc}/data/КПГЗ ,СПГЗ, СТЕ.xlsx'

    contracts = pd.read_excel(path_contracts)
    voc = pd.read_excel(path_voc)

    ph = PurchaseHistory(user_pick, voc, contracts)

    ph.get_purchases(include_rk=True, include_kpgz=True)
    ph.drop_cancelled()

    return ph.check_regular_purchase()

def pick_history(user_pick: str):
    path_contracts = f'{script_loc}/data/Выгрузка контрактов по Заказчику.xlsx'
    path_voc = f'{script_loc}/data/КПГЗ ,СПГЗ, СТЕ.xlsx'

    contracts = pd.read_excel(path_contracts)
    voc = pd.read_excel(path_voc)

    ph = PurchaseHistory(user_pick, voc, contracts)

    ph.get_purchases(include_rk=True, include_kpgz=True)
    ph.drop_cancelled()

    return ph.generate_features()


def pick_history(user_pick: str):
    path_contracts = f'{script_loc}/data/Выгрузка контрактов по Заказчику.xlsx'
    path_voc = f'{script_loc}/data/КПГЗ ,СПГЗ, СТЕ.xlsx'

    contracts = pd.read_excel(path_contracts)
    voc = pd.read_excel(path_voc)

    ph = PurchaseHistory(user_pick, voc, contracts)

    ph.get_purchases(include_rk=True, include_kpgz=True)
    ph.drop_cancelled()

    return ph.generate_features()


def init_models():
    nltk.download('stopwords')

    global reference_model, leftovers_model, sales_model

    sales_model =  None
    reference_model = PromptMatching(f'{script_loc}/data/processed_names.xlsx', 'Название СТЕ', 'Название СТЕ processed', 'КПГЗ')
    leftovers_model = FindLeftovers(f'{script_loc}/data/processed_names.xlsx', f'{script_loc}/data/concat_leftovers.xlsx')
