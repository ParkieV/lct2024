import os

import numpy as np
import pandas as pd
import torch
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import process

from api.src.configurations.models import model, tokenizer
from api.src.services.text_service import Dataset

script_loc = os.path.dirname(os.path.realpath(__file__))

class PromptMatching:
    ''' Поиск похожих товаров по введенному пользователем запросу

    Аттрибуты:
        original_column: название колонки с оригинальными названиями товаров
        processed_column: название колонки с обработанными названиями товаров
        embeddings_column: название колонки с эмбеддингами товаров
        preprocessor: объект класса Dataset для обработки текста
    '''
    def __init__(self):
        ''' Инициализация класса
        
        '''
        self.original_column = 'Название СТЕ'
        self.processed_column = 'Название СТЕ processed'
        self.embeddings_column = 'КПГЗ'

        self.preprocessor = Dataset(pd.read_excel(f'{script_loc}/data/processed_names.xlsx'), text_col=self.processed_column)
        

    def get_embeddings(self, texts):
        ''' Получить эмбеддинги текстов

        Вход:
            texts: список текстов

        Выход:
            embeddings: эмбеддинги текстов полученные с помощью модели RuBERT-Base
        '''
        inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)

        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings

    def match(self, user_prompt, top_n):
        ''' Поиск похожих товаров по введенному пользователем запросу

        Вход:
            user_prompt: запрос пользователя
            top_n: количество наиболее похожих товаров
        
        Выход:
            {'values': список наиболее похожих товаров}
        '''
        
        df = pd.read_excel(f'{script_loc}/data/processed_names.xlsx')

        goods = df[self.processed_column].tolist()

        self.preprocessor.prepare_dataset(process_russian_text_type='lemmatizer')
        df = self.preprocessor.data.copy()
        user_prompt = self.preprocessor.prepare_sentence(user_prompt, process_russian_text_type='lemmatizer')

        results = process.extract(user_prompt, goods, limit=top_n)
        most_similar = [result[0] for result in results]

        self.df = df[df[self.processed_column].isin(most_similar)]
        product_embeddings = self.get_embeddings(self.df[self.embeddings_column].tolist())

        help_embedding = self.get_embeddings([user_prompt])

        similarities = cosine_similarity(help_embedding, product_embeddings).flatten()
        self.df['similarity'] = similarities
        self.df = self.df.sort_values(by='similarity', ascending=False)

        return {'values': self.df[self.original_column].to_list()}
