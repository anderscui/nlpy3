# coding=utf-8
import json

import MySQLdb
import pandas as pd
from collections import defaultdict


def bytes_to_str(bs):
    return str(bs, 'utf-8')


def extract_title(title):
    if ':' in title:
        return title.split(':')[1].strip()
    else:
        return title


db = MySQLdb.connect(host='localhost', user='root', passwd='nadileaf', db='wikidata')
df = pd.read_sql_query("select * from langlinks where ll_lang like 'zh%'", db)


langs = defaultdict(dict)
for i, row in df.iterrows():
    from_id = int(row['ll_from'])
    lang = bytes_to_str(row['ll_lang'])
    title = bytes_to_str(row['ll_title'])
    langs[from_id][lang] = title

zh_lans = ['zh-cn', 'zh', 'zh-tw']

langs_zh = {}
for i in langs:
    zhlans = langs[i]
    for lan in zh_lans:
        if lan in zhlans:
            langs_zh[i] = extract_title(zhlans[lan])
            break

json.dump(langs, open('en_langs.json', 'w'), ensure_ascii=False)
json.dump(langs_zh, open('en_langs_zh.json', 'w'), ensure_ascii=False)
