# %%
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import textwrap
from torch.utils.data import DataLoader
from torch import cuda
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer
)

from t5_sql_to_en.dataset import SQLDataset

# %%
model = T5ForConditionalGeneration.from_pretrained('save/t5_sql_to_en')
tokenizer = T5Tokenizer.from_pretrained('save/t5_sql_to_en')
dataset = SQLDataset(tokenizer, type_path='val')

# %%
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# %%
print(dataset[0]['source_ids'].shape)
print(dataset[1]['source_ids'].shape)

# %%
it = iter(loader)
batch = next(it)
#batch["source_ids"].shape
#print(batch)
for _id in batch['source_ids'][0]:
    id = _id.item()
    token = tokenizer.decode(id)
    print('{}'.format(token), end='')
for _id in batch['target_ids'][0]:
    id = _id.item()
    token = tokenizer.decode(id)
    print('{}'.format(token), end='')

# %%
batch_source_ids = batch['source_ids']
batch_source_mask = batch['source_mask']
outs = model.generate(input_ids=batch_source_ids,
                      attention_mask=batch_source_mask)

dec = [tokenizer.decode(ids) for ids in outs]

texts = [tokenizer.decode(ids) for ids in batch['source_ids']]
targets = [tokenizer.decode(ids) for ids in batch['target_ids']]

# %%
for i in range(len(texts)):
    lines = textwrap.wrap(texts[i], width=100)
    sql = '\n'.join(lines).replace('translate SQL to English: ', '')
    print('SQL: {}'.format(sql))
    print("\nActual: %s" % targets[i])
    print("Predicted: %s" % dec[i])
    print("=====================================================================\n")

# %%
