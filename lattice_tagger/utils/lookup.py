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
        >>> dictionary = MorphemeDictionary(tag_to_morphs)
        >>> eojeol_lookup = LRLookup(dictionary)

        >>> sent = '너무너무너무는 아이오아이의 노래입니다'
        >>> sentence_lookup(sent, eojeol_lookup)

        $ [(Word(너무너무너무, 너무너무너무/Noun, len=6), 0, 6),
           (Word(는, 는/Josa, len=1), 6, 7),
           (Word(아이오아이, 아이오아이/Noun, len=5), 7, 12),
           (Word(의, 의/Josa, len=1), 12, 13),
           (Word(노래, 노래/Noun, len=2), 13, 15),
           (Word(입니다, 이/Adjective + ㅂ니다/Eomi, len=3), 15, 18)]
    """

    offset = 0
    nodes = []
    for eojeol in sent.split():
        nodes += eojeol_lookup(eojeol, offset)
        offset += len(eojeol)
    return nodes

class LRLookup:
    """
    Assume that eojeol has no space noise

    Usage
    -----
        >>> morph_dict = MorphemeDictionary(tag_to_morphs)
        >>> morph_dict.as_Word('했다')

        $ [Word(했다, 하/Verb + 았다/Eomi, len=2)]

        >>> morph_dict.as_Word('공연')

        $ [Word(공연, 공연/Noun, len=2)]

        >>> eojeol_lookup = LRLookup(morph_dict)
        >>> eojeol_lookup('공연했다')

        $ [(Word(공연, 공연/Noun, len=2), 0, 2), (Word(했다, 하/Verb + 았다/Eomi, len=2), 2, 4)]

        >>> eojeol_lookup('공연했다', offset=3)

        $ [(Word(공연, 공연/Noun, len=2), 3, 5), (Word(했다, 하/Verb + 았다/Eomi, len=2), 5, 7)]

    """

    def __init__(self, dictionary, templates=None):
        self.dictionary = dictionary
        if templates is None:
            templates = self._default_templates()
        self.templates = templates

    def _default_templates(self):
        templates = [
            (Noun, Josa),
            (Noun, Adjective),
            (Noun, Verb),
        ]
        return templates

    def __call__(self, eojeol, offset=0):
        return self.lookup(eojeol, offset)

    def lookup(self, eojeol, offset=0):
        def accept(l_, r_, template):
            return l_.tag0 == template[0] and r_.tag0 == template[1]

        words = self.dictionary.as_Word(eojeol)

        if words:
            return [(word, offset, offset + word.len) for word in words]

        n = len(eojeol)
        for i in range(1, n):
            l = self.dictionary.as_Word(eojeol[:i])
            r = self.dictionary.as_Word(eojeol[i:])
            for l_ in l:
                for r_ in r:
                    for template in self.templates:
                        if not accept(l_, r_, template):
                            continue
                        words.append((l_, offset, offset + l_.len))
                        words.append((r_, offset + l_.len, offset + l_.len + r_.len))
        return words


class SubwordLookup:
    """
    Assume that eojeol has space noise.
    Check whether subword is enrolled in dictionary for all subword.

    Usage
    -----
        >>> eojeol_lookup = SubwordLookup(morph_dict)
        >>> eojeol_lookup('공연을했다', offset=7)

        $ [(Word(공연, 공연/Noun, len=2), 7, 9),
           (Word(을, 을/Josa, len=1), 9, 10),
           (Word(했다, 하/Verb + 았다/Eomi, len=2), 10, 12)]
    """

    def __init__(self, dictionary):
        self.dictionary = dictionary

    def __call__(self, eojeol, offset=0):
        return self.lookup(eojeol, offset)

    def lookup(self, eojeol, offset=0):
        words = []
        n = len(eojeol)
        for b in range(n):
            for e in range(b+1, n+1):
                sub = eojeol[b:e]
                words += [
                    (word, offset + b, offset + e) for word in self.dictionary.as_Word(sub)
                    if not (word.tag0 == Eomi)
                ]
        return words