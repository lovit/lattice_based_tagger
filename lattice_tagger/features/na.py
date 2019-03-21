"""
Feature from Lattice-based Discriminative Approach for Korean Morphological Analysis
Seoung-Hoon Na, Chang-Hyun Kim, and Young-Kil Kim (2014)
"""

from collections import namedtuple
from lattice_tagger.utils import text_to_words
from .feature import AbstractFeatureTransformer


class NaFeatureTransformer(WordsEncoder):
    def encode(self, words):
        morphs, morph_features = self._to_morph_features(words)
        features = []
        n = len(words)
        for i in range(1, n):
            features_ = first_order_feature(
                morph_features[i-1],
                morph_features[i]
            )
            features_ += second_order_feature(
                morph_features[i-1],
                morph_features[i],
                morph_features[i+1]
            )
            features.append(features_)
        return morphs[1:-1], features

    def _to_morph_features(self, words):
        features = []
        morphs = []
        for word in words:
            features.append(morph_to_feature(word, is_L=True))
            morphs.append((word.morph0, word.tag0))
            if word.tag1 is not None:
                features.append(morph_to_feature(word, is_L=False))
                morphs.append((word.morph1, word.tag1))
        return morphs, features


class Feature(namedtuple('Feature', 'ls rs lo ro w t n n_ w_')):
    """
    Usage
    -----
        >>> feature = Feature(True, False, False, False, '아이오아이', 'Noun', 5, 5, '아이오아이')
        >>> print(feature)

        $ (ls=True, rs=False, lo=False, ro=False, w=아이오아이, t=Noun, n=5, n_=5, w_=아이오아이)
    """

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return '(%s)' % ', '.join(['{}={}'.format(k,v) for k,v in self._asdict().items()])


def morph_to_feature(word, is_L=True):
    """
    ls : Is there white space before morpheme
    rs : Is there white space after morpheme
    lo : Is the first syllable of morpheme derived from syllable mapping
    ro : Is the last syllable of morpheme derived from syllable mapping
    w : Surfacial form of morpheme
    t : Tag of morpheme
    n : Length of the surface form of morpheme
    n_ : Extended length of the surface form of morpheme using lo and ro (compound feature)
    w_ : Extended surface form of morpheme using lo and ro

    Usage
    -----
        >>> from lattice_tagger.utils import Word
        >>> from lattice_tagger.feature import morph_to_feature_na
        >>> word = Word('입니다', '이', 'ㅂ니다', 'Adjective', 'Eomi', 3)
        >>> morph_to_feature_na(word, is_L=True)
        >>> morph_to_feature_na(word, is_L=False)

        $ (ls=True, rs=False, lo=True, ro=False, w=입, t=Adjective, n=1, n_=4, w_=이)
        $ (ls=False, rs=True, lo=False, ro=True, w=입니다, t=Adjective, n=3, n_=4, w_=ㅂ니다)

        >>> word = Word('아이오아이', '아이오아이', None, 'Noun', None, 5)
        >>> morph_to_feature_na(word, is_L=True)

        $ (ls=1, rs=0, lo=0, ro=0, w=아이오아이, t=Noun, n=5, n_=5, w_=아이오아이)

    """
    if is_L:
        return L_to_feature(word)
    elif word.morph1:
        return R_to_feature(word)
    return None

def L_to_feature(word):
    n = len(word.morph0)
    ls = True
    rs = False
    lo = True if ((word.morph1) and (word.word[n-1] != word.morph0[-1])) else False
    ro = False
    w = word.word[:n]
    t = word.tag0
    n_ = n + (0 if word.morph1 is None else len(word.morph1))
    w_ = word.morph0
    return Feature(ls, rs, lo, ro, w, t, n, n_, w_)

def R_to_feature(word):
    n = len(word.morph1)
    ls = False
    rs = True
    lo = False
    ro = True if ((word.morph1) and (word.word[n-1] != word.morph0[-1])) else False
    w = word.word[-n:]
    t = word.tag0
    n_ = n + len(word.morph0)
    w_ = word.morph1
    return Feature(ls, rs, lo, ro, w, t, n, n_, w_)

