import nltk

with open('sents.txt', 'r') as f:
    sample = f.read()

sentences = nltk.sent_tokenize(sample)
tokenized = [nltk.word_tokenize(s) for s in sentences]
tagged = [nltk.pos_tag(s) for s in tokenized]
chunked = nltk.ne_chunk_sents(tagged, binary=True)


def extract_ne(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_ne(child))

    return entity_names


entity_names = []
for tree in chunked:
    entity_names.extend(extract_ne(tree))

print(set(entity_names))
