from collections import namedtuple
from lattice_tagger.utils import Word
from lattice_tagger.tagset import *


def sentence_lookup(sent, eojeol_lookup):
    """
    Arguments
    ---------
    sent : str
        String type sentence
    eojeol_lookup : Lookup function

    Returns
    -------
    nodes : list of Word

    Usage
    ----
        >>> dictionary = DemoMorphemeDictionary()
        >>> eojeol_lookup = LRLookup(dictionary)

        >>> sent = '너무너무너무는 아이오아이의 노래입니다'
        >>> sentence_lookup(sent, eojeol_lookup)

        $ [Word(너무너무너무는, 너무너무너무/Noun + 는/Josa, len=7, b=0, e=7),
           Word(아이오아이의, 아이오아이/Noun + 의/Josa, len=6, b=7, e=13),
           Word(노래, 노래/Noun, len=2, b=13, e=15),
           Word(입니다, 이/Adjective + ㅂ니다/Eomi, len=3, b=15, e=18)]

        >>> eojeol_lookup = WordLookup(dictionary)
        >>> sentence_lookup(sent, eojeol_lookup)

        $ [Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6),
           Word(너무너무너무는, 너무너무너무/Noun + 는/Josa, len=7, b=0, e=7),
           Word(아이, 아이/Noun, len=2, b=7, e=9),
           Word(아이오, 아이오/Noun, len=3, b=7, e=10),
           Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12),
           Word(아이오아이의, 아이오아이/Noun + 의/Josa, len=6, b=7, e=13),
           Word(이, 이/Noun, len=1, b=8, e=9),
           Word(아이, 아이/Noun, len=2, b=10, e=12),
           Word(아이의, 아이/Noun + 의/Josa, len=3, b=10, e=13),
           Word(이, 이/Noun, len=1, b=11, e=12),
           Word(이의, 이/Noun + 의/Josa, len=2, b=11, e=13),
           Word(노래, 노래/Noun, len=2, b=13, e=15),
           Word(입니다, 이/Adjective + ㅂ니다/Eomi, len=4, b=15, e=18)]
    """

    offset = 0
    nodes = []
    for eojeol in sent.split():
        nodes += eojeol_lookup(eojeol, offset)
        offset += len(eojeol)
    return nodes


class EojeolLookup:
    def __call__(self, eojeol, offset=0):
        return self.lookup(eojeol, offset)

    def lookup(self, eojeol, offset):
        raise NotImplemented

class LRLookup(EojeolLookup):
    def __init__(self, dictionary, prefer_exact_match=True):
        self.dictionary = dictionary
        self.prefer_exact_match = prefer_exact_match

    def lookup(self, eojeol, offset=0):
        return lr_lookup(eojeol, self.dictionary, offset, self.prefer_exact_match)

class SubwordLookup(EojeolLookup):
    def __init__(self, dictionary, prefer_exact_match=True):
        self.dictionary = dictionary
        self.prefer_exact_match = prefer_exact_match

    def lookup(self, eojeol, offset=0):
        return subword_lookup(eojeol, self.dictionary, offset, self.prefer_exact_match)

class WordLookup(EojeolLookup):
    def __init__(self, dictionary, prefer_exact_match=True, standalones=None, max_len=-1):
        if not hasattr(dictionary, 'surface_to_lemma'):
            raise ValueError('dictionary must be MorphemeDictionary')

        if standalones is None:
            standalones = [Noun, Adverb, Exclamation, Determiner]

        self.dictionary = dictionary
        self.prefer_exact_match = prefer_exact_match
        self.standalones = standalones
        if max_len <= 0:
            self.max_len = self._find_max_len(dictionary, standalones)
        else:
            self.max_len = max_len

    def lookup(self, eojeol, offset=0):
        return word_lookup(eojeol, self.dictionary, offset,
            self.prefer_exact_match, self.standalones, self.max_len)

    def _find_max_len(self, dictionary, standalones):
        standalones_ = set(standalones)
        standalones_.add(Verb)
        standalones_.add(Adjective)
        max_len = 0
        for tag, morphs in dictionary.tag_to_morphs.items():
            if not tag in standalones_:
                continue
            max_len = max(max_len, max(len(morph) for morph in morphs))
        return max_len

