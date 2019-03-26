from ..tagset import *


class WordsEncoder:
    def __init__(self, feature_dic=None):
        self.feature_dic = feature_dic
        raise NotImplemented('Inherit WordsEncoder and implement encode function')

    def is_trained(self):
        return self.feature_dic is not None

    def set_feature_dic(self, feature_dic):
        self.feature_dic = feature_dic
        return self

    def encode_sequence(self, words, *args):
        raise NotImplemented('Inherit WordsEncoder and implement encode_sequence function')

    def encode_word(self, *args):
        raise NotImplemented('Inherit WordsEncoder and implement encode_word function')

    def transform_sequence(self, words, *args):
        raise NotImplemented('Inherit WordsEncoder and implement transform_sequence function')

    def transform_word(self, *args):
        raise NotImplemented('Inherit WordsEncoder and implement transform_word function')

    def _filter(self, features):
        return [f for f in features if f in self.feature_dic]

class SimpleTrigramEncoder(WordsEncoder):
    """
    >>> sent = '너무너무너무는 아이오아이의 노래입니다'
    >>> text = '너무너무너무/Noun 는/Josa  아이오아이/Noun 의/Josa  노래/Noun 이/Adjective+ㅂ니다/Eomi'
    >>> words = text_to_words(text)
    >>> words_ = flatten_words(words)

    >>> encoder = SimpleTrigramEncoder()
    >>> encoder.encode_sequence(words_)
    >>> encoder.transform_sequence(words_)

    >>> encoder.encode_word(word_i, word_j, word_k)
    >>> encoder.transform_word(word_i, word_j, word_k)

    """

    def __init__(self, feature_dic=None):
        self.feature_dic = feature_dic

    def encode_sequence(self, words):
        if not self.is_trained():
            raise ValueError('Insert feature_dic first')
        feature_seq = self.transform_sequence(words)
        idx_seq = [[self.feature_dic[f] for f in features] for features in feature_seq]
        return idx_seq

    def encode_word(self, word_i, word_j, word_k):
        features = self.transform_word(word_i, word_j, word_k)
        idxs = [self.feature_dic[f] for f in features]
        return idxs

    def transform_sequence(self, words):
        n = len(words) - 2 # include BOS, EOS
        words_ = [None] + words
        feature_seq = []
        for word_i, word_j, word_k in zip(words_, words, words[1:-1]):
            feature_seq.append(self.transform_word(word_i, word_j, word_k))
        return feature_seq

    def transform_word(self, word_i, word_j, word_k):
        features = trigram_encoder(word_i, word_j, word_k)
        if self.is_trained():
            features = self._filter(features)
        return features

def trigram_encoder(word_i, word_j, word_k):
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
    7 : (wi, wj, wk)
    8 : (wi or wj, wk) if all ti, tj, tk in {Noun, Adjective, Adverb, Verb} # contextual feature
    """

    contextual_tags = {Noun, Adverb, Adjective, Verb}

    # bigram feature
    features = [
        (0, word_j.word, word_k.word, word_k.tag0),
        (1, word_j.word, word_k.tag0),
        (2, word_j.tag0, word_k.word, word_k.tag0),
        (3, word_j.tag0, word_k.tag0),
        (4, word_k.len)
    ]

    # unigram, word is L feature
    features.append((5, word_k.word, word_k.tag0, word_k.is_l))

    # unknown length feature
    if word_j.tag0 == Unk:
        features.append((6, min(8, word_j.len)))

    # trigram feature
    if word_i is not None:
        features.append((7, word_i.word, word_j.word, word_k.word))

    # contextual feature
    if word_k.tag0 in contextual_tags:
        if word_j.tag0 in contextual_tags:
            features.append((8, word_j.morph0, word_k.morph0))
        elif (word_i is not None) and (word_i.tag0 in contextual_tags):
            features.append((8, word_i.morph0, word_k.morph0))

    return features
