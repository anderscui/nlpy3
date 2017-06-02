# coding=utf-8


class MMatchTokenzier():
    """使用最大匹配分词"""
    def __init__(self, adict):
        self.words = {}
        prefix = set()
        for word, tag in adict.items():
            if word:
                self.words[word] = tag
                prefix.add(word[0])
        self.prefix = frozenset(prefix)

    def tokenize(self, text):
        segs = []

        N = len(text)
        k = 0
        rest = []
        while k < N:
            i = N
            found = 0
            if text[k] in self.prefix:
                while i > k:
                    word = text[k:i]
                    if word in self.words:
                        if rest:
                            segs.append(''.join(rest))
                            rest = []
                        segs.append(word)
                        found = 1
                        break
                    elif i == k + 1:
                        rest.append(text[k])
                        i -= 1
                    else:
                        i -= 1
            else:
                rest.append(text[k])

            if found:
                k = i
            else:
                k += 1
        if rest:
            segs.append(''.join(rest))
        return segs


if __name__ == '__main__':
    d = {'一个': 1,
         '自然语言': 1,
         '自然语言处理': 1,
         'java': 1,
         'javascript': 1,
         'scala': 1}

    t = MMatchTokenzier(d)
    print(t.tokenize('他是一个自然语言处理工程师，熟悉javascript'))
