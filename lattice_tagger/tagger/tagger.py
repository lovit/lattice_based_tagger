from ..beam import beam_search
from ..beam import BeamScoreFunctions
from ..beam import RegularizationScore
from ..beam import SimpleTrigramFeatureScore
from ..dictionary import BaseMorphemeDictionary
from ..dictionary import sentence_lookup_as_begin_index
from ..dictionary import LRLookup, WordLookup, MorphemeLookup


class Tagger:
    """
        >>> dictionary = DemoMorphemeDictionary()
        >>> encoder = SimpleTrigramEncoder(feature_to_idx)
        >>> funcs = BeamScoreFunctions(
        >>>     RegularizationScore(unknown_penalty=-.1, known_preference=0.5),
        >>>     MorphemePreferenceScore({Noun: {'아이오아이':2.2}}),
        >>>     WordPreferenceScore({Adjective: {'입니다':3.3}}),
        >>>     SimpleTrigramFeatureScore(coefficients, encoder)
        >>> )

        >>> tagger = Tagger(
        >>>     DemoMorphemeDictionary(),
        >>>     encoder=encoder,
        >>>     score_funcs=funcs
        >>> )

        >>> sent = '너무너무너무는 아이오아이의 노래 입니다'
        >>> tagger.tag(sent)


        $ Sequences(
            words : [
              Word(BOS, BOS/BOS, len=0, b=0, e=0)
              Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6, L)
              Word(는, 는/Josa, len=1, b=6, e=7)
              Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12, L)
              Word(의, 의/Josa, len=1, b=12, e=13)
              Word(노래, 노래/Noun, len=2, b=13, e=15, L)
              Word(입니다, 이/Adjective + ㅂ니다/Eomi, len=3, b=15, e=18, L)
              Word(EOS, EOS/EOS, len=0, b=18, e=18)
            ]
            score : 13.396394844836715
            num unks in tails : 0
          )
    """

    def __init__(self, dictionary='base', lookup='subword_lookup',
        encoder=None, score_funcs=None):

        # set dictionary
        # TODO
        if isinstance(dictionary, str):
            dictionary = BaseMorphemeDictionary()

        self.dictionary = dictionary

        # set lookup function
        # if isinstance(lookup, str):
        # TODO
        eojeol_lookup = MorphemeLookup(dictionary, flatten=False)

        self.eojeol_lookup = eojeol_lookup

        # set score functions
        # TODO
        self.score_funcs = score_funcs

    def tag(self, sent, beam_size=3, ensure_normalize=True, debug=False):
        if not ensure_normalize:
            # TODO normalize
            sent = sent

        chars = sent.replace(' ', '')
        words, bindex = sentence_lookup_as_begin_index(sent, self.eojeol_lookup)
        matures = beam_search(bindex, chars, self.score_funcs,
            beam_size=beam_size, debug=debug)

        return matures[0]
