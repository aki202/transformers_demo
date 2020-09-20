# %%
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pprint import pprint as pp

# %%
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
classifier = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

# %%
batch = tokenizer(
  ['I love you', 'All you need is kill'],
  padding=True,
  truncation=True,
  return_tensors='pt'
)
pp(batch)

# %%
outputs = model(**batch)

# %%
outputs

# %%


# %%
