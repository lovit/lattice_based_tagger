from lattice_tagger.tagset import *

def _get_default_rules():
    rules = {
        '했': (('하', '았'),),
        '갔': (('가', '았'),),
        '입': (('이', 'ㅂ'),),
        '있': (('이', 'ㅆ'),),
        '였': (('이', '었'),),
        '춥': (('추', 'ㅂ'),),
    }
    return rules

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
            surface_to_canon = _get_default_rules()
        self.surface_to_canon = surface_to_canon

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
