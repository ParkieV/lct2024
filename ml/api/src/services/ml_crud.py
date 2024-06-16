import re
import os

import numpy as np
import pandas as pd

from api.src.services.matching_service import PromptMatching

def matching_service_reference(user_prompt):
    ''' Поиск похожих товаров по введенному пользователем запросу

    Вход:
        user_prompt: запрос пользователя

    Выход:
        {'values': список наиболее похожих товаров}
    '''
    prompt_matching = PromptMatching()
    return prompt_matching.match(user_prompt, 15)


def is_regular(model):
    ''' Проверка на регулярность

    Вход:
        model: модель
    
    Выход:
        результат проверки на регулярность
    '''
    return model.check_regular()