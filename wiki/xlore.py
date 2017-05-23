# coding=utf-8
import re

RE_XLORE = re.compile('(.+)\[(.+)\]', re.U)

s = '罗夫尚·巴伊拉莫夫[Rovshan Bayramov]foo'
print(RE_XLORE.findall(s))

s = '牛郎织女'
print(RE_XLORE.findall(s))


def check_file(fname):
    with open(fname) as f:
        for line in f:
            line = line.strip()
            found = RE_XLORE.findall(line)
            if found:
                assert len(found) == 1
                zh, en = found[0]
                print(en, zh)


