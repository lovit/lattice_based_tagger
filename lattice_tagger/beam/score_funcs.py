from ..tagset import *
from .beam import Sequence


class BeamScoreFunction:
    def __call__(self, sequence, word_k):
        return self.score(sequence, word_k)

    def evaluate(self, seq):
        raise NotImplemented('Inherit and implement evaluate function')

    def score(self, seq, word_k):
        raise NotImplemented('Inherit and implement score function')


class BeamScoreFunctions:
    """
    Cumulate BeamScoreFunction instances

        >>> funcs = BeamScoreFunctions(
        >>>     RegularizationScore(unknown_penalty=-.1, known_preference=0.5),
        >>>     MorphemePreferenceScore({Noun: {'아이오아이':2.2}}),
        >>>     WordPreferenceScore({Adjective: {'입니다':3.3}}),
        >>>     SimpleTrigramFeatureScore(coefficients, encoder)
        >>> )

        >>> sent = '너무너무너무는 아이오아이의 노래 입니다'
        >>> chars = sent.replace(' ', '')
        >>> words, bindex = sentence_lookup_as_begin_index(sent, eojeol_lookup)
        >>> matures = beam_search(bindex, chars, funcs, beam_size=3, debug=False)
    """

    def __init__(self, *functions):
        for func in functions:
            if not isinstance(func, BeamScoreFunction):
                raise ValueError('functions must be instance of BeamScoreFunction')
        self.funcs = [func for func in functions]

    def __call__(self, sequence, word_k):
        return self.score(sequence, word_k)

    def evaluate(self, seq):
        score = 0
        for func in self.funcs:
            score += func.evaluate(seq)
        return score

    def score(self, sequence, word_k):
        score = 0
        for func in self.funcs:
            score += func(sequence, word_k)
        return score

class RegularizationScore(BeamScoreFunction):
    def __init__(self, unknown_penalty=-0.1, known_preference=0.1):
        self.unknown_penalty = unknown_penalty
        self.known_preference = known_preference

    def evaluate(self, seq):
        return sum(self.score(None, word) for word in seq.sequences)

    def score(self, seq, word_k):
        if word_k.tag0 == Unk:
            return self.unknown_penalty
        return self.known_preference * word_k.len

class MorphemePreferenceScore(BeamScoreFunction):
    def __init__(self, tag_to_morph=None):
        if tag_to_morph is None:
            tag_to_morph = {}
        self.tag_to_morph = tag_to_morph

    def evaluate(self, seq):
        return sum(self.score(None, word) for word in seq.sequences)

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

    def evaluate(self, seq):
        return sum(self.score(None, word) for word in seq.sequences)

    def score(self, seq, word_k):
        return self.tag_to_word.get(word_k.tag0, {}).get(word_k.word, 0)

class SimpleTrigramFeatureScore(BeamScoreFunction):
    def __init__(self, coefficients, encoder):

        if not encoder.is_trained():
            raise ValueError('Encoder must be trained first')

        num_features = len(coefficients)
        if len(encoder.feature_dic) != num_features:
            raise ValueError('Encoder and coefficients have different size features')

        self.coefficients = coefficients
        self.encoder = encoder
        self.num_features = num_features

    def evaluate(self, seq):
        score = 0
        seq_tmp = Sequence([seq.sequences[0]], 0)
        for word in seq.sequences:
            if word.tag0 == BOS or word.tag0 == EOS:
                continue
            increment = self.score(seq_tmp, word)
            seq_tmp = seq_tmp.add(word, increment)
        return seq_tmp.score

    def score(self, seq, word_k):
        word_i = None if len(seq.sequences) == 1 else seq.sequences[-2]
        word_j = seq.sequences[-1]
        feature_idxs = self.encoder.encode_word(word_i, word_j, word_k)
        score = 0
        for idx in feature_idxs:
            score += self.coefficients[idx]
        return score