def first_order_feature(fi, fj):
    """
    ls : Is there white space before morpheme
    rs : Is there white space after morpheme
    lo : Is the first syllable of morpheme derived from syllable mapping
    ro : Is the last syllable of morpheme derived from syllable mapping
    w : Surfacial form of morpheme
    t : Tag of morpheme
    n : Length of the surface form of morpheme
    n_ : Extended length of the surface form of morpheme using lo and ro (compound feature)
    w_ : Extended surface form of morpheme using lo and ro

    0 - 3   : (tj, n_j), (tj, n_i, n_j), (ti, tj, n_i, n_j), (ti, tj, roi),
    4 - 8   : (tj, roi), (tj, roj), (tj, lsj), (tj, lsj, loj), (tj, rsj, roj),
    9 - 14  : (tj, wj), (tj, w_j), (wi, wj), (w_i, wj), (ti, tj, wj), (ti, tj, w_j),
    15 - 18 : (tj, w_i, w_j), (ti, wi, wj), (ti, w_i, w_j), (ti, tj, wi),
    19 - 21 : (ti, tj, w_i), (ti, tj, wi, wj), (ti, tj, w_i, w_j)

    Usage
    -----
        >>> sent = '너무너무너무/Noun 는/Josa 아이오아이/Noun 의/Josa 노래/Noun 이/Adjective+ㅂ니다/Eomi'
        >>> features = text_to_features(sent)
        >>> first_order_feature(features[0], features[1])

        $ [(0, 'Josa', 1),
           (1, 'Josa', 6, 1),
           (2, 'Noun', 'Josa', 6, 1),
           (3, 'Noun', 'Josa', False),
           (4, 'Josa', False),
           (5, 'Josa', False),
           (6, 'Josa', True),
           (7, 'Josa', True, False),
           (8, 'Josa', False, False),
           (9, 'Josa', '는'),
           (10, 'Josa', '는'),
           (11, '너무너무너무', '는'),
           (12, '너무너무너무', '는'),
           (13, 'Noun', 'Josa', '는'),
           (14, 'Noun', 'Josa', '는'),
           (15, 'Josa', '너무너무너무', '는'),
           (16, 'Noun', '너무너무너무', '는'),
           (17, 'Noun', '너무너무너무', '는'),
           (18, 'Noun', 'Josa', '너무너무너무'),
           (19, 'Noun', 'Josa', '너무너무너무'),
           (20, 'Noun', 'Josa', '너무너무너무', '는'),
           (21, 'Noun', 'Josa', '너무너무너무', '는')]
    """

    features = [
        (0, fj.t, fj.n_),
        (1, fj.t, fi.n_, fj.n_),
        (2, fi.t, fj.t, fi.n_, fj.n_),
        (3, fi.t, fj.t, fi.ro),
        (4, fj.t, fi.ro),
        (5, fj.t, fj.ro),
        (6, fj.t, fj.ls),
        (7, fj.t, fj.ls, fj.lo),
        (8, fj.t, fj.rs, fj.ro),
        (9, fj.t, fj.w),
        (10, fj.t, fj.w_),
        (11, fi.w, fj.w),
        (12, fi.w_, fj.w),
        (13, fi.t, fj.t, fj.w),
        (14, fi.t, fj.t, fj.w_),
        (15, fj.t, fi.w_, fj.w_),
        (16, fi.t, fi.w, fj.w),
        (17, fi.t, fi.w_, fj.w_),
        (18, fi.t, fj.t, fi.w),
        (19, fi.t, fj.t, fi.w_),
        (20, fi.t, fj.t, fi.w, fj.w),
        (21, fi.t, fj.t, fi.w_, fj.w_)
    ]
    return features

def second_order_feature(fi, fj, fk):
    """
    ls : Is there white space before morpheme
    rs : Is there white space after morpheme
    lo : Is the first syllable of morpheme derived from syllable mapping
    ro : Is the last syllable of morpheme derived from syllable mapping
    w : Surfacial form of morpheme
    t : Tag of morpheme
    n : Length of the surface form of morpheme
    n_ : Extended length of the surface form of morpheme using lo and ro (compound feature)
    w_ : Extended surface form of morpheme using lo and ro

    22 - 26 : (ti, tk, wj), (tk, wi, wj), (ti, tj, wk), (ti, tj, tk, wk), (ti, tj, tk, wj, wk)
    27 - 30 : (ti, tj, tk, wi, wj, wk), (ti, tj, tk, wj), (ti, tj, tk, wi), (ti, tj, tk, wi, wk)

    Usage
    -----
        >>> sent = '너무너무너무/Noun 는/Josa 아이오아이/Noun 의/Josa 노래/Noun 이/Adjective+ㅂ니다/Eomi'
        >>> features = text_to_features(sent)
        >>> second_order_feature(features[0], features[1], features[2])

        $ [(22, 'Noun', 'Noun', '는'),
           (23, 'Noun', '너무너무너무', '는'),
           (24, 'Noun', 'Josa', '아이오아이'),
           (25, 'Noun', 'Josa', 'Noun', '아이오아이'),
           (26, 'Noun', 'Josa', 'Noun', '는', '아이오아이'),
           (27, 'Noun', 'Josa', 'Noun', '너무너무너무', '는', '아이오아이'),
           (28, 'Noun', 'Josa', 'Noun', '는'),
           (29, 'Noun', 'Josa', 'Noun', '너무너무너무'),
           (30, 'Noun', 'Josa', 'Noun', '너무너무너무', '아이오아이')]
    """

    features = [
        (22, fi.t, fk.t, fj.w),
        (23, fk.t, fi.w, fj.w),
        (24, fi.t, fj.t, fk.w),
        (25, fi.t, fj.t, fk.t, fk.w),
        (26, fi.t, fj.t, fk.t, fj.w, fk.w),
        (27, fi.t, fj.t, fk.t, fi.w, fj.w, fk.w),
        (28, fi.t, fj.t, fk.t, fj.w),
        (29, fi.t, fj.t, fk.t, fi.w),
        (30, fi.t, fj.t, fk.t, fi.w, fk.w)
    ]
    return features