def subword_lookup(eojeol, dictionary, offset=0, prefer_exact_match=True):
    """
    >>> from lattice_tagger.utils import DemoMorphemeDictionary
    >>> dictionary = DemoMorphemeDictionary()

    >>> subword_lookup('아이오아이', dictionary)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5)]

    >>> subword_lookup('아이오아이', dictionary)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=2, e=7)]

    >>> subword_lookup('아이오아이', dictionary, prefer_exact_match=False)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5),
       Word(아이, 아이/Noun, len=2, b=0, e=2),
       Word(아이오, 아이오/Noun, len=3, b=0, e=3),
       Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5),
       Word(이, 이/Adjective, len=1, b=1, e=2),
       Word(이, 이/Noun, len=1, b=1, e=2),
       Word(이, 이/Josa, len=1, b=1, e=2),
       Word(아이, 아이/Noun, len=2, b=3, e=5),
       Word(이, 이/Adjective, len=1, b=4, e=5),
       Word(이, 이/Noun, len=1, b=4, e=5),
       Word(이, 이/Josa, len=1, b=4, e=5)]
    """

    words = dictionary.lookup(eojeol, offset)
    if prefer_exact_match and words:
        return words

    n = len(eojeol)
    for b in range(n):
        for e in range(b+1, n+1):
            sub = eojeol[b:e]
            words += dictionary.lookup(sub, offset + b)
    return words

def lr_lookup(eojeol, dictionary, offset=0, prefer_exact_match=True):
    """
    >>> from lattice_tagger.utils import DemoMorphemeDictionary
    >>> dictionary = DemoMorphemeDictionary()

    >>> lr_lookup('아이오아이', dictionary)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5)]

    >>> lr_lookup('아이오아이', dictionary, offset=2)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=2, e=7)]

    >>> lr_lookup('아이오아이', dictionary, prefer_exact_match=False)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5),
       Word(아이오, 아이오/Noun, len=3, b=0, e=3),
       Word(아이, 아이/Noun, len=2, b=3, e=5)]

    >>> lr_lookup('아이오아이의', dictionary)
    $ [Word(아이오아이의, 아이오아이/Noun + 의/Josa, len=6, b=0, e=6)]
    """

    words = dictionary.lookup(eojeol, offset)
    if prefer_exact_match and words:
        return words

    n = len(eojeol)
    e = offset + n
    for i in range(1, n):
        # special case : Noun + Josa
        l, r = eojeol[:i], eojeol[i:]
        if dictionary.check(l, Noun) and dictionary.check(r, Josa):
            words.append(Word(eojeol, l, r, Noun, Josa, n, offset, e))
            continue
        lset = dictionary.lookup(eojeol[:i], offset)
        rset = dictionary.lookup(eojeol[i:], offset + i)
        if not lset or not rset:
            continue
        words += lset
        words += rset
    return words

