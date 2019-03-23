from collections import defaultdict
from lattice_tagger.utils import get_process_memory
from lattice_tagger.utils import text_to_words
from lattice_tagger.utils import flatten_words
from lattice_tagger.utils import left_space_tag


def scan_features(sent_morph_pairs, encoder, min_count=1, verbose=False, debug=False):
    """
    >>> idx_to_feature, feature_to_idx, idx_to_count = scan_features(sent_morph_pairs, encoder, min_count)
    """
    counter = defaultdict(int)
    for i, (sent, morph_text) in enumerate(sent_morph_pairs):
        if verbose and i % 1000 == 0:
            mem = get_process_memory()
            num = len(counter)
            print('\rscanning {} th pairs ... mem = {:.3} GB, {} features'.format(i, mem, num), end='')
        try:
            words = flatten_words(text_to_words(sent, morph_text))
            chars, is_l_tag = left_space_tag(sent)
            feature_seq = encoder.transform(words, is_l_tag)
            for features in feature_seq:
                for feature in features:
                    counter[feature] += 1
        except Exception as e:
            if debug:
                print()
                print(e)
                print('{} th pair'.format(i))
                print('sent : {}'.format(sent))
                print('morph_text : {}'.format(morph_text), end='\n\n')
            continue

    # frequency filtering
    counter = {k:v for k,v in counter.items() if v >= min_count}

    if verbose:
        mem = get_process_memory()
        num = len(counter)
        print('\rscanning from {} pairs. mem = {:.3} GB, {} features'.format(i+1, mem, num))

    idx_to_feature, feature_to_idx, idx_to_count = indexing(counter)
    return idx_to_feature, feature_to_idx, idx_to_count

def indexing(counter):
    idx_to_item = [feature for feature, _ in sorted(
        counter.items(), key=lambda x:(x[0][0], -x[1]))]
    idx_to_count = [counter[f] for f in idx_to_item]
    item_to_idx = {feature:idx for idx, feature in enumerate(idx_to_item)}
    return idx_to_item, item_to_idx, idx_to_count

def scan_dictionary(sent_morph_pairs, min_count=1):
    counter = defaultdict(int)
    for _, morph_text in sent_morph_pairs:
        morphs = [morph for eojeol in morph_text.split() for morph in eojeol.split('+')]
        for morph in morphs:
            counter[morph] += 1
    counter = {k:v for k,v in counter.items() if v >= min_count}
    counter = {tuple(k.split('/',1)):v for k,v in counter.items()}
    tag_to_morphs = defaultdict(lambda: set())
    for morph, tag in counter:
        tag_to_morphs[tag].add(morph)
    return dict(tag_to_morphs), counter
