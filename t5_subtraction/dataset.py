# %%
import glob
import os
import json
import re
from torch.utils.data import Dataset

# %%
class SubtractionDataset(Dataset):
    def __init__(self, tokenizer, type_path = 'train'):
        self.tokenizer = tokenizer
        self.type_path = type_path
        self.inputs = []
        self.targets = []

        self._build()

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        source_ids = self.inputs[index]["input_ids"].squeeze()
        target_ids = self.targets[index]["input_ids"].squeeze()

        source_mask = self.inputs[index]["attention_mask"].squeeze() # might need to squeeze
        target_mask = self.targets[index]["attention_mask"].squeeze() # might need to squeeze

        return {
            "source_ids": source_ids,
            "source_mask": source_mask,
            "target_ids": target_ids,
            "target_mask": target_mask
        }

    def _build(self):
        if self.type_path == 'train':
            lines_range = [0, 30000]
        elif self.type_path == 'test':
            lines_range = [30000, 40000]
        elif self.type_path == 'val':
            lines_range = [40000, 50000]
        elif self.type_path == 'mini':
            lines_range = [0, 20]
        else: raise 'Invalid "type_path"'

        with open('./data/subtraction_data.txt', 'r') as f:
            lines = f.readlines()
            for line in lines[lines_range[0]:lines_range[1]]:
                x, y = line.strip().split(' ')
                spaced_x = re.sub(r'(.)', r'\1 ', x).strip()
                spaced_y = re.sub(r'(.)', r'\1 ', y).strip()
                source = 'calc Formula to Answer: {} </s>'.format(spaced_x)
                target = spaced_y  + ' </s>'

                # tokenize inputs
                tokenized_inputs = self.tokenizer.batch_encode_plus(
                    [source], padding=True, return_tensors="pt", truncation=False
                )
                # tokenize targets
                tokenized_targets = self.tokenizer.batch_encode_plus(
                    [target], padding=True, return_tensors="pt", truncation=False
                )

                #print('x:{},\ty:{},\t{}\t{}'.format(x, y, source, target))

                self.inputs.append(tokenized_inputs)
                self.targets.append(tokenized_targets)

# %%
if __name__ == '__main__':
    from transformers import T5Tokenizer
    tokenizer = T5Tokenizer.from_pretrained('t5-base')
# %%
    dataset = SubtractionDataset(tokenizer, type_path='mini')
# %%
    print('len={}'.format(len(dataset)))
    data = dataset[10]
    print(data)
    for _id in data['source_ids']:
        id = _id.item()
        token = tokenizer.decode(id)
        print('{}({}), '.format(token, id), end='')
    print('')
    print("'{}'".format(tokenizer.decode(data['source_ids'])))
    print("'{}'".format(tokenizer.decode(data['target_ids'])))


# %%
