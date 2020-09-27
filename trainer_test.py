# %%
from transformers import BertForSequenceClassification

model = BertForSequenceClassification.from_pretrained('bert-base-uncased', return_dict=True)
model.train()

# %%
from transformers import AdamW

# %%
no_decay = ['biad', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
    {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0 }
]
#optimizer = AdamW(model.parameters(), lr=1e-5)
optimizer = AdamW(optimizer_grouped_parameters, lr=1e-5)

# %%
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
text_batch = ["I love Pixer.", "I don't care for Pixer."]
encoding = tokenizer(text_batch, return_tensors='pt', padding=True, truncation=True)
input_ids = encoding['input_ids']
attention_mask = encoding['attention_mask']

# %%
labels = torch.tensor([1, 0]).unsqueeze(0)
outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
loss = outputs.loss
loss.backward()
optimizer.step()

# %%
from transformers import BertTokenizer, glue_convert_examples_to_features
import tensorflow as tf
import tensorflow_datasets as tfds

# %%
data = tfds.load('glue/mrpc')
#train_dataset = glue_convert_examples_to_features(data['train'], tokenizer, max_length=128, task='mrpc')

# %%
