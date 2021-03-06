from collections import defaultdict
from collections import namedtuple
from glob import glob

from .lemmatizer import analyze_morphology
from ..utils import installpath
from ..utils import left_space_tag
from ..tagset import *


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

def text_to_words(word_text, morph_text, sent=None):
    """
    '+' 는 형태소 결합 (활용)을 표현하는 기호이며, 어절의 구분 기호는 두 칸 띄어쓰기, 단어의 구분 기호는 한 칸 띄어쓰기를 이용한다.

    Usage
    -----
        >>> word_text = '너무너무너무 는  아이오아이 의  노래  입니다'
        >>> morph_text = '너무너무너무/Noun 는/Josa  아이오아이/Noun 의/Josa  노래/Noun  이/Adjective+ㅂ니다/Eomi'
        >>> text_to_words(word_text, morph_text)

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6, L),
           Word(는, 는/Josa, len=1, b=6, e=7),
           Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12, L),
           Word(의, 의/Josa, len=1, b=12, e=13),
           Word(노래, 노래/Noun, len=2, b=13, e=15, L),
           Word(입니다, 이/Adjective + ㅂ니다/Eomi, len=3, b=15, e=18, L),
           Word(EOS, EOS/EOS, len=0, b=18, e=18)]


        >>> word_text = '빙수  고명으로  얹는  삶은  단팥과  찰떡  젤리  포장도  나와 있다'
        >>> morph_text = '빙수/Noun  고명/Noun+으로/Josa  얹/Verb+는/Eomi  삶/Verb+은/Eomi  단팥/Noun+과/Josa  찰떡/Noun  젤리/Noun  포장/Noun+도/Josa  나오/Verb+아/Eomi  있/Verb+다/Eomi'
        >>> text_to_words(word_text, morph_text)

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(빙수, 빙수/Noun, len=2, b=0, e=2, L),
           Word(고명으로, 고명/Noun + 으로/Josa, len=4, b=2, e=6, L),
           Word(얹는, 얹/Verb + 는/Eomi, len=2, b=6, e=8, L),
           Word(삶은, 삶/Verb + 은/Eomi, len=2, b=8, e=10, L),
           Word(단팥과, 단팥/Noun + 과/Josa, len=3, b=10, e=13, L),
           Word(찰떡, 찰떡/Noun, len=2, b=13, e=15, L),
           Word(젤리, 젤리/Noun, len=2, b=15, e=17, L),
           Word(포장도, 포장/Noun + 도/Josa, len=3, b=17, e=20, L),
           Word(나와, 나오/Verb + 아/Eomi, len=2, b=20, e=22, L),
           Word(EOS, EOS/EOS, len=0, b=22, e=22)]


        >>> word_text = '빙수  고명 으로  얹는  삶은  단팥 과  찰떡  젤리  포장 도  나와 있다'
        >>> morph_text = '빙수/Noun  고명/Noun 으로/Josa  얹/Verb+는/Eomi  삶/Verb+은/Eomi  단팥/Noun 과/Josa  찰떡/Noun  젤리/Noun  포장/Noun 도/Josa  나오/Verb+아/Eomi 있/Verb+다/Eomi'
        >>> text_to_words(word_text, morph_text)
        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(빙수, 빙수/Noun, len=2, b=0, e=2, L),
           Word(고명, 고명/Noun, len=2, b=2, e=4, L),
           Word(으로, 으로/Josa, len=2, b=4, e=6),
           Word(얹는, 얹/Verb + 는/Eomi, len=2, b=6, e=8, L),
           Word(삶은, 삶/Verb + 은/Eomi, len=2, b=8, e=10, L),
           Word(단팥, 단팥/Noun, len=2, b=10, e=12, L),
           Word(과, 과/Josa, len=1, b=12, e=13),
           Word(찰떡, 찰떡/Noun, len=2, b=13, e=15, L),
           Word(젤리, 젤리/Noun, len=2, b=15, e=17, L),
           Word(포장, 포장/Noun, len=2, b=17, e=19, L),
           Word(도, 도/Josa, len=1, b=19, e=20),
           Word(나와, 나오/Verb + 아/Eomi, len=2, b=20, e=22, L),
           Word(있다, 있/Verb + 다/Eomi, len=2, b=22, e=24),
           Word(EOS, EOS/EOS, len=0, b=24, e=24)]
    """

    word_text = word_text.split('  ')
    morph_text = morph_text.split('  ')

    nw = len(word_text)
    nm = len(morph_text)
    if nw != nm:
        raise ValueError('Different length of eojeols in (word_text=%d, morph_text=%d)' % (nw, nm))

    if sent is None:
        sent = ' '.join(eojeol.replace(' ', '') for eojeol in word_text)

    chars, ltags = left_space_tag(sent)

    b = 0
    words = [Word(BOS, BOS, None, BOS, None, 0, 0, 0, False)]
    for eojeols, morphs in zip(word_text, morph_text):
        for word, morph in zip(eojeols.split(), morphs.split()):
            morphtags = str_to_morphtag(morph)
            morph0, tag0 = morphtags[0]
            n = len(word)
            e = b + n
            if len(morphtags) == 1:
                word = Word(word, morph0, None, tag0, None, n, b, e, ltags[b] == 1)
            elif len(morphtags) == 2:
                morph1, tag1 = morphtags[1]
                word = Word(word, morph0, morph1, tag0, tag1, n, b, e, ltags[b] == 1)
            else:
                raise ValueError('Word (%s) consists of three or more morphemes' % word)
            b += n
            words.append(word)
    words.append(Word(EOS, EOS, None, EOS, None, 0, b, b, False))
    return words

