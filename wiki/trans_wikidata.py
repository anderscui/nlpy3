# coding=utf-8
import json

en_lans = ['en', 'en-gb', 'en-ca']
zh_lans = ['zh-cn', 'zh-hans', 'zh', 'zh-hant', 'zh-tw', 'zh-hk', 'zh-sg', 'zh-mo']


def extract_title(title):
    if ':' in title:
        return title.split(':')[1].strip()
    else:
        return title


def en_label(item_labels):
    for lan in en_lans:
        if lan in item_labels:
            return item_labels[lan]
    return ''


def zh_label(item_labels):
    for lan in zh_lans:
        if lan in item_labels:
            return item_labels[lan]
    return ''


def en_zh_labels(labels):
    en_zh = {}
    for item_id in labels:
        item_labels = labels[item_id]['labels']
        enlabel = en_label(item_labels)
        zhlabel = zh_label(item_labels)
        if enlabel and zhlabel:
            if ':' not in enlabel or enlabel.startswith('Category:'):
                enlabel = extract_title(enlabel)
                zhlabel = extract_title(zhlabel)
            else:
                continue

            if enlabel[0].islower():
                enlabel = enlabel[0].upper() + enlabel[1:]
            en_zh[enlabel] = zhlabel
    return en_zh

all_labels = json.load(open('labels.json'))
en_zh = en_zh_labels(all_labels)
# 906234