def word_lookup(eojeol, dictionary, offset=0, prefer_exact_match=True, standalones=None, max_len=-1):
    """
    >>> word_lookup('아이오아이', dictionary)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5)]

    >>> word_lookup('노래를', dictionary)
    $ [Word(노래, 노래/Noun, len=2, b=0, e=2),
      Word(노래를, 노래/Noun + 를/Josa, len=3, b=0, e=3)]

    >>> word_lookup('우와!노래를했다', dictionary)
    $ [Word(우와, 우와/Exclamation, len=2, b=0, e=2),
       Word(노래, 노래/Noun, len=2, b=3, e=5),
       Word(노래를, 노래/Noun + 를/Josa, len=3, b=3, e=6),
       Word(했다, 하/Verb + 았다/Eomi, len=3, b=6, e=8)]
    """

    # Initialize
    n = len(eojeol)

    if standalones is None:
        # Noun + Josa, Adjective / Verb + Eomi
        standalones = [Noun, Adverb, Exclamation, Determiner]

    if max_len <= 0:
        max_len = n

    # eojeol exact match
    words = dictionary.lookup(eojeol, offset)
    if prefer_exact_match and words:
        return words

    # prepare conjugation points
    lemmatizing = [dictionary.surface_to_lemma.get(c, []) for c in eojeol]

    # check loop
    for b in range(n):
        for le in range(b+1, min(b+max_len, n)+1):
            l = eojeol[b:le]

            # check conjugation points
            if not lemmatizing[le-1]:
                l_ = None
            else:
                l_ = [(l[:-1] + l1, r0) for l1, r0 in lemmatizing[le-1]]

            # check standalone tags
            for ltag in standalones:
                if dictionary.check(l, ltag):
                    words.append(Word(l, l, None, ltag, None, le-b, offset + b, offset + le))

            # check L + R structure
            for re in range(le, n+1):
                r = eojeol[le:re]

                # when exists no conjugation
                if dictionary.check(l, Noun) and dictionary.check(r, Josa):
                    words.append(Word(l+r, l, r, Noun, Josa, re-b, offset + b, offset + re))
                if dictionary.check(l, Verb) and dictionary.check(r, Eomi):
                    words.append(Word(l+r, l, r, Verb, Eomi, re-b, offset + b, offset + re))
                if dictionary.check(l, Adjective) and dictionary.check(r, Eomi):
                    words.append(Word(l+r, l, r, Adjective, Eomi, re-b, offset + b, offset + re))

                if l_ is None:
                    continue

                # when exists conjugation
                for l_lemma, r0 in l_:
                    r_lemma = r0 + r
                    if dictionary.check(l_lemma, Verb) and dictionary.check(r_lemma, Eomi):
                        words.append(Word(l+r, l_lemma, r_lemma, Verb, Eomi, re-b+1, offset + b, offset + re))
                    if dictionary.check(l_lemma, Adjective) and dictionary.check(r_lemma, Eomi):
                        words.append(Word(l+r, l_lemma, r_lemma, Adjective, Eomi, re-b+1, offset + b, offset + re))

    return words

def sentence_lookup_as_graph(sent, eojeol_lookup):
    """
    Arguments
    ---------
    sent : str
        String type input sentence
    eojeol_lookup : lookup function

    Returns
    -------
    nodes : list of Node
    edges : list of [from node, to node, weight]

    Usage
    -----
        >>> eojeol_lookup = WordLookup(dictionary)
        >>> nodes, edges = sentence_lookup_as_graph('공연을했다', eojeol_lookup)

        >>> print(nodes)

        $ ['BOS',
           'EOS',
           Word(공연, 공연/Noun, len=2, b=0, e=2),
           Word(공연을, 공연/Noun + 을/Josa, len=3, b=0, e=3),
           Word(했다, 하/Verb + 았다/Eomi, len=3, b=3, e=5)]


        >>> for from_, to_, weight in edges:
        >>>     print('{} -> {} : {}'.format(from_, to_, weight))

        $ BOS -> Word(공연, 공연/Noun, len=2, b=0, e=2) : 0
          BOS -> Word(공연을, 공연/Noun + 을/Josa, len=3, b=0, e=3) : 0
          Word(공연, 공연/Noun, len=2, b=0, e=2) -> Word(했다, 하/Verb + 았다/Eomi, len=3, b=3, e=5) : 0
          Word(공연을, 공연/Noun + 을/Josa, len=3, b=0, e=3) -> Word(했다, 하/Verb + 았다/Eomi, len=3, b=3, e=5) : 0
          Word(했다, 하/Verb + 았다/Eomi, len=3, b=3, e=5) -> EOS : 0
    """

    def closest(begin, last, bindex):
        for i in range(begin, last):
            if bindex[i]:
                return i
        return -1

    n = len(sent.replace(' ',''))
    words = sentence_lookup(sent, eojeol_lookup)

    # if there exist no word in dictionary
    if not words:
        return [], []

    bindex = [[] for _ in range(n)]
    for word in words:
        bindex[word.b].append(word)

    edges = [[BOS, word, 0] for word in bindex[closest(0, n, bindex)]]
    for words_in_b in bindex:
        for from_word in words_in_b:
            adj_b = closest(from_word.e, n, bindex)
            if adj_b == -1:
                edges.append([from_word, EOS, 0])
            else:
                for to_word in bindex[adj_b]:
                    edges.append([from_word, to_word, 0])

    nodes = [BOS, EOS] + words

    return nodes, edges