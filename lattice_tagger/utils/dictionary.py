from collections import namedtuple
from glob import glob
from .utils import installpath
from .utils import load_rules
from lattice_tagger.tagset import *

def str_to_morphtag(word):
    """
    Usage
    -----
        >>> word_to_morphtag('너무너무너무/Noun')
        $ [['너무너무너무', 'Noun']]

        >>> word_to_morphtag('이/Adjective+ㅂ니다/Eomi')
        $ [['이', 'Adjective'], ['ㅂ니다', 'Eomi']]
    """

    return [morphtag.split('/',1) for morphtag in word.split('+')]

def text_to_words(sent, morph_text):
    """
    Usage
    -----
        >>> sent = '너무너무너무는 아이오아이의 노래 입니다'
        >>> morph_text = '너무너무너무/Noun 는/Josa 아이오아이/Noun 의/Josa 노래/Noun 이/Adjective+ㅂ니다/Eomi'
        >>> text_to_words(sent, morph_text)

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6),
           Word(는, 는/Josa, len=1, b=6, e=7),
           Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12),
           Word(의, 의/Josa, len=1, b=12, e=13),
           Word(노래, 노래/Noun, len=2, b=13, e=15),
           Word(이+ㅂ니다, 이/Adjective + ㅂ니다/Eomi, len=4, b=15, e=18),
           Word(EOS, EOS/EOS, len=0, b=18, e=18)]


        >>> sent = '빙수 고명으로 얹는 삶은 단팥과 찰떡 젤리 포장도 나와 있다'
        >>> morph_text = '빙수/Noun 고명/Noun+으로/Josa 얹/Verb+는/Eomi 삶/Verb+은/Eomi 단팥/Noun+과/Josa 찰떡/Noun 젤리/Noun 포장/Noun+도/Josa 나오/Verb+아/Eomi 있/Verb+다/Eomi'
        >>> text_to_words(sent, morph_text)

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(빙수, 빙수/Noun, len=2, b=0, e=2),
           Word(고명으로, 고명/Noun + 으로/Josa, len=4, b=2, e=6),
           Word(얹는, 얹/Verb + 는/Eomi, len=2, b=6, e=8),
           Word(삶은, 삶/Verb + 은/Eomi, len=2, b=8, e=10),
           Word(단팥과, 단팥/Noun + 과/Josa, len=3, b=10, e=13),
           Word(찰떡, 찰떡/Noun, len=2, b=13, e=15),
           Word(젤리, 젤리/Noun, len=2, b=15, e=17),
           Word(포장도, 포장/Noun + 도/Josa, len=3, b=17, e=20),
           Word(나와, 나오/Verb + 아/Eomi, len=2, b=20, e=22),
           Word(있다, 있/Verb + 다/Eomi, len=2, b=22, e=24),
           Word(EOS, EOS/EOS, len=0, b=24, e=24)]
    """

    b = 0
    words = [Word(BOS, BOS, None, BOS, None, 0, 0, 0)]
    for eojeol, morphs in zip(sent.split(), morph_text.split()):
        morphtags = str_to_morphtag(morphs)
        morph0, tag0 = morphtags[0]
        n = len(eojeol)
        e = b + n
        if len(morphtags) == 1:
            word = Word(morph0, morph0, None, tag0, None, n, b, e)
        elif len(morphtags) == 2:
            morph1, tag1 = morphtags[1]
            word = Word(eojeol, morph0, morph1, tag0, tag1, len(eojeol), b, e)
        else:
            raise ValueError('Word (%s) consists of three or more morphemes' % word)
        b += n
        words.append(word)
    words.append(Word(EOS, EOS, None, EOS, None, 0, b, b))
    return words

