class AbstractFeatureTransformer:
    def __call__(self, words):
        return self.words_to_features(words)
    def words_to_features(self, words):
        raise NotImplemented