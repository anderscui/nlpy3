import jieba
import jieba.posseg as pseg

sent = '张超涛来自中国上海市复旦大学数学系.她来自青岛某大学.'
tokens = ' '.join(jieba.cut(sent))
print(tokens)


sent = "Machine-learning工程师"
for w, t in pseg.cut(sent):
    print(w, t)
