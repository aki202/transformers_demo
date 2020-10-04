# %%
import glob
import os
import json
import re
from torch.utils.data import Dataset
from transformers import T5Tokenizer
tokenizer = T5Tokenizer.from_pretrained('t5-base')

# %%
def datum_to_pair(datum):
    source = 'translate SQL to English: {} </s>'.format(datum['query'])
    target = '{} </s>'.format(datum['question'])
    return source, target

# %%
all_inputs = []
all_outputs = []

spider_json = json.load(open('./data/spider/train_spider.json'))
others_json = json.load(open('./data/spider/train_others.json'))
dev_json = json.load(open('./data/spider/dev.json'))

for datum in spider_json:
    _input, _output = datum_to_pair(datum)
    all_inputs.append(_input)
    all_outputs.append(_output)

for datum in spider_json:
    _input, _output = datum_to_pair(datum)
    all_inputs.append(_input)
    all_outputs.append(_output)

for datum in others_json:
    _input, _output = datum_to_pair(datum)
    all_inputs.append(_input)
    all_outputs.append(_output)

for datum in dev_json:
    _input, _output = datum_to_pair(datum)
    all_inputs.append(_input)
    all_outputs.append(_output)

# tokenize inputs
tokenized_inputs = tokenizer.batch_encode_plus(
    all_inputs, padding=True, return_tensors="pt", truncation=True
)
# tokenize targets
tokenized_targets = tokenizer.batch_encode_plus(
    all_outputs, padding=True, return_tensors="pt", truncation=True
)

# %%
print(len(all_inputs))
print(tokenized_inputs['input_ids'][0].shape) # (250)
print(tokenized_targets['input_ids'][0].shape) # (50)
#print('x:{},\ty:{},\t{}\t{}'.format(x, y, source, target))

# %%
