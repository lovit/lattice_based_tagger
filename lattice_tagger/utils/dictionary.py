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

def text_to_words(text):
    """
    Usage
    -----
        >>> text = '너무너무너무/Noun 는/Josa 아이오아이/Noun 의/Josa 노래/Noun 이/Adjective+ㅂ니다/Eomi'
        >>> text_to_words(sent)

        $ [Word(BOS, BOS/BOS, len=0),
           Word(너무너무너무, 너무너무너무/Noun, len=6),
           Word(는, 는/Josa, len=1),
           Word(아이오아이, 아이오아이/Noun, len=5),
           Word(의, 의/Josa, len=1),
           Word(노래, 노래/Noun, len=2),
           Word(이+ㅂ니다, 이/Adjective + ㅂ니다/Eomi, len=4),
           Word(EOS, EOS/EOS, len=0)]
    """

    words = [Word(BOS, BOS, None, BOS, None, 0)]
    for word in text.split():
        morphtags = str_to_morphtag(word)
        morph0, tag0 = morphtags[0]
        if len(morphtags) == 1:
            word = Word(morph0, morph0, None, tag0, None, len(morph0))
        elif len(morphtags) == 2:
            morph1, tag1 = morphtags[1]
            word = Word('%s+%s' % (morph0, morph1), morph0, morph1, tag0, tag1, len(morph0) + len(morph1))
        else:
            raise ValueError('Word (%s) consists of three or more morphemes' % word)
        words.append(word)
    words.append(Word(EOS, EOS, None, EOS, None, 0))
    return words

class Word(namedtuple('Word', 'word morph0 morph1 tag0 tag1 len')):
    """
    Usage
    -----
        >>> word = Word('아이오아이', '아이오아이', None, 'Noun', None, 5)
        >>> print(word)

        $ Word(아이오아이, 아이오아이/Noun, len=5)

        >>> word = Word('가고있는', '가고있', '는', 'Verb', 'Eomi', 4)
        >>> print(word)

        $ Word(가고있는, 가고있/Verb + 는/Eomi, len=4)

        >>> word = Word('간', '가', 'ㄴ', 'Verb', 'Eomi', 1)
        >>> print(word)

        $ Word(간, 가/Verb + ㄴ/Eomi, len=1)

    """

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        if self.morph1:
            args = (self.word, self.morph0, self.tag0, self.morph1, self.tag1, self.len)
            return 'Word(%s, %s/%s + %s/%s, len=%d)' % args
        args = (self.word, self.morph0, self.tag0, self.len)
        return 'Word(%s, %s/%s, len=%d)' % args


class WordDictionary:
    """
    Usage
    -----
        >>> tag_to_words = {
        >>>     Noun: {'아이', '이', '노래', '너무너무너무', '아이오아이', '공연', '춤', '연습'},
        >>>     Josa: {'는', '의', '을', '이'},
        >>>     Verb: {'춥니다'},
        >>>     Adjective: {'있습니다', '입니다'},
        >>> }
        
        >>> dictionary = WordDictionary(tag_to_words)
        >>> dictionary.check('아이', 'Noun')

        $ True

        >>> dictionary.get_tags('아이')

        $ ['Noun']
    """

    def __init__(self, tag_to_morph):
        self.tag_to_morph = tag_to_morph

    def as_Word(self, word):
        words = [
            Word(word, word, None, tag, None, len(word))
            for tag in self.get_tags(word)]
        return words

    def check(self, word, tag):
        return word in self.tag_to_morph.get(tag, {})

    def get_tags(self, word):
        return [tag for tag, words in self.tag_to_morph.items() if word in words]

    def add(self, words, tag, force=False):
        if isinstance(words, str):
            words = {words}
        if (not force) and not (tag in self.tag_to_morph):
            raise ValueError('{} tag does not exist in dictionary'.format(tag))
        if not (tag in self.tag_to_morph):
            self.tag_to_morph[tag] = set(words)
        self.tag_to_morph[tag].update(words)

    def remove_words(self, words, tag):
        if isinstance(words, str):
            words = {words}
        if not isinstance(words, set):
            words = set(words)
        if not (tag in self.tag_to_morph):
            raise ValueError('{} tag does not exist in dictioanry')
        before = self.tag_to_morph[tag]
        before = {word for word in before if not (word in words)}
        self.tag_to_morph[tag] = before


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

        >>> dictionary = MorphemeDictionary(tag_to_words)
        >>> dictionary.lemmatize('있다')

        $ [(('있', 'Adjective'), ('다', 'Eomi')), (('이', 'Adjective'), ('ㅆ다', 'Eomi'))]

    """

    def __init__(self, tag_to_morph, surface_to_canon=None):
        super().__init__(tag_to_morph)
        if surface_to_canon is None:
            surface_to_canon = {}
        self.surface_to_canon = surface_to_canon

    def as_Word(self, word):
        length = len(word)
        words = [
            Word(word, word, None, tag, None, length)
            for tag in self.get_tags(word)]
        for (m0, t0), (m1, t1) in self.lemmatize(word):
            words.append(Word(word, m0, m1, t0, t1, length))
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
        if not l[-1] in self.surface_to_canon:
            return None
        l_pre = l[:-1]
        for l_suf, r_pre in self.surface_to_canon[l[-1]]:
            stem = l_pre + l_suf
            eomi = r_pre + r
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
