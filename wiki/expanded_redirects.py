# coding=utf-8
import glob
import re
from utils import dump_to_json, load_json, extract_cat_title, clean_title

RE_DOC_TITLE = re.compile('<doc id="(\d+)" .+ title="(.+?)">', re.U)
RE_CAT = re.compile(r'\[\[(Category|分類|分类):((.|\n)+?)\]\]', re.U | re.M)
RE_REDIRECT = re.compile('#redirect\s*\[\[(.+?)]]', re.I | re.U)


def extract_title_id(doc_line):
    matches = RE_DOC_TITLE.findall(doc_line)
    if len(matches) != 1:
        print(doc_line)
    assert len(matches) == 1
    return matches[0]


def main(data_dir):
    redirects = {}
    batch = 1
    for fname in glob.glob(data_dir + '/*/wiki*', recursive=False):
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

                    for cur_line in cur_lines:
                        m = RE_REDIRECT.search(cur_line)
                        if m:
                            cur_doc['redirect'] = m.group(1)
                            break

                    if 'redirect' in cur_doc:
                        redirects[doc_id] = cur_doc

                    in_doc = False
                    cur_doc = {}
                    cur_lines = []

                else:
                    cur_lines.append(line)

        if len(redirects) >= 100000:
            dump_to_json(redirects, 'expanded/expanded_{}.json'.format(batch))
            redirects = {}
            batch += 1

    if redirects:
        dump_to_json(redirects, 'expanded/expanded_{}.json'.format(batch))
        redirects = {}


if __name__ == '__main__':
    main('en_items_raw')
    # 14766698

    # docs = {}
    # for fname in glob.glob('expanded_*.json', recursive=True):
    #     print(fname)
    #     docs.update(load_json(fname))
    # print(len(docs))
    # extract_categories()
