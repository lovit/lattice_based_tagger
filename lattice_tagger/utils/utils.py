import json
import os

installpath = os.path.sep.join(
    os.path.dirname(os.path.realpath(__file__)).split(os.path.sep)[:-1])


## Operation for syllable transformation rules
def rules_to_strf(rules):
    def concatenate(l, r):
        return '%s+%s' % (l,r)
    return {key:[concatenate(l,r) for l,r in values] for key, values in rules.items()}

def load_rules(path):
    def parse(lr_list):
        return tuple(tuple(lr.split('+')) for lr in lr_list)

    with open(path, encoding='utf-8') as f:
        rules = json.load(f)
    rules = {k:parse(v) for k,v in rules.items()}
    return rules

def write_rules(rules, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('{\n')
        n = len(rules)
        rules = list(rules.items())
        for key, values in rules[:-1]:
            f.write('  "{}": [{}],\n'.format(key, ','.join(['"%s"' % v for v in values])))
        f.write('  "{}": [{}]\n'.format(rules[-1][0], ','.join(['"%s"' % v for v in rules[-1][1]])))
        f.write('}\n')

def left_space_tag(sent):
    """
    >>> sent = '너무너무너무는 아이오아이의 노래입니다'
    >>> chars, tags = left_space_tag(sent)
    >>> chars = '너무너무너무는아이오아이의노래입니다'
    >>> tags = [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
    """
    chars = sent.replace(' ','')
    tags = [1] + [0]*(len(chars) - 1)
    idx = 0

    for c in sent:
        if c == ' ':
            tags[idx] = 1
        else:
            idx += 1
    return chars, tags

def flatten_words(words):
    """
    >>> text = '너무너무너무/Noun 는/Josa  아이오아이/Noun 의/Josa  노래/Noun 이/Adjective+ㅂ니다/Eomi'
    >>> words = text_to_words(text)
    $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
       Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6),
       Word(는, 는/Josa, len=1, b=6, e=7),
       Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12),
       Word(의, 의/Josa, len=1, b=12, e=13),
       Word(노래, 노래/Noun, len=2, b=13, e=15),
       Word(이+ㅂ니다, 이/Adjective + ㅂ니다/Eomi, len=4, b=15, e=18),
       Word(EOS, EOS/EOS, len=0, b=18, e=18)]

    >>> words_ = flatten_words(words)
    $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
       Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6),
       Word(는, 는/Josa, len=1, b=6, e=7),
       Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12),
       Word(의, 의/Josa, len=1, b=12, e=13),
       Word(노래, 노래/Noun, len=2, b=13, e=15),
       Word(이, 이/Adjective, len=1, b=15, e=16),
       Word(ㅂ니다, ㅂ니다/Eomi, len=2, b=16, e=18),
       Word(EOS, EOS/EOS, len=0, b=18, e=18)]
    """

    words_ = []
    for word in words:
        if word.tag1 is None:
            words_.append(word)
            continue
        len0 = len(word.morph0)
        len1 = len(word.morph1)
        b = word.b
        m = word.b + len0
        e = word.e
        if 'ㄱ' <= word.morph1[0] <= 'ㅎ':
            len1 -= 1
        word0 = Word(word.morph0, word.morph0, None, word.tag0, None, len0, b, m)
        word1 = Word(word.morph1, word.morph1, None, word.tag1, None, len1, m, e)
        words_.append(word0)
        words_.append(word1)
    return words_
