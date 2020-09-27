# %%
# Importing stock libraries
import numpy as np
import torch
import torch.nn.functional as F
from pprint import pprint as pp

# Importing the T5 modules from huggingface/transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration, AdamW, Trainer, TrainingArguments

# %%
tokenizer = T5Tokenizer.from_pretrained("t5-base")
model = T5ForConditionalGeneration.from_pretrained("t5-base")

# %%
x_batch = []
y_batch = []
with open('./data/subtraction_data.txt') as f:
    for line in f:
        x, y = line.strip().split(' ')
        x_batch.append('calc Number to Number: {} </s>'.format(x))
        y_batch.append('{} </s>'.format(y))

# %%
print(len(x_batch), len(y_batch))
print(x_batch[0:3])
print(y_batch[0:3])

# %%
input_encoding = tokenizer(x_batch, return_tensors='pt', padding=True)
input_ids = input_encoding['input_ids']
input_attention_mask = input_encoding['attention_mask']

# %%
output_encoding = tokenizer(y_batch, return_tensors='pt', padding=True)
output_ids = output_encoding['input_ids']
output_attention_mask = output_encoding['attention_mask']

# %%
optimizer = AdamW(model.parameters(), lr=1e-5)

# %%
class DataSet(torch.utils.data.Dataset):
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, index):
        return {
            'input_ids': self.X[index],
            'labels': self.Y[index],
        }

dataset = DataSet(input_ids, output_ids)

# %%
training_args = TrainingArguments(
    output_dir='./results',          # output directory
    num_train_epochs=1,              # total number of training epochs
    logging_dir='./logs',            # directory for storing logs
)

trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=dataset,         # training dataset
)

# %%
trainer.train()

# %%
tokenizer.save_pretrained('save/t5_subtraction')
model.save_pretrained('save/t5_subtraction')
