from ..beam import beam_search
from ..beam import BeamScoreFunctions
from ..beam import RegularizationScore
from ..beam import SimpleTrigramFeatureScore
from ..dictionary import BaseMorphemeDictionary
from ..dictionary import sentence_lookup_as_begin_index
from ..dictionary import LRLookup, SubwordLookup, WordLookup


class Tagger:
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
        eojeol_lookup = SubwordLookup(dictionary, flatten=False)

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
