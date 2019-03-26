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
    def __init__(self, unknown_penalty=-0.1, known_preference=0.1, syllable_penalty=-0.2):
        self.unknown_penalty = unknown_penalty
        self.known_preference = known_preference
        self.syllable_penalty = syllable_penalty

    def evaluate(self, seq):
        return sum(self.score(None, word) for word in seq.sequences)

    def score(self, seq, word_k):
        value = 0
        if word_k.tag0 == Unk:
            value += self.unknown_penalty
        else:
            value += (self.known_preference * word_k.len)
        if word_k.len == 1 and word_k.tag0 == Noun:
            value += self.syllable_penalty
        return value

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
    def __init__(self, encoder=None, coefficients=None):
        self.set_encoder(encoder, coefficients)

    def set_encoder(self, encoder, coefficients=None):
        if encoder is None:
            self.num_features = 0
            self.coefficients = None
            self.encoder = encoder
            return self

        if not encoder.is_trained():
            raise ValueError('Encoder must be trained first')
        self.num_features = len(encoder.feature_dic)

        if coefficients is None:
            coefficients = [0] * self.num_features

        if len(coefficients) != self.num_features:
            raise ValueError('Encoder and coefficients have different size features')

        self.coefficients = coefficients
        self.encoder = encoder
        return self

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
