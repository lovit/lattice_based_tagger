class SentMorphemePairs:
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
            char_str = ' '.join(eojeols)
            morph_str = ' '.join(morphs)
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
                eojeols.append(columns[0])
                if len(columns) > self.col:
                    morphs.append(columns[self.col])

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

class FeatureDecoratedPairs:
    def __init__(self, sent_morph_pairs, encoder, checkpoints=-1,
        only_features=False, verbose=False):
        self.pairs = sent_morph_pairs
        self.encoder = encoder
        self.checkpoints = checkpoints
        self.only_features = only_features
        self.verbose = verbose

    def __iter__(self):
        for i, (sent, morph_text) in enumerate(self.pairs):
            if self.checkpoints > 0 and i % checkpoints:
                print('\rprocessing {} sents ... '.format(i), end='')
            try:
                words = text_to_words(sent, morph_text)
                words_ = flatten_words(words)
                chars, is_l = left_space_tag(sent)
                feature_seq = self.encoder(words_, is_l)
                if self.only_features:
                    yield feature_seq
                else:
                    yield sent.split(), words, feature_seq
            except Exception as e:
                if self.verbose:
                    print(e)
                    print('sentence idx = {}'.format(i))
                    print('sent : {}'.format(sent))
                    print('morphs : {}'.format(morph_text), end='\n\n')
                continue
