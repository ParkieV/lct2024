import os

import pickle
import whisper
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased")
tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")

SCRIPT_LOC = os.path.dirname(os.path.realpath(__file__))
model_file_path = SCRIPT_LOC + '/model_weights/whisper.pickle'

# Check if the whisper exists
if os.path.exists(model_file_path):
    with open(model_file_path, 'rb') as handle:
        whisper_model = pickle.load(handle)
else:
    # Download the model
    whisper_model = whisper.load_model("small")

    # Save the model
    with open(model_file_path, 'wb') as handle:
        pickle.dump(whisper_model, handle, protocol=pickle.HIGHEST_PROTOCOL)