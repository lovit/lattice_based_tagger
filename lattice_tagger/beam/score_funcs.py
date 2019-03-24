from ..tagset import *

def trigram_beam_score(seq, word_k, **kargs):
    base_score = seq.score
    if len(seq.sequences) == 1:
        word_i = None
    else:
        word_i = seq.sequences[-2]
    word_j = seq.sequences[-1]

    # TODO
    # featurize

    # cumulate feature coefficient
    score_increment = 0

    return score_increment

def penalty(seq, word_k, **kargs):
    if word_k.tag0 == Unk:
        return kargs.get('unknown_penalty', 0)
    return 0.001
    # return 0
