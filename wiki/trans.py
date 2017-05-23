# coding=utf-8

ptitles = {}
ctitles = {}
langs = {}
xlore = {}
zh_lans = ['zh-cn', 'zh', 'zh-tw']


def trans_to_zh(titles, langs, title):
    pid = titles.get(title, '')
    if not pid:
        return ''
    zhs = langs.get(pid, {})
    for lan in zh_lans:
        if lan in zhs:
            return zhs[lan]
    return ''


def transfer(title):
    if title in xlore:
        return xlore[title]
    ptitle = trans_to_zh(ptitles, langs, title)
    if ptitle:
        return ptitle
    else:
        return trans_to_zh(ctitles, langs, title)


pi = 0
for k in ptitles:
    trans = transfer(k)
    if trans:
        pi += 1

ci = 0
for k in ctitles:
    trans = transfer(k)
    if trans:
        ci += 1

# pi: 424315; ci: 102984

### wikidata languages; labels/entities;
en_lans = ['en', 'en-gb', 'en-ca']
zh_lans = ['zh-cn', 'zh-hans', 'zh', 'zh-hant', 'zh-tw', 'zh-hk', 'zh-sg', 'zh-mo']

labels = {}


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


def en_zh_labels():
    en_zh = {}
    for item_id in labels:
        item_labels = labels[item_id]['labels']
        enlabel = en_label(item_labels)
        zhlabel = zh_label(item_labels)
        if enlabel and zhlabel:
            if ':' not in enlabel or enlabel.startswith('Category:'):
                enlabel = extract_title(enlabel)
                zhlabel = extract_title(zhlabel)
            if enlabel[0].islower():
                enlabel = enlabel[0].upper() + enlabel[1:]
            en_zh[enlabel] = zhlabel
    return en_zh

en_zh = en_zh_labels()
# 912071
