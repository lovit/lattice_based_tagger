from .dictionary import text_to_words
from .dictionary import flatten_words
from .utils import left_space_tag
from .utils import get_process_memory


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
