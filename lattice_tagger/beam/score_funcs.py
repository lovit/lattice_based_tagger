from ..tagset import *


class BeamScoreFunction:
    def __call__(self, sequence, word_k):
        return self.score(sequence, word_k)

    def score(self, seq, word_k):
        raise NotImplemented('Inherit and implement score function')

class BeamScoreFunctions:
    def __init__(self, *functions):
        for func in functions:
            if not isinstance(func, BeamScoreFunction):
                raise ValueError('functions must be instance of BeamScoreFunction')
        self.funcs = [func for func in functions]

    def __call__(self, sequence, word_k):
        return self.score(sequence, word_k)

    def score(self, sequence, word_k):
        score = 0
        for func in self.funcs:
            score += func(sequence, word_k)
        return score

class RegularizationScore(BeamScoreFunction):
    def __init__(self, unknown_penalty=-0.1, known_preference=0.1):
        self.unknown_penalty = unknown_penalty
        self.known_preference = known_preference

    def score(self, seq, word_k):
        if word_k.tag0 == Unk:
            return self.unknown_penalty
        return self.known_preference * word_k.len

class MorphemePreferenceScore(BeamScoreFunction):
    def __init__(self, tag_to_morph=None):
        if tag_to_morph is None:
            tag_to_morph = {}
        self.tag_to_morph = tag_to_morph

    def score(self, seq, word_k):
        score = self.tag_to_morph.get(word_k.tag0, {}).get(word_k.morph0, 0)
        if word_k.tag1 is not None:
            score += self.tag_to_morph.get(word_k.tag1, {}).get(word_k.morph1, 0)
        return score

class WordPreferenceScore(BeamScoreFunction):
    def __init__(self, tag_to_word=None):
        if tag_to_word is None:
            tag_to_word = {}
        self.tag_to_word = tag_to_word

    def score(self, seq, word_k):
        return self.tag_to_word.get(word_k.tag0, {}).get(word_k.word, 0)

class FeatureScore(BeamScoreFunction):
    def __init__(self, coefficient, encoder):
        self.coefficient = coefficient
        self.encoder = encoder
        self.n_features = len(coefficient)

    def score(self, seq, word_k):
        if len(seq.sequences) == 1:
            word_i = None
        else:
            word_i = seq.sequences[-2]
        word_j = seq.sequences[-1]

        # TODO
        # featurize

        # cumulate feature coefficient
        score = 0

        return score
