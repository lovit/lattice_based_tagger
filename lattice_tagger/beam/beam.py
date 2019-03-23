import numpy as np
coefficients = (np.random.random_sample(1000) - 0.5).tolist()


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
        candidates = sorted(candidates, key=lambda x:x.score)[:self.k]
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

    def __init__(self, sequences, score):
        self.sequences = sequences
        self.score = score

    def add(self, node, score_increment):
        return Sequence([node for node in self.sequences] + [node], self.score + score_increment)

    def __repr__(self):
        words = '[\n  {}\n]'.format('\n  '.join([str(w) for w in self.sequences]))
        return 'words = {}\nscore = {}'.format(words, self.score)
