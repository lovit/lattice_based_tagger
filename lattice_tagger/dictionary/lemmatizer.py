# transplanted from github.com/lovit/korean_lemmatizer
from ..tagset import Adjective, Verb, Eomi


def analyze_morphology(word, verbs, adjectives, eomis, lemma_rules, debug=False):
    """
    Arguments
    ---------
    word : str
        A word to analyze its morphology
    verbs : set of str
        Verb dictionary
    adjectives : set of str
        Adjective dictionary
    eomis : set of str
        Eomi dictionary
    lemma_rules : dict of tuple
        Lemmatization rules
    debug : Boolean
        If True, it prints all candidates

    Returns
    -------
    morphs : list of tuple
        For example,
            word = '파랬던'
            morphs = [(('파랗', 'Adjective'), ('았던', 'Eomi'))]
        Dictionary checked list of (stem, eomi)
    Function get_lemma_candidates returns set of (stem, eomi) candidates.
    This function checks whether the stem and eomi is known words using dictionaries.

    Usage
    -----
        >>> rules = {'랬':(('랗', '았'), )}
        >>> adjectives = {'파랗'}
        >>> verbs = {}
        >>> eomis = {'았다'}
        >>> word = '파랬다'
        >>> analyze_morphology(word, verbs, adjectives, eomis, rules)
        $ [(('파랗', 'Adjective'), ('았다', 'Eomi'))]
    """

    morphs = []
    for stem, eomi in get_lemma_candidates(word, lemma_rules, debug):
        if not (eomi in eomis):
            continue
        if stem in adjectives:
            morphs.append(((stem, Adjective), (eomi, Eomi)))
        if stem in verbs:
            morphs.append(((stem, Verb), (eomi, Eomi)))
    return morphs

def get_lemma_candidates(word, rules, debug=False):
    """
    Arguments
    ---------
    word : str
        A word to analyze its morphology
    rules : dict of tuple
        Lemmatization rules
    Returns
    -------
    morphs : list of tuple
        All possible subword combination satisfying lemmatization rules
    용언이 활용되는 지점은 어간과 어미가 만나는 지점으로, 표현형 (surfacial form) 에서
    활용이 되는 지점의 길이에 따라 모든 경우를 확인한다.
    # 1 음절만 활용되는 경우
    - `했 = 하 + 았`
        - 시작했으니까 = 시작하 + 았으니까
    - `랬 = 랗 + 았`
        - 파랬던 = 파랗 + 았던
    # 2 음절만 활용되는 경우
    - `추운 = 춥 + 은`
        - 추운데 = 춥 + 은데
    - `했다 = 하 + 았다`
        - 시작했다 = 시작하 + 았다
    # 3 음절만 활용되는 경우
    - `가우니 = 갑 + 니`
        - 차가우니까 = 차갑 + 니까
    Debug mode 에서는 단어의 활용 지점과 단어의 어간, 어미 조합 후보를 출력한다.
        >>> lemmatizer = Lemmatizer(dictionary_name='demo')
        >>> lemmatizer.analyze('파랬다', debug=True)
        $ [DEBUG] word: 파랬다 = 파랗 + 았다, conjugation: 랬 = 랗 + 았
    """

    def debug_on(word, l, stem, eomi, r, conj):
        args = (word, l+stem, eomi+r, conj, stem, eomi)
        print('[DEBUG] word: {} = {} + {}, conjugation: {} = {} + {}'.format(*args))

    max_i = len(word) - 1
    candidates = []
    for i, c in enumerate(word):
        l = word[:i+1]
        r = word[i+1:]
        l_ = word[:i]
        if i < max_i:
            candidates.append((l, r))

        # 1 syllable conjugation
        for stem, eomi in rules.get(c, {}):
            for stem, eomi in rules.get(c, {}):
                candidates.append((l_ + stem, eomi + r))
                if debug:
                    debug_on(word, l_, stem, eomi, r, c)

        # 2 or 3 syllables conjugation
        for conj in {word[i:i+2], word[i:i+3]}:
            for stem, eomi in rules.get(conj, {}):
                candidates.append((l_ + stem, eomi + r[1:]))
                if debug:
                    debug_on(word, l_, stem, eomi, r[1:], conj)
    return candidates