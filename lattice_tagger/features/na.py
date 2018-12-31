"""
Feature from Lattice-based Discriminative Approach for Korean Morphological Analysis
Seoung-Hoon Na, Chang-Hyun Kim, and Young-Kil Kim (2014)
"""

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

        $ (1, 0, 1, 0, '입', 'Adjective', 1, 4, '입니다')
        $ (0, 1, 0, 1, '입니다', 'Adjective', 3, 4, '입니다')

        >>> word = Word('아이오아이', '아이오아이', None, 'Noun', None, 5)
        >>> morph_to_feature_na(word, is_L=True)

        $ (1, 0, 0, 0, '아이오아이', 'Noun', 5, 5, '아이오아이')

    """
    if is_L:
        return L_to_feature(word)
    elif word.morph1:
        return R_to_feature(word)
    return None

def L_to_feature(word):
    n = len(word.morph0)
    ls = 1
    rs = 0
    lo = 1 if ((word.morph1) and (word.word[n-1] != word.morph0[-1])) else 0
    ro = 0
    w = word.word[:n]
    t = word.tag0
    n_ = n + (0 if word.morph1 is None else len(word.morph1))
    w_ = word.word
    return (ls, rs, lo, ro, w, t, n, n_, w_)

def R_to_feature(word):
    n = len(word.morph1)
    ls = 0
    rs = 1
    lo = 0
    ro = 1 if ((word.morph1) and (word.word[n-1] != word.morph0[-1])) else 0
    w = word.word[-n:]
    t = word.tag0
    n_ = n + len(word.morph0)
    w_ = word.word
    return (ls, rs, lo, ro, w, t, n, n_, w_)