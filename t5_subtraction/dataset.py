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
        else: raise 'Invalid "type_path"'

        with open('./data/subtraction_data.txt', 'r') as f:
            lines = f.readlines()
            for line in lines[lines_range[0]:lines_range[1]]:
                x, y = line.strip().split(' ')
                x = x  + ' </s>'
                y = y  + ' </s>'

                # tokenize inputs
                tokenized_inputs = self.tokenizer.batch_encode_plus(
                    [x], max_length=8, pad_to_max_length=True,
                    return_tensors="pt", truncation=True
                )
                # tokenize targets
                tokenized_targets = self.tokenizer.batch_encode_plus(
                    [y], max_length=5, pad_to_max_length=True,
                    return_tensors="pt", truncation=True
                )

                self.inputs.append(tokenized_inputs)
                self.targets.append(tokenized_targets)

# %%
if __name__ == '__main__':
    from transformers import T5Tokenizer
    tokenizer = T5Tokenizer.from_pretrained('t5-base')
    dataset = SubtractionDataset(tokenizer, type_path='val')
    print(len(dataset))
    data = dataset[28]
    print(tokenizer.decode(data['source_ids']))
    print(tokenizer.decode(data['target_ids']))


# %%
