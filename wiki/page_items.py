# coding=utf-8
import json
from collections import defaultdict


def dump_to_json(obj, fname):
    json.dump(obj, open(fname, 'w'), ensure_ascii=False)

items = json.load(open('items.json'))
ptitles = items['0']
ctitles = items['14']

ptit_cleaned = {}
ptit_syn = {}
ptit_disam = {}
for pid in ptitles:
    item = ptitles[pid]
    if 'redirect_to' in item:
        ptit_syn[pid] = item
    elif 'is_disam' in item:
        ptit_disam[pid] = item
    else:
        ptit_cleaned[pid] = item

dump_to_json(ptit_cleaned, 'pages_cleaned.json')
dump_to_json(ptit_syn, 'pages_syn.json')
dump_to_json(ptit_disam, 'pages_disam.json')


# disam: 49797
# syn: 7778368
# main: 5347484
