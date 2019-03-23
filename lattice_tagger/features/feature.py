class WordsEncoder:
    def __init__(self, feature_dic=None):
        self.feature_dic = feature_dic
        raise NotImplemented('Inherit WordsEncoder and implement encode function')

    def is_trained(self):
        return self.feature_dic is not None

    def encode(self, words, *args):
        raise NotImplemented('Inherit WordsEncoder and implement encode function')

    def transform(self, words, *args):
        raise NotImplemented

    def _filter(self, feature_seq):
        if self.feature_dic is None:
            raise ValueError('Insert feature_dic first')
        filtered_seq = [[f for f in features if f in self.feature_dic] for features in feature_seq]
        return filtered_seq

class SimpleTrigramEncoder(WordsEncoder):
    """
    >>> sent = '너무너무너무는 아이오아이의 노래입니다'
    >>> text = '너무너무너무/Noun 는/Josa  아이오아이/Noun 의/Josa  노래/Noun 이/Adjective+ㅂ니다/Eomi'
    >>> words = text_to_words(text)
    >>> words_ = flatten_words(words)
    >>> chars, is_l = left_space_tag(sent)

    >>> encoder = SimpleTrigramEncoder()
    >>> encoder(words_)
    """

    def __init__(self, feature_dic=None):
        self.feature_dic = feature_dic

    def is_trained(self):
        return self.feature_dic is not None

    def encode(self, words, is_l=None):
        if self.feature_dic is None:
            raise ValueError('Insert feature_dic first')
        feature_seq = self.transform(words, is_l)
        idx_seq = [[self.feature_dic[f] for f in features] for features in feature_seq]
        return idx_seq

    def transform(self, words, is_l=None):
        feature_seq = trigram_encoder(words, is_l)
        if self.feature_dic is not None:
            feature_seq = self._filter(feature_seq)
        return feature_seq

def trigram_encoder(words, word_is_L=None):
    """
    trigram : (wi, ti), (wj, tj), (wk, tk)
    current positiion : k

    0 : (wj, wk, tk) # disambiguate wk with tk (이/Josa, 이/Adjective)
    1 : (wj, tk)
    2 : (tj, wk, tk)
    3 : (tj, tk)
    4 : (len(wk))
    5 : (wk morph, tk, wk is L-part of eojeol)
    6 : unknown length between (wj, wk)
    7 : (wi, wj, wk morph)
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
        (0, word_j.word, word_k.word, word_k.tag0),
        (1, word_j.word, word_k.tag0),
        (2, word_j.tag0, word_k.word, word_k.tag0),
        (3, word_j.tag0, word_k.tag0),
        (4, word_k.len)
    ]

    # unigram, word is L feature
    if word_is_L is not None:
        if word_k.b == word_k.e:
            is_l_tag = False
        else:
            is_l_tag = word_is_L[word_k.b]
        features.append((5, word_k.word, word_k.tag0, is_l_tag))

    # unknown length feature
    features.append((6, min(8, word_k.b - word_j.e)))

    # trigram feature
    if word_i is not None:
        features.append((7, word_i.word, word_j.word, word_k.word))

    return features
