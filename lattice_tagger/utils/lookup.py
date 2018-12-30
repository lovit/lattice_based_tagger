from collections import namedtuple
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


class Node(namedtuple('Node', 'word morph0 morph1 tag0 tag1 b e len')):
    """
    Usage
    -----
        >>> node = Node('아이오아이', '아이오아이', None, 'Noun', None, 3, 8, 5)
        >>> print(node)

        $ Node(아이오아이, 아이오아이/Noun, 3, 8, len=5)

        >>> node = Node('가고있는', '가고있', '는', 'Verb', 'Eomi', 0, 4, 4)
        >>> print(node)

        $ Node(가고있는, 가고있/Verb + 는/Eomi, 0, 4, len=4)

        >>> node = Node('간', '가', 'ㄴ', 'Verb', 'Eomi', 5, 6, 1)
        >>> print(node)

        $ Node(간, 가/Verb + ㄴ/Eomi, 5, 6, len=1)

    """

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        if self.morph1:
            args = (self.word, self.morph0, self.tag0,
                    self.morph1, self.tag1, self.b, self.e, self.len)
            return 'Node(%s, %s/%s + %s/%s, %d, %d, len=%d)' % args
        args = (self.word, self.morph0, self.tag0, self.b, self.e, self.len)
        return 'Node(%s, %s/%s, %d, %d, len=%d)' % args

def word_posi_to_node(word, b, e):
    return Node(word.word, word.morph0, word.morph1, word.tag0, word.tag1, b, e, word.len)

def lookup_as_edge(sent, eojeol_lookup):
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
        >>> nodes, edges = lookup_as_edge('공연을했다', eojeol_lookup)
        >>> print(nodes)

        $ ['BOS',
           'EOS',
           Node(공연, 공연/Noun, 0, 2, len=2),
           Node(을, 을/Josa, 2, 3, len=1),
           Node(했다, 하/Verb + 았다/Eomi, 3, 5, len=2)]

        >>> print(edges)

        $ [['BOS', Node(공연, 공연/Noun, 0, 2, len=2), 0],
           [Node(공연, 공연/Noun, 0, 2, len=2), Node(을, 을/Josa, 2, 3, len=1), 0],
           [Node(을, 을/Josa, 2, 3, len=1), Node(했다, 하/Verb + 았다/Eomi, 3, 5, len=2), 0],
           [Node(했다, 하/Verb + 았다/Eomi, 3, 5, len=2), 'EOS', 0]]
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
    nodes = [BOS, EOS]
    for word, b, e in words:
        node = word_posi_to_node(word, b, e)
        bindex[b].append(node)
        nodes.append(node)

    edges = [[BOS, word, 0] for word in bindex[closest(0, n, bindex)]]
    for nodes_b in bindex:
        for node in nodes_b:
            adj_b = closest(node.e, n, bindex)
            if adj_b == -1:
                edges.append([node, EOS, 0])
            else:
                for adj in bindex[adj_b]:
                    edges.append([node, adj, 0])
    return nodes, edges