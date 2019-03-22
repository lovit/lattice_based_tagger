class WordsEncoder:
    def __init__(self, feature_dic=None):
        self.feature_dic = feature_dic
        raise NotImplemented('Inherit WordsEncoder and implement encode function')

    def __call__(self, words):
        return self.encode(words)

    def is_trained(self):
        return self.feature_dic is not None

    def encode(self, words):
        raise NotImplemented('Inherit WordsEncoder and implement encode function')

    def _filter(self, feature_seq):
        if self.feature_dic is None:
            raise ValueError('Insert feature_dic first')
        filtered_seq = [[f for f in features if f in self.feature_dic] for features in feature_seq]
        return filtered_seq

class SimpleTrigramEncoder(WordsEncoder):
    def __init__(self, feature_dic=None):
        self.feature_dic = feature_dic

    def is_trained(self):
        return self.feature_dic is not None

    def encode(self, words, is_l=None):
        feature_seq = trigram_encoder(words, is_l)
        if self.feature_dic is not None:
            feature_seq = self._filter(feature_seq)
        return feature_seq


def trigram_encoder(words, word_is_L=None):
    """
    trigram : (wi, ti), (wj, tj), (wk, tk)
    current positiion : k

    0 : (wj, wk morph, tk) # disambiguate wk with tk (이/Josa, 이/Adjective)
    1 : (wj, tk)
    2 : (tj, wk morph, tk)
    3 : (tj, tk)
    4 : (len(wk))
    5 : (wk morph, tk, wk is L-part of eojeol)
    6 : (wi, wj, wk morph)
    """
    n = len(words) - 2 # include BOS, EOS
    words_ = [None] + words

    feature_seq = []
    for word_i, word_j, word_k in zip(words_, words, words[1:-1]):
        feature_seq.append(trigram_encoder_(word_i, word_j, word_k, word_is_L))
    return feature_seq

def trigram_encoder_(word_i, word_j, word_k, word_is_L=None):
    # bigram feature
    features = [
        (0, word_j.morph0, word_k.morph0, word_k.tag0),
        (1, word_j.morph0, word_k.tag0),
        (2, word_j.tag0, word_k.morph0, word_k.tag0),
        (3, word_j.tag0, word_k.tag0),
        (4, word_k.len)
    ]

    # unigram, word is L feature
    if word_is_L is not None:
        features.append((5, word_k.morph0, word_k.tag0, word_is_L[word_k.b]))

    # trigram feature
    if word_i is not None:
        features.append((6, word_i.morph0, word_j.morph0, word_k.morph0))

    return features
