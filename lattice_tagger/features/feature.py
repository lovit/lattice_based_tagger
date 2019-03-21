class WordsEncoder:
    def __init__(self, feature_dic=None):
        self.feature_dic = feature_dic

    def __call__(self, words):
        return self.encode(words)

    def is_trained(self):
        return self.feature_dic is not None

    def encode(self, words):
        raise NotImplemented

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

    def encode(self, words):
        feature_seq = trigram_encoder(words)
        if self.feature_dic is not None:
            feature_seq = self._filter(feature_seq)
        return feature_seq


def trigram_encoder(words):
    raise NotImplemented
