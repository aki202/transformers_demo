# %%
import textwrap
from tqdm.auto import tqdm
from sklearn import metrics
from torch.utils.data import DataLoader
from torch import cuda
from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer,
    get_linear_schedule_with_warmup
)

from t5_imdb.dataset import ImdbDataset

# %%
model = T5ForConditionalGeneration.from_pretrained('save/t5_base_imdb_sentiment')
tokenizer = T5Tokenizer.from_pretrained('save/t5_base_imdb_sentiment')
dataset = ImdbDataset(tokenizer, 'data/aclImdb', 'test', max_len=512)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# %%
it = iter(loader)
batch = next(it)
batch["source_ids"].shape

# %%
batch_source_ids = batch['source_ids'].cuda() if cuda.is_available() else batch['source_ids']
batch_source_mask = batch['source_mask'].cuda() if cuda.is_available() else batch['source_mask']
outs = model.generate(input_ids=batch_source_ids,
                      attention_mask=batch_source_mask,
                      max_length=2)

dec = [tokenizer.decode(ids) for ids in outs]

texts = [tokenizer.decode(ids) for ids in batch['source_ids']]
targets = [tokenizer.decode(ids) for ids in batch['target_ids']]

# %%
for i in range(len(texts)):
    lines = textwrap.wrap("Review:\n%s\n" % texts[i], width=100)
    print("\n".join(lines))
    print("\nActual sentiment: %s" % targets[i])
    print("Predicted sentiment: %s" % dec[i])
    print("=====================================================================\n")
