# %%
from flask import Flask, request, redirect, url_for, abort, jsonify
from flask_cors import CORS

import argparse
import textwrap
from torch.utils.data import DataLoader
from torch import cuda
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer
)

from pprint import pprint as pp

# %%
parser = argparse.ArgumentParser(description='evaluate sql_to_en model using t5')
parser.add_argument('-m', '--model', help='model to use', default='t5_sql_to_en__E2')
params = parser.parse_args(args=[])
#params = parser.parse_args()

print('Model name: {}'.format(params.model))
print('')

# %%
print('Loading model')
model = T5ForConditionalGeneration.from_pretrained('save/' + params.model)
tokenizer = T5Tokenizer.from_pretrained('t5-base')

# %%
app = Flask(__name__)

@app.route("/", methods=["POST"])
def receive():
    query = request.json['query']

    source = 'translate SQL to English: {} </s>'.format(query)
    raw_batch = tokenizer.batch_encode_plus(
        [source], max_length=250, padding='max_length', return_tensors="pt",
        truncation=True
    )

    source_ids = raw_batch["input_ids"]
    source_mask = raw_batch["attention_mask"]

    if cuda.is_available():
        model.to('cuda')
        source_ids = source_ids.cuda()

    outs = model.generate(input_ids=source_ids, attention_mask=source_mask)

    dec = [tokenizer.decode(ids) for ids in outs]
    return jsonify({"language": "python", 'res': dec[0]})

@app.route("/", methods=["OPTIONS"])
def option():
    resp = flask.Response('OK')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# %%
CORS(app)
app.run()
