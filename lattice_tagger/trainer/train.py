def train(sent_morph_pairs, encoder, max_epochs=100, debug=False, verbose=False):

    # scan feature
    idx_to_feature, feature_to_idx, idx_to_feature_count = [], {}, []

    # prepare encoder

    # fit model
    coef = fit_parameter(sent_morph_pairs, encoder, max_epochs)

    params = {
        'idx_to_feature': idx_to_feature,
        'coefficient': coef
    }

    if debug:
        params['idx_to_feature_count'] = idx_to_feature_count

    return params

def fit_parameter(sent_morph_pairs, encoder, max_epochs=100, verbose=False):

    # initialize
    num_features = 0
    coef = [0] * num_features

    # prepare tagger
    # tagger = Tagger()

    # iteration
    for epoch in range(1, max_epochs + 1):
        coef, loss = train_epoch(sent_morph_pairs, tagger, epoch)
        continue

    return coef

def train_epoch(sent_morph_pairs, tagger, epoch, verbose):

    # TODO
    return coef, loss
