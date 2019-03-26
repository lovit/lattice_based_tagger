from collections import namedtuple
from lattice_tagger.dictionary import Word
from lattice_tagger.dictionary import flatten_words
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

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0)
           Word(너무너무너무는, 너무너무너무/Noun + 는/Josa, len=7, b=0, e=7, L),
           Word(아이오아이의, 아이오아이/Noun + 의/Josa, len=6, b=7, e=13, L),
           Word(노래, 노래/Noun, len=2, b=13, e=15, L),
           Word(입니다, 이/Adjective + ㅂ니다/Eomi, len=3, b=15, e=18),
           Word(EOS, EOS/EOS, len=0, b=18, e=18)]

        >>> eojeol_lookup = WordLookup(dictionary)
        >>> sentence_lookup(sent, eojeol_lookup)

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6, L),
           Word(는, 는/Josa, len=1, b=6, e=7),
           Word(아이, 아이/Noun, len=2, b=7, e=9, L),
           Word(아이오, 아이오/Noun, len=3, b=7, e=10, L),
           Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12, L),
           Word(이, 이/Noun, len=1, b=8, e=9),
           Word(아이, 아이/Noun, len=2, b=10, e=12),
           Word(이, 이/Noun, len=1, b=11, e=12),
           Word(의, 의/Josa, len=1, b=12, e=13),
           Word(노래, 노래/Noun, len=2, b=13, e=15, L),
           Word(입니다, 이/Adjective + ㅂ니다/Eomi, len=3, b=15, e=18),
           Word(EOS, EOS/EOS, len=0, b=18, e=18)]
    """

    n = len(sent.replace(' ', ''))
    BOS_word = Word(BOS, BOS, None, BOS, None, 0, 0, 0, False)
    EOS_word = Word(EOS, EOS, None, EOS, None, 0, n, n, False)

    offset = 0
    nodes = [BOS_word]
    for eojeol in sent.split():
        nodes += eojeol_lookup(eojeol, offset)
        offset += len(eojeol)
    nodes.append(EOS_word)
    return nodes


class EojeolLookup:
    def __init__(self, flatten=False):
        self.flatten = flatten

    def __call__(self, eojeol, offset=0):
        return self.lookup(eojeol, offset)

    def lookup(self, eojeol, offset):
        raise NotImplemented

class LRLookup(EojeolLookup):
    def __init__(self, dictionary, prefer_exact_match=True, flatten=False):
        self.dictionary = dictionary
        self.prefer_exact_match = prefer_exact_match
        self.flatten = flatten

    def lookup(self, eojeol, offset=0):
        words = lr_lookup(eojeol, self.dictionary, offset, self.prefer_exact_match)
        if self.flatten:
            words = flatten_words(words)
        return words

class WordLookup(EojeolLookup):
    def __init__(self, dictionary, prefer_exact_match=True, flatten=False):
        self.dictionary = dictionary
        self.prefer_exact_match = prefer_exact_match
        self.flatten = flatten

    def lookup(self, eojeol, offset=0):
        words = word_lookup(eojeol, self.dictionary, offset, self.prefer_exact_match)
        if self.flatten:
            words = flatten_words(words)
        return words

class MorphemeLookup(EojeolLookup):
    def __init__(self, dictionary, prefer_exact_match=True, standalones=None, max_len=-1, flatten=False):
        if not hasattr(dictionary, 'rules'):
            raise ValueError('dictionary must be MorphemeDictionary')

        if standalones is None:
            standalones = [Noun, Adverb, Exclamation, Determiner, Number]

        self.dictionary = dictionary
        self.prefer_exact_match = prefer_exact_match
        self.standalones = standalones
        if max_len <= 0:
            self.max_len = self._find_max_len(dictionary, standalones)
        else:
            self.max_len = max_len
        self.flatten = flatten

    def lookup(self, eojeol, offset=0):
        words = morpheme_lookup(eojeol, self.dictionary, offset,
            self.prefer_exact_match, self.standalones, self.max_len)
        if self.flatten:
            words = flatten_words(words)
        return words

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

def word_lookup(eojeol, dictionary, offset=0, prefer_exact_match=True):
    """
    >>> from lattice_tagger.utils import DemoMorphemeDictionary
    >>> dictionary = DemoMorphemeDictionary()

    >>> word_lookup('아이오아이', dictionary)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5, L)]

    >>> word_lookup('아이오아이', dictionary)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5, L)]

    >>> word_lookup('아이오아이', dictionary, prefer_exact_match=False)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5, L),
       Word(아이, 아이/Noun, len=2, b=0, e=2, L),
       Word(아이오, 아이오/Noun, len=3, b=0, e=3, L),
       Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5, L),
       Word(이, 이/Adjective, len=1, b=1, e=2),
       Word(이, 이/Noun, len=1, b=1, e=2),
       Word(이, 이/Josa, len=1, b=1, e=2),
       Word(아이, 아이/Noun, len=2, b=3, e=5),
       Word(이, 이/Adjective, len=1, b=4, e=5),
       Word(이, 이/Noun, len=1, b=4, e=5),
       Word(이, 이/Josa, len=1, b=4, e=5)]
    """

    words = dictionary.lookup(eojeol, offset, is_l=True)
    if prefer_exact_match and words:
        return words

    n = len(eojeol)
    for b in range(n):
        is_l = (b == 0)
        for e in range(b+1, n+1):
            sub = eojeol[b:e]
            words += dictionary.lookup(sub, offset + b, is_l)
    return words

def lr_lookup(eojeol, dictionary, offset=0, prefer_exact_match=True):
    """
    >>> from lattice_tagger.utils import DemoMorphemeDictionary
    >>> dictionary = DemoMorphemeDictionary()

    >>> lr_lookup('아이오아이', dictionary)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5, L)]

    >>> lr_lookup('아이오아이', dictionary, offset=2)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=2, e=7, L)]

    >>> lr_lookup('아이오아이', dictionary, prefer_exact_match=False)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5, L),
       Word(아이오, 아이오/Noun, len=3, b=0, e=3, L),
       Word(아이, 아이/Noun, len=2, b=3, e=5)]

    >>> lr_lookup('아이오아이의', dictionary)
    $ [Word(아이오아이의, 아이오아이/Noun + 의/Josa, len=6, b=0, e=6, L)]
    """

    words = dictionary.lookup(eojeol, offset, is_l=True)
    if prefer_exact_match and words:
        return words

    n = len(eojeol)
    e = offset + n
    for i in range(1, n):
        # special case : Noun + Josa
        l, r = eojeol[:i], eojeol[i:]
        if dictionary.check(l, Noun) and dictionary.check(r, Josa):
            words.append(Word(eojeol, l, r, Noun, Josa, n, offset, e, is_l=True))
            continue
        lset = dictionary.lookup(eojeol[:i], offset, is_l=True)
        rset = dictionary.lookup(eojeol[i:], offset + i, is_l=False)
        if not lset or not rset:
            continue
        words += lset
        words += rset
    return words

def morpheme_lookup(eojeol, dictionary, offset=0, prefer_exact_match=True, standalones=None, max_len=-1):
    """
    >>> word_lookup('아이오아이', dictionary)
    $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5, L)]

    >>> word_lookup('노래를', dictionary)
    $ [Word(노래, 노래/Noun, len=2, b=0, e=2, L),
       Word(를, 를/Josa, len=1, b=2, e=3)]]

    >>> word_lookup('우와!노래를했다', dictionary)
    $ [Word(우와, 우와/Exclamation, len=2, b=0, e=2, L),
       Word(노래, 노래/Noun, len=2, b=3, e=5),
       Word(를, 를/Josa, len=1, b=5, e=6),
       Word(했다, 하/Verb + 았다/Eomi, len=2, b=6, e=8)]
    """

    # Initialize
    n = len(eojeol)

    if standalones is None:
        # Noun + Josa, Adjective / Verb + Eomi
        standalones = [Noun, Adverb, Exclamation, Determiner, Number]

    if max_len <= 0:
        max_len = n

    # eojeol exact match
    words = dictionary.lookup(eojeol, offset, is_l=True)
    if prefer_exact_match and words:
        return words

    # prepare conjugation points
    noun_end = [0] * (n + 1)

    # check loop
    for b in range(n):
        is_l = (b == 0)
        for e in range(b+1, min(b+max_len, n) + 1):
            sub = eojeol[b:e]

            # Check stand-alone tags
            for tag in standalones:
                if dictionary.check(sub, tag):
                    words.append(Word(sub, sub, None, tag, None, e-b, offset + b, offset + e, is_l))
                    if tag == Noun:
                        noun_end[e] = 1

            # Check Noun + Josa
            if noun_end[b] > 0 and dictionary.check(sub, Josa):
                words.append(Word(sub, sub, None, Josa, None, e-b, offset + b, offset + e, is_l))

            # Check predicators
            for (m0, t0), (m1, t1) in dictionary.lemmatize(sub):
                words.append(Word(sub, m0, m1, t0, t1, e-b, offset + b, offset + e, is_l))

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
        >>> eojeol_lookup = MorphemeLookup(dictionary)
        >>> nodes, edges = sentence_lookup_as_graph('공연을했다', eojeol_lookup)

        >>> print(nodes)

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(EOS, EOS/EOS, len=0, b=5, e=5),
           Word(공연, 공연/Noun, len=2, b=0, e=2, L),
           Word(공연을, 공연/Noun + 을/Josa, len=3, b=0, e=3, L),
           Word(했다, 하/Verb + 았다/Eomi, len=3, b=3, e=5)]


        >>> for from_, to_, weight in edges:
        >>>     print('{} -> {} : {}'.format(from_, to_, weight))

        $ Word(BOS, BOS/BOS, len=0, b=0, e=0) -> Word(공연, 공연/Noun, len=2, b=0, e=2, L) : 0
          Word(BOS, BOS/BOS, len=0, b=0, e=0) -> Word(공연을, 공연/Noun + 을/Josa, len=3, b=0, e=3, L) : 0
          Word(공연, 공연/Noun, len=2, b=0, e=2, L) -> Word(했다, 하/Verb + 았다/Eomi, len=3, b=3, e=5) : 0
          Word(공연을, 공연/Noun + 을/Josa, len=3, b=0, e=3, L) -> Word(했다, 하/Verb + 았다/Eomi, len=3, b=3, e=5) : 0
          Word(했다, 하/Verb + 았다/Eomi, len=3, b=3, e=5) -> Word(EOS, EOS/EOS, len=0, b=5, e=5) : 0
    """

    def closest(begin, last, bindex):
        for i in range(begin, last):
            if bindex[i]:
                return i
        return -1

    n = len(sent.replace(' ',''))
    words, bindex = sentence_lookup_as_begin_index(sent, eojeol_lookup)

    BOS_word = words[0]
    EOS_word = words[-1]

    edges = [[BOS_word, word, 0] for word in bindex[closest(0, n, bindex)]]
    for words_in_b in bindex:
        for from_word in words_in_b:
            adj_b = closest(from_word.e, n, bindex)
            if adj_b == -1:
                edges.append([from_word, EOS_word, 0])
            else:
                for to_word in bindex[adj_b]:
                    if from_word.len == 0 and to_word.len == 0:
                        continue
                    edges.append([from_word, to_word, 0])

    return words, edges # (words, edges)

def sentence_lookup_as_begin_index(sent, eojeol_lookup):
    """
        >>> eojeol_lookup = WordLookup(dictionary)
        >>> words, bindex = sentence_lookup_as_begin_index('공연을했다', eojeol_lookup)

        >>> bindex
        $ [[Word(공연, 공연/Noun, len=2, b=0, e=2, L),
            Word(공연을, 공연/Noun + 을/Josa, len=3, b=0, e=3, L)],
           [],
           [],
           [Word(했다, 하/Verb + 았다/Eomi, len=2, b=3, e=5, L)],
           []]
    """

    n = len(sent.replace(' ',''))
    words = sentence_lookup(sent, eojeol_lookup)

    # if there exist no word in dictionary
    if len(words) <= 2:
        return words, []

    bindex = [[] for _ in range(n)]
    for word in words[1:-1]:
        bindex[word.b].append(word)

    return words, bindex
