import re
import os

import numpy as np
import pandas as pd
import torch
import nltk

from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from pymystem3 import Mystem
from thefuzz import process

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

        self.tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
        self.model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased")

        self.preprocessor = Dataset(self.df, text_col=processed_column)

    def get_embeddings(self, texts):
        inputs = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)

        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings

    def match(self, user_prompt, top_n):

        goods = self.df[self.processed_column].tolist()

        self.preprocessor.prepare_dataset(process_russian_text_type='lemmatizer')
        self.df = self.preprocessor.data.copy()
        user_prompt = self.preprocessor.prepare_sentence(user_prompt, process_russian_text_type='lemmatizer')

        results = process.extract(user_prompt, goods, limit=top_n)
        most_similar = [result[0] for result in results]

        processed_df = self.df.copy()
        processed_df = processed_df[processed_df[self.processed_column].isin(most_similar)]

        product_embeddings = self.get_embeddings(processed_df[self.embeddings_column].tolist())
        user_prompt_embedding = self.get_embeddings([user_prompt])

        similarities = cosine_similarity(user_prompt_embedding, product_embeddings).flatten()

        processed_df['similarity'] = similarities

        processed_df = processed_df.sort_values(by='similarity', ascending=False)

        return {'values': processed_df[self.original_column].to_list()}



reference_model = None

def init_models():
    script_loc = os.path.dirname(os.path.realpath(__file__))
    nltk.download('stopwords')

    global reference_model
    reference_model = PromptMatching(f'{script_loc}/data/processed_names.xlsx', 'Название СТЕ', 'Название СТЕ processed', 'КПГЗ')

def matching_service_reference(prompt: str):

    output = reference_model.match(prompt, 15)

    return output