def flatten_words(words):
    """
        >>> word_text = '너무너무너무 는  아이오아이 의  노래  입니다'
        >>> morph_text = '너무너무너무/Noun 는/Josa  아이오아이/Noun 의/Josa  노래/Noun  이/Adjective+ㅂ니다/Eomi'
        >>> flatten_words(text_to_words(word_text, morph_text))

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(너무너무너무, 너무너무너무/Noun, len=6, b=0, e=6, L),
           Word(는, 는/Josa, len=1, b=6, e=7),
           Word(아이오아이, 아이오아이/Noun, len=5, b=7, e=12, L),
           Word(의, 의/Josa, len=1, b=12, e=13),
           Word(노래, 노래/Noun, len=2, b=13, e=15, L),
           Word(이, 이/Adjective, len=1, b=15, e=16, L),
           Word(ㅂ니다, ㅂ니다/Eomi, len=2, b=16, e=18),
           Word(EOS, EOS/EOS, len=0, b=18, e=18)]


        >>> word_text = '봤어  영화관 가면  늘  보는  정도 인데  뭘'
        >>> morph_text = '보/Verb+았어/Eomi  영화관/Noun 가/Verb+면/Eomi  늘/Adverb  보/Verb+는/Eomi  정도/Noun 인데/Josa  무엇/Pronoun+을/Josa'
        >>> flatten_words(text_to_words(word_text, morph_text))

        $ [Word(BOS, BOS/BOS, len=0, b=0, e=0),
           Word(보, 보/Verb, len=1, b=0, e=1, L),
           Word(았어, 았어/Eomi, len=2, b=1, e=2),
           Word(영화관, 영화관/Noun, len=3, b=2, e=5, L),
           Word(가, 가/Verb, len=1, b=5, e=6),
           Word(면, 면/Eomi, len=1, b=6, e=7),
           Word(늘, 늘/Adverb, len=1, b=7, e=8, L),
           Word(보, 보/Verb, len=1, b=8, e=9, L),
           Word(는, 는/Eomi, len=1, b=9, e=10),
           Word(정도, 정도/Noun, len=2, b=10, e=12, L),
           Word(인데, 인데/Josa, len=2, b=12, e=14),
           Word(무엇, 무엇/Pronoun, len=2, b=14, e=15, L),
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
        word0 = Word(word.morph0, word.morph0, None, word.tag0, None, len0, b, m, word.is_l)
        word1 = Word(word.morph1, word.morph1, None, word.tag1, None, len1, m, e, False)
        words_.append(word0)
        words_.append(word1)
    return words_

class Word(namedtuple('Word', 'word morph0 morph1 tag0 tag1 len b e is_l')):
    """
    Usage
    -----
        >>> word = Word('아이오아이', '아이오아이', None, 'Noun', None, 5, 0, 5, True)
        >>> print(word)

        $ Word(아이오아이, 아이오아이/Noun, len=5, b=0, e=5, L)


        >>> word = Word('가고있는', '가고있', '는', 'Verb', 'Eomi', 4, 2, 6, True)
        >>> print(word)

        $ Word(가고있는, 가고있/Verb + 는/Eomi, len=4, b=2, e=6, L)


        >>> word = Word('간', '가', 'ㄴ', 'Verb', 'Eomi', 1, 3, 4, False)
        >>> print(word)

        $ Word(간, 가/Verb + ㄴ/Eomi, len=1, b=3, e=4)
    """

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.morph1:
            args = (self.word, self.morph0, self.tag0, self.morph1, self.tag1, self.len, self.b, self.e, ', L' if self.is_l else '')
            return 'Word(%s, %s/%s + %s/%s, len=%d, b=%d, e=%d%s)' % args
        args = (self.word, self.morph0, self.tag0, self.len, self.b, self.e, ', L' if self.is_l else '')
        return 'Word(%s, %s/%s, len=%d, b=%d, e=%d%s)' % args


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

        >>> dictionary.lookup('아이오아이', 5, True)
        $ [Word(아이오아이, 아이오아이/Noun, len=5, b=5, e=10, L)]
    """

    def __init__(self, tag_to_morphs):
        self.tag_to_morphs = tag_to_morphs

    def lookup(self, morph, b=0, is_l=False):
        n = len(morph)
        e = b + n
        words = [
            Word(morph, morph, None, tag, None, n, b, e, is_l)
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
        >>> rules = {
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

    def __init__(self, tag_to_morph, rules=None):
        super().__init__(tag_to_morph)
        if rules is None:
            rules = {}
        self.rules = rules

        self.verbs = tag_to_morph.get(Verb, {})
        self.adjectives = tag_to_morph.get(Adjective, {})
        self.eomis = tag_to_morph.get(Eomi, {})

    def lookup(self, word, b=0, is_l=False):
        n = len(word)
        e = b + n
        words = [
            Word(word, word, None, tag, None, n, b, e, is_l)
            for tag in self.get_tags(word)]
        for (m0, t0), (m1, t1) in self.lemmatize(word):
            words.append(Word(word, m0, m1, t0, t1, n, b, e, is_l))
        return words

    def lemmatize(self, word):
        return analyze_morphology(word, self.verbs, self.adjectives, self.eomis, self.rules)


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
        rules = load_rules('%s/resources/demo_morph/rules' % installpath)
        super().__init__(tag_to_morphs, rules)


class BaseMorphemeDictionary(MorphemeDictionary):
    """
    Morpheme dictionary trained from Sejong Corpus
    """

    def __init__(self):
        tag_to_morphs = load_dictionary('%s/resources/base/' % installpath)
        rules = load_rules('%s/resources/base/rules' % installpath)
        super().__init__(tag_to_morphs, rules)

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

def rules_to_strf(rules):
    return ['%s %s %s' % (key, l, r) for key, values in rules.items() for l, r in values]

def load_rules(path):
    rules = defaultdict(lambda: set())
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            columns = line.strip().split()
            if len(columns) != 3:
                print('Exception (%d line) : %s' % (i, line))
                continue
            surface, l, r = columns
            rules[surface].add((l, r))
    rules = {surface:tuple(canons) for surface, canons in rules.items()}
    return rules

def write_rules(rules, path):
    with open(path, 'w', encoding='utf-8') as f:
        for surface, canons in rules.items():
            for l, r in canons:
                f.write('%s %s %s\n' % (surface, l, r))