def flatten_words(words):
    """
        >>> sent = '너무너무너무는 아이오아이의 노래 입니다'
        >>> morph_text = '너무너무너무/Noun 는/Josa 아이오아이/Noun 의/Josa 노래/Noun 이/Adjective+ㅂ니다/Eomi'
        >>> words = text_to_words(sent, morph_text)
        >>> words_ = flatten_words(words)

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6),
           Word(는, 는/Josa, len=1, b=6, e=7),
           Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12),
           Word(의, 의/Josa, len=1, b=12, e=13),
           Word(노래, 노래/Noun, len=2, b=13, e=15),
           Word(이, 이/Adjective, len=1, b=15, e=16),
           Word(ㅂ니다, ㅂ니다/Eomi, len=2, b=16, e=18),
           Word(EOS, EOS/EOS, len=0, b=18, e=18)]


        >>> sent = '봤어 영화관 가면 늘 보는 정도인데 뭘'
        >>> morph_text = '보/Verb+았어/Eomi 영화관/Noun 가/Verb+면/Eomi 늘/Adverb 보/Verb+는/Eomi 정도/Noun+인데/Josa 무엇/Pronoun+을/Josa'
        >>> words = text_to_words(sent, morph_text)
        >>> words_ = flatten_words(words)

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(보, 보/Verb, len=1, b=0, e=1),
           Word(았어, 았어/Eomi, len=2, b=1, e=2),
           Word(영화관, 영화관/Noun, len=3, b=2, e=5),
           Word(가, 가/Verb, len=1, b=5, e=6),
           Word(면, 면/Eomi, len=1, b=6, e=7),
           Word(늘, 늘/Adverb, len=1, b=7, e=8),
           Word(보, 보/Verb, len=1, b=8, e=9),
           Word(는, 는/Eomi, len=1, b=9, e=10),
           Word(정도, 정도/Noun, len=2, b=10, e=12),
           Word(인데, 인데/Josa, len=2, b=12, e=14),
           Word(무엇, 무엇/Pronoun, len=2, b=14, e=15),
           Word(을, 을/Josa, len=1, b=15, e=15),
           Word(EOS, EOS/EOS, len=0, b=15, e=15)]
    """

    words_ = []
    for word in words:
        if word.tag1 is None:
            words_.append(word)
            continue
        len0 = len(word.morph0)
        len1 = len(word.morph1)
        b = word.b
        m = min(word.e, word.b + len0)
        e = word.e
        if 'ㄱ' <= word.morph1[0] <= 'ㅎ':
            len1 -= 1
        word0 = Word(word.morph0, word.morph0, None, word.tag0, None, len0, b, m)
        word1 = Word(word.morph1, word.morph1, None, word.tag1, None, len1, m, e)
        words_.append(word0)
        words_.append(word1)
    return words_

class Word(namedtuple('Word', 'word morph0 morph1 tag0 tag1 len b e')):
    """
    Usage
    -----
        >>> word = Word('아이오아이', '아이오아이', None, 'Noun', None, 5)
        >>> print(word)

        $ Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5)

        >>> word = Word('가고있는', '가고있', '는', 'Verb', 'Eomi', 4, 2, 6)
        >>> print(word)

        $ Word(가고있는, 가고있/Verb + 는/Eomi, len=4, b=2, e=6)

        >>> word = Word('간', '가', 'ㄴ', 'Verb', 'Eomi', 1, 3, 4)
        >>> print(word)

        $ Word(간, 가/Verb + ㄴ/Eomi, len=1, b=3, e=4)
    """

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        if self.morph1:
            args = (self.word, self.morph0, self.tag0, self.morph1, self.tag1, self.len, self.b, self.e)
            return 'Word(%s, %s/%s + %s/%s, len=%d, b=%d, e=%d)' % args
        args = (self.word, self.morph0, self.tag0, self.len, self.b, self.e)
        return 'Word(%s, %s/%s, len=%d, b=%d, e=%d)' % args


class WordDictionary:
    """
    Usage
    -----
        >>> tag_to_morphs = {
        >>>     Noun: {'아이', '이', '노래', '너무너무너무', '아이오아이', '공연', '춤', '연습'},
        >>>     Josa: {'는', '의', '을', '이'},
        >>>     Verb: {'춥니다'},
        >>>     Adjective: {'있습니다', '입니다'},
        >>> }
        
        >>> dictionary = WordDictionary(tag_to_morphs)
        >>> dictionary.check('아이', 'Noun')
        $ True

        >>> dictionary.get_tags('아이')
        $ ['Noun']

        >>> dictionary.lookup('아이오아이')
        $ [Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5)]

        >>> dictionary.lookup('아이오아이', 5)
        $ [Word(아이오아이, 아이오아이/Noun, len=5, b=5, e=10)]
    """

    def __init__(self, tag_to_morphs):
        self.tag_to_morphs = tag_to_morphs

    def lookup(self, morph, b=0):
        n = len(morph)
        e = b + n
        words = [
            Word(morph, morph, None, tag, None, n, b, e)
            for tag in self.get_tags(morph)]
        return words

    def check(self, morph, tag):
        return morph in self.tag_to_morphs.get(tag, {})

    def get_tags(self, morph):
        return [tag for tag, morphs in self.tag_to_morphs.items() if morph in morphs]

    def add(self, morphs, tag, force=False):
        if isinstance(morphs, str):
            morphs = {morphs}
        if (not force) and not (tag in self.tag_to_morphs):
            raise ValueError('{} tag does not exist in dictionary'.format(tag))
        if not (tag in self.tag_to_morphs):
            self.tag_to_morphs[tag] = set(morphs)
        self.tag_to_morphs[tag].update(morphs)

    def remove_words(self, morphs, tag):
        if isinstance(morphs, str):
            morphs = {morphs}
        if not isinstance(morphs, set):
            morphs = set(morphs)
        if not (tag in self.tag_to_morphs):
            raise ValueError('{} tag does not exist in dictioanry')
        before = self.tag_to_morphs[tag]
        before = {morph for morph in before if not (morph in morphs)}
        self.tag_to_morphs[tag] = before


