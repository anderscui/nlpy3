# coding=utf-8
import json


def dump_to_json(obj, fname):
    json.dump(obj, open(fname, 'w'), ensure_ascii=False)


def load_json(fname):
    return json.load(open(fname))
