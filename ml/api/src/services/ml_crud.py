import re
import os

import numpy as np
import pandas as pd

from api.src.services.matching_service import PromptMatching

def matching_service_reference(user_prompt):
    prompt_matching = PromptMatching()
    return prompt_matching.match(user_prompt, 15)


def is_regular(model):
    return model.check_regular()