class MorphemeDictionary(WordDictionary):
    """
    Usage
    -----
        >>> tag_to_morphs = {
        >>>     Noun: {'아이', '이', '노래', '너무너무너무', '아이오아이', '공연', '춤', '연습'},
        >>>     Josa: {'는', '의', '을', '이'},
        >>>     Verb: {'추', '하'},
        >>>     Adjective: {'있', '이'},
        >>>     Eomi: {'ㅂ니다', '습니다', '았습니다', '다', 'ㅆ다'}
        >>> }
        >>> surface_to_lemma = {
        >>>     '했': (('하', '았'),),
        >>>     '있': (('이', 'ㅆ'),),
        >>>     '입': (('이', 'ㅂ'),)
        >>> }

        >>> dictionary = MorphemeDictionary(tag_to_morphs, surface_to_lemma)
        >>> dictionary.lemmatize('있다')
        $ [(('있', 'Adjective'), ('다', 'Eomi')), (('이', 'Adjective'), ('ㅆ다', 'Eomi'))]

        >>> dictionary.lookup('있다', b=3)
        $ [Word(있다, 있/Adjective + 다/Eomi, len=2, b=3, e=5),
        $  Word(있다, 이/Adjective + ㅆ다/Eomi, len=2, b=3, e=5)]

        >>> dictionary.lookup('아이오아이', 5)
        $ [Word(아이오아이, 아이오아이/Noun, len=5, b=5, e=10)]
    """

    def __init__(self, tag_to_morph, surface_to_lemma=None):
        super().__init__(tag_to_morph)
        if surface_to_lemma is None:
            surface_to_lemma = {}
        self.surface_to_lemma = surface_to_lemma

    def lookup(self, word, b=0):
        n = len(word)
        e = b + n
        words = [
            Word(word, word, None, tag, None, n, b, e)
            for tag in self.get_tags(word)]
        for (m0, t0), (m1, t1) in self.lemmatize(word):
            words.append(Word(word, m0, m1, t0, t1, n, b, e))
        return words

    def lemmatize(self, word):
        lemmas = []
        for i in range(1, len(word)+1):
            for stem, eomi in self._lemmatize(word[:i], word[i:]):
                lemmas.append((stem, eomi))
        return lemmas

    def _lemmatize(self, l, r):
        if self.check(l, Verb) and self.check(r, Eomi):
            yield (l, Verb), (r, Eomi)
        if self.check(l, Adjective) and self.check(r, Eomi):
            yield (l, Adjective), (r, Eomi)
        if not l[-1] in self.surface_to_lemma:
            return None
        l_pre = l[:-1]
        for l_lemma, r_lemma in self.surface_to_lemma[l[-1]]:
            stem = l_pre + l_lemma
            eomi = r_lemma + r
            if self.check(eomi, Eomi):
                if self.check(stem, Verb):
                    yield (stem, Verb), (eomi, Eomi)
                if self.check(stem, Adjective):
                    yield (stem, Adjective), (eomi, Eomi)


class DemoWordDictionary(WordDictionary):
    """
    Word dictionary for demo and development
    """

    def __init__(self):
        tag_to_words = load_dictionary('%s/resources/demo_word/' % installpath)
        super().__init__(tag_to_words)


class DemoMorphemeDictionary(MorphemeDictionary):
    """
    Morpheme dictionary for demo and development
    """

    def __init__(self):
        tag_to_morphs = load_dictionary('%s/resources/demo_morph/' % installpath)
        surface_to_canon = load_rules('%s/resources/demo_morph/rules.json' % installpath)
        super().__init__(tag_to_morphs, surface_to_canon)


class BaseMorphemeDictionary(MorphemeDictionary):
    """
    Morpheme dictionary trained from Sejong Corpus
    """

    def __init__(self):
        tag_to_morphs = load_dictionary('%s/resources/base/' % installpath)
        surface_to_canon = load_rules('%s/resources/base/rules.json' % installpath)
        super().__init__(tag_to_morphs, surface_to_canon)

def load_dictionary(directory):
    def load(path):
        with open(path, encoding='utf-8') as f:
            words = {word.split()[0] for word in f}
        return words

    def parse_tag(path):
        return path.split('/')[-1][:-4]

    paths = glob('%s/*.txt' % directory)
    tag_to_morphs = {parse_tag(path):load(path) for path in paths}
    return tag_to_morphs
