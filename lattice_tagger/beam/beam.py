from ..tagset import *
from lattice_tagger.utils import Word


def beam_search(bindex, len_sent, chars, score_functions, beam_size=5, max_len=8, debug=False):

    bos = Sequence([Word(BOS, BOS, None, BOS, None, 0, 0, 0)], 0)
    beam = Beam([[bos]], beam_size)

    for e in range(1, len_sent + 1):

        growns = []

        # find candidates
        b_min = max(0, e - max_len)
        for b in range(b_min, e):
            immatures = beam[b]
            expandes = [word for word in bindex[b] if word.e == e]

            # prepare unknown Word
            if not expandes:
                sub = chars[b:e]
                expandes = [Word(sub, sub, None, Unk, None, e - b, b, e)]

            # score
            for immature in immatures:
                for expand in expandes:
                    # skip successive two unknown words
                    if (immature.num_unk > 0) and (expand.tag0 == Unk) and (b_min < b):
                        continue
                    # calculate
                    increment = score_functions(immature, expand)
                    growns.append(immature.add(expand, increment))

        # append growns to beam
        beam.append(growns)

        if debug:
            print('\n{}\nEnd point = {}, len(growns) = {}\n'.format('-'*40, e, len(growns)))
            growns = sorted(growns, key=lambda x:-x.score)
            for grown in growns:
                print(grown, end='\n\n')

    return beam.beam[-1]

class Beam:
    """
        >>> word0 = Word('BOS', 'BOS', None, 'BOS', None, 0, 0, 0)
        >>> word1 = Word('아이오아이', '아이오아이', None, 'Noun', None, 5, 0, 5)
        >>> bos = Sequence([word0], 0.3)
        >>> beam = Beam([bos], k=5)
        >>> immatures = beam[0]
        >>> exapandeds = []
        >>> for immature in immatures:
        >>>     exapandeds.add(immature.add(word1, 1))
    """
    def __init__(self, beam=None, k=5):
        self.k = k
        self.beam = beam if beam is not None else []

    def __getitem__(self, index):
        """index for end point"""
        return self.beam[index]

    def append(self, candidates):
        # descending order of score
        candidates = sorted(candidates, key=lambda x:-x.score)[:self.k]
        self.beam += [candidates]

class Sequence:
    """
        >>> word0 = Word('BOS', 'BOS', None, 'BOS', None, 0, 0, 0)
        >>> word1 = Word('아이오아이', '아이오아이', None, 'Noun', None, 5, 0, 5)

        >>> sequence = Sequence([word0], 0.3)
        $ words = [
            Word(BOS, BOS/BOS, len=0, b=0, e=0)
          ]
          score = 0.3

        >>> sequence.add(word1, score_increment=1)
        $ words = [
            Word(BOS, BOS/BOS, len=0, b=0, e=0)
            Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5)
          ]
          score = 1.3
    """

    def __init__(self, sequences, score, num_unk=0):
        self.sequences = sequences
        self.score = score
        self.num_unk = num_unk

    def add(self, node, score_increment):
        num_unk = self.num_unk + 1 if node.tag0 == Unk else 0
        new_nodes = [n for n in self.sequences] + [node]
        new_score = self.score + score_increment
        return Sequence(new_nodes, new_score, num_unk)

    def __repr__(self):
        words = '[\n    {}\n  ]'.format('\n    '.join([str(w) for w in self.sequences]))
        return 'Sequences(\n  words : {}\n  score : {}\n  num unks in tails : {}\n)'.format(
            words, self.score, self.num_unk)

    def __str__(self):
        return self.__repr__()
