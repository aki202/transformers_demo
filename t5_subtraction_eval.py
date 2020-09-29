# %%
# Importing stock libraries
import numpy as np
import torch
import torch.nn.functional as F
from pprint import pprint as pp

# Importing the T5 modules from huggingface/transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration, AdamW, Trainer, TrainingArguments

# %%
tokenizer = T5Tokenizer.from_pretrained("save/t5_subtraction")
model = T5ForConditionalGeneration.from_pretrained("save/t5_subtraction")

# %%
x_batch = []
y_batch = []
with open('./data/subtraction_data.txt') as f:
    for line in f:
        x, y = line.strip().split(' ')
        x_batch.append('calc Formula to Answer: {} </s>'.format(x))
        y_batch.append('{} </s>'.format(y))

# %%
print(len(x_batch), len(y_batch))
print(x_batch[0:3])
print(y_batch[0:3])

# %%
input_formula = 'calc Formula to Answer: 123-10 </s>'
input_encoding = tokenizer([input_formula], return_tensors='pt', padding=True)

output = model.generate(input_ids=input_encoding['input_ids'],
               attention_mask=input_encoding['attention_mask'])

tokenizer.decode(output[0])

# %%
