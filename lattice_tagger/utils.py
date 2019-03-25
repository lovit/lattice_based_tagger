from collections import defaultdict
import json
import os
import psutil


installpath = os.path.dirname(os.path.realpath(__file__))


## Operation for syllable transformation rules
def rules_to_strf(rules):
    return ['%s %s %s' % (key, l, r) for key, values in rules.items() for l, r in values]

def load_rules(path):
    rules = defaultdict(lambda: set())
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            columns = line.strip().split()
            if len(columns) != 3:
                print('Exception (%d line) : %s' % (i, line))
                continue
            surface, l, r = columns
            rules[surface].add((l, r))
    rules = {surface:tuple(canons) for surface, canons in rules.items()}
    return rules

def write_rules(rules, path):
    with open(path, 'w', encoding='utf-8') as f:
        for surface, canons in rules.items():
            for l, r in canons:
                f.write('%s %s %s\n' % (surface, l, r))

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

def get_process_memory():
    """It returns the memory usage of current process"""

    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 ** 3)


class WordMorphemePairs:
    """
        >>> train_data = SentMorphemePairs('../data/train.txt')
        >>> for sent, morphs in train_data:
                # do something
    """

    def __init__(self, filepath, morph_column=1, sep='\t', num_sents=-1):
        self.path = filepath
        self.sep = sep
        self.col = morph_column
        self.num_sents = num_sents
        self.len = 0

    def __iter__(self):
        def wrapup(eojeols, morphs):
            if not eojeols:
                return '', '', [], []
            char_str = '  '.join(eojeols)
            morph_str = '  '.join(morphs)
            return char_str, morph_str, [], []

        n_sents = 0
        eojeols = []
        morphs = []

        with open(self.path, encoding='utf-8') as f:
            for i, line in enumerate(f):
                # check max num of sents
                if self.num_sents > 0 and n_sents >= self.num_sents:
                    break

                # yield char & morph sequence
                if not line.strip():
                    char_str, morph_str, eojeols, morphs = wrapup(eojeols, morphs)
                    if char_str:
                        yield char_str, morph_str
                    n_sents += 1
                    continue

                # cumulate eojeol & morphs to buffer
                columns = line[:-1].split(self.sep)
                if len(columns) <= self.col:
                    continue

                eojeol = columns[0]
                morph = columns[self.col]
                if eojeol.strip() and len(morph.strip()) >= 3:
                    eojeols.append(eojeol)
                    morphs.append(morph)

            if eojeols:
                yield wrapup(eojeols, morphs)[:2]
        self.len = n_sents

    def __len__(self):
        if self.len > 0:
            return self.len
        with open(self.path, encoding='utf-8') as f:
            for i, line in enumerate(f):
                if self.num_sents > 0 and self.len > self.num_sents:
                    break
                if line.strip():
                    continue
                self.len += 1
        return self.len
