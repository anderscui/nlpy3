# coding=utf-8
import json
from collections import defaultdict, Counter

import jieba
from toolz import take

com_file = 'company.txt'

c = Counter()
with open('company.txt') as f:
    for line in f:
        c.update(jieba.cut(line))
