from collections import defaultdict
from lattice_tagger import get_process_memory
from lattice_tagger import left_space_tag
from lattice_tagger.dictionary import text_to_words
from lattice_tagger.dictionary import flatten_words



def scan_features(word_morph_pairs, encoder, min_count=1, predefined_features=None,
    verbose=False, debug=False, flatten=False):

    """
        >>> idx_to_feature, feature_to_idx, idx_to_count = scan_features(sent_morph_pairs, encoder, min_count)
    """

    if predefined_features is None:
        predefined_features = {}

    counter = defaultdict(int, predefined_features)
    for i, (word_text, morph_text) in enumerate(word_morph_pairs):
        if verbose and i % 1000 == 0:
            mem = get_process_memory()
            num = len(counter)
            print('\rscanning {} th pairs ... mem = {:.3} GB, {} features'.format(i, mem, num), end='')
        try:
            words = text_to_words(word_text, morph_text)
            if flatten:
                words = flatten_words(words)
            feature_seq = encoder.transform_sequence(words)
            for features in feature_seq:
                for feature in features:
                    counter[feature] += 1
        except Exception as e:
            if debug:
                print()
                print(e)
                print('{} th pair'.format(i))
                print('word_text : {}'.format(word_text))
                print('morph_text : {}'.format(morph_text), end='\n\n')
            continue

    # frequency filtering
    counter = {k:v for k,v in counter.items() if v >= min_count}

    if verbose:
        mem = get_process_memory()
        num = len(counter)
        print('\rscanning from {} pairs. mem = {:.3} GB, {} features'.format(i+1, mem, num))

    idx_to_feature = [feature for feature, _ in sorted(
        counter.items(), key=lambda x:(x[0][0], -x[1], x[0][1]))]
    idx_to_count = [counter[f] for f in idx_to_feature]
    feature_to_idx = {feature:idx for idx, feature in enumerate(idx_to_feature)}

    return idx_to_feature, feature_to_idx, idx_to_count

def scan_dictionary(word_morph_pairs, min_count=1):
    """
        >>> tag_to_morphs, counter = scan_dictionary(word_morph_pairs, min_count)
    """
    counter = defaultdict(int)
    for _, morph_text in word_morph_pairs:
        morphs = [morph.strip() for eojeol in morph_text.split() for morph in eojeol.split('+')]
        for morph in morphs:
            if len(morph) < 3:
                continue
            counter[morph] += 1
    counter = {k:v for k,v in counter.items() if v >= min_count}
    counter = {tuple(k.split('/',1)):v for k,v in counter.items()}
    tag_to_morphs = defaultdict(lambda: set())
    for morph, tag in counter:
        tag_to_morphs[tag].add(morph)
    return dict(tag_to_morphs), counter
