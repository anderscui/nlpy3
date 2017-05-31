# coding=utf-8
import glob

from utils import dump_to_json, load_json, extract_cat_title, clean_title, strip_tags


items = load_json('items_trans.json')
pitems = items['0']
citems = items['14']
print(len(pitems), len(citems))  # (13175649, 1591041) 14766690

expanded = load_json('items_expanded.json')
print(len(expanded))  # 14766698

i = 0
for k in pitems:
    i += len(pitems[k].get('inst_of', []))
for k in citems:
    i += len(citems[k].get('subcls_of', []))
# 28404178

j = 0
for k in expanded:
    j += len(expanded[k].get('cats', []))
# j: 31579087


from html.entities import name2codepoint
import re


RE_WS = re.compile('\s+', re.U)


def unescape(text):
    """
    Removes HTML or XML character references and entities from a text string.

    :param text The HTML (or XML) source text.
    :return The plain text, as a Unicode string, if necessary.
    """

    def fixup(m):
        text = m.group(0)
        code = m.group(1)
        try:
            if text[1] == "#":  # character reference
                if text[2] == "x":
                    return chr(int(code[1:], 16))
                else:
                    return chr(int(code))
            else:  # named entity
                return chr(name2codepoint[code])
        except:
            return text  # leave as is

    return re.sub("&#?(\w+);", fixup, text)


def split_word(s):
    if not s:
        return [s]

    res = []
    if s[0].islower():
        last = 0
        for i, c in enumerate(s):
            if c.isupper():
                res.append(s[last:i])
                last = i
        if last < len(s) - 1:
            res.append(s[last:])

        return [r for r in res if r]

    return [s]


def process_cat_title(title, ctitles):
    if title in ctitles:
        return title

    title = title.replace('_', ' ')
    if title in ctitles:
        return title

    title = RE_WS.sub(' ', title)
    if title in ctitles:
        return title

    title = unescape(title)
    if title in ctitles:
        return title

    title = strip_tags(title)
    if title in ctitles:
        return title

    if title.capitalize() in ctitles:
        return title.capitalize()

    if len(title) > 0:
        temp = title[0].upper() + title[1:]
        if temp in ctitles:
            return temp

    parts = title.split()
    title2 = ' '.join(sum([split_word(p) for p in parts if p], []))
    if title2 in ctitles:
        return title2

    return title


ctitles = {}
for pid in pitems:
    item = pitems[pid]
    inst_of = item.get('inst_of', [])
    if pid in expanded:
        new_item = expanded[pid]
        cats = new_item.get('cats', [])
        new_cats = set(inst_of + cats)
        res = []
        for c in new_cats:
            c = process_cat_title(c, ctitles)
            if c in ctitles:
                res.append(c)

        if res:
            item['inst_of'] = res
        elif 'inst_of' in item:
            del item['inst_of']
    else:
        print(pid)


for cid in citems:
    item = citems[cid]
    subcls_of = item.get('subcls_of', [])
    if cid in expanded:
        new_item = expanded[cid]
        cats = new_item.get('cats', [])
        new_cats = set(subcls_of + cats)
        res = []
        for c in new_cats:
            c = process_cat_title(c, ctitles)
            if c in ctitles:
                res.append(c)

        if res:
            item['subcls_of'] = res
        elif 'subcls_of' in item:
            del item['subcls_of']
    else:
        print(cid)
