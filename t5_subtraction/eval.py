# %%
import textwrap
from torch.utils.data import DataLoader
from torch import cuda
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer
)

from t5_subtraction.dataset import SubtractionDataset

# %%
model = T5ForConditionalGeneration.from_pretrained('save/t5_subtraction')
tokenizer = T5Tokenizer.from_pretrained('save/t5_subtraction')
dataset = SubtractionDataset(tokenizer, type_path='test')
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# %%
it = iter(loader)
batch = next(it)
#batch["source_ids"].shape
#print(batch)
for _id in batch['source_ids'][0]:
    id = _id.item()
    token = tokenizer.convert_ids_to_tokens(id)
    print('id: {} / {}'.format(id, token))

# %%
batch_source_ids = batch['source_ids'].cuda() if cuda.is_available() else batch['source_ids']
batch_source_mask = batch['source_mask'].cuda() if cuda.is_available() else batch['source_mask']
outs = model.generate(input_ids=batch_source_ids,
                      attention_mask=batch_source_mask,
                      max_length=5)

dec = [tokenizer.decode(ids) for ids in outs]

texts = [tokenizer.decode(ids) for ids in batch['source_ids']]
targets = [tokenizer.decode(ids) for ids in batch['target_ids']]

# %%
for i in range(len(texts)):
    lines = textwrap.wrap("Formula:\n%s\n" % texts[i], width=100)
    print("\n".join(lines))
    print("\nActual: %s" % targets[i])
    print("Predicted: %s" % dec[i])
    print("=====================================================================\n")

# %%
