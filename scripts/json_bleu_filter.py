# %%
'''
Filter out low-bleu samples.

python scripts/json_bleu_filter.py data/spider/tree_trans15.json data/spider/tree_trans15_sim01.json 0.1
'''
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from pprint import pprint as pp
from nltk import bleu_score, word_tokenize
import json
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('src_json', type=str)
parser.add_argument('dst_json', type=str)
parser.add_argument('threshold', type=float)
args = parser.parse_args()

jsons = json.load(open(args.src_json))

stop_words = ['a', 'an', 'what', 'find', 'the', 'of', 'in', 'which', 'show', 'return', 'list', '.', '?']

def trim_stop_words(src: [str]):
    return [e for e in src if e not in stop_words]

def similarity(str1: [str], str2: [str]):
    point: int = 0
    for e in str1:
        if e in str2: point += 1
    return point / len(str1)

counts = {
    'all': 0,
    'extra': 0,
    'hard': 0,
    'medium': 0,
    'easy': 0,
}
new_samples = []

for (idx, sample) in enumerate(jsons):
    go = trim_stop_words(word_tokenize(sample['original_question'].lower()))
    hy = trim_stop_words(word_tokenize(sample['question'].lower()))
    #bleu4 = bleu_score.sentence_bleu([go], hy)
    simil = similarity(hy, go)

    catalog = True
    if simil < args.threshold: catalog = False
    if simil >= args.threshold + 0.1: catalog = False

    print('[{}] {} {}'.format(idx, catalog, sample['query']))
    #print('bleu: {}'.format(bleu4))
    print('simi: {}'.format(simil))
    print('org: {}'.format(sample['original_question']))
    print('new: {}'.format(sample['question']))
    print('org trim: {}'.format(' '.join(go)))
    print('new trim: {}'.format(' '.join(hy)))
    print('')
    if catalog:
        counts['all'] += 1
        counts[sample['hardness']] += 1
        #sample['bleu'] = bleu4
        sample['similarity'] = simil
        new_samples.append(sample)
    # time.sleep(1)

print(counts)

with open(args.dst_json, 'w') as f:
   print(json.dumps(new_samples, indent=4), file=f)
