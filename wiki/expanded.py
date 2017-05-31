# coding=utf-8
import glob
import re
from utils import dump_to_json, load_json, extract_cat_title, clean_title

RE_DOC_TITLE = re.compile('<doc id="(\d+)" .+ title="(.+?)">', re.U)
RE_CAT = re.compile(r'\[\[(Category|分類|分类):((.|\n)+?)\]\]', re.U | re.M)
DISAMS = {'__DISAMBIG__'}


def extract_categories():
    print(RE_CAT.findall("""[[Category:Redirects from  non-English
     -language terms]][[Category:Redirects to undetermined-language terms]]"""))
    print(RE_CAT.findall("""[[Category:American films]]"""))


def extract_title_id(doc_line):
    matches = RE_DOC_TITLE.findall(doc_line)
    if len(matches) != 1:
        print(doc_line)
    assert len(matches) == 1
    return matches[0]


def main():
    docs = {}
    batch = 1
    for fname in glob.glob('text/*/wiki*', recursive=True):
        print(fname)
        with open(fname) as f:
            in_doc = False
            cur_doc = {}
            cur_lines = []
            for line in f:
                if not in_doc:
                    if line.startswith('<doc id="'):
                        in_doc = True
                        doc_id, title = extract_title_id(line)
                        cur_doc['id'] = doc_id
                        cur_doc['title'] = clean_title(title)
                    continue

                if line.startswith('</doc>'):
                    doc_id = cur_doc['id']
                    del cur_doc['id']

                    text = ''.join(cur_lines)
                    cats = RE_CAT.findall(text)
                    cats = [c.split('|')[0].strip() for _, c, _ in cats]
                    if cats:
                        cur_doc['cats'] = cats
                    is_disam = any(disam in text for disam in DISAMS)
                    if is_disam:
                        cur_doc['dis'] = 1

                    docs[doc_id] = cur_doc

                    in_doc = False
                    cur_doc = {}
                    cur_lines = []

                else:
                    cur_lines.append(line)

        if len(docs) >= 100000:
            dump_to_json(docs, 'enwiki/expanded_{}.json'.format(batch))
            docs = {}
            batch += 1

    if docs:
        dump_to_json(docs, 'enwiki/expanded_{}.json'.format(batch))
        docs = {}


if __name__ == '__main__':
    main()
    # 14766698

    docs = {}
    for fname in glob.glob('expanded_*.json', recursive=True):
        print(fname)
        docs.update(load_json(fname))
    print(len(docs))
    # extract_categories()
