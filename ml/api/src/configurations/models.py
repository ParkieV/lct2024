from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased")
tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")