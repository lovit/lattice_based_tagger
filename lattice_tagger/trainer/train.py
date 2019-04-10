def train(word_morph_pairs, dictionary, encoder, score_func, regularity_func,
          max_epochs=100, min_feature_count=1, predefined_features=None,
          verbose=False, debug=False):

    # scan feature
    if verbose:
        print('Scanning features ...')

    if predefined_features is None:
        # length unknown word feature (feature class 6)
        # default 1 - 8 (longer than 8 -> use 8)
        predefined_features = {(6, len_):min_feature_count for len_ in range(1, 9)}

    idx_to_feature, feature_to_idx, idx_to_feature_count = scan_features(
        word_morph_pairs, encoder, min_count=min_feature_count, verbose=verbose,
        debug=debug, predefined_features=predefined_features)

    # prepare encoder & score
    encoder.feature_dic = feature_to_idx
    funcs = BeamScoreFunctions(
        regularity_func,
        score_func.set_encoder(encoder)
    )

    tagger = Tagger(dictionary, encoder=encoder, score_funcs=funcs)

    # fit model
    if verbose:
        print('Estimating parameter ...')

    coef = fit_parameter(word_morph_pairs, encoder, tagger, max_epochs)

    # wrap-up trained parameters
    params = {
        'idx_to_feature': idx_to_feature,
        'coefficient': coef
    }

    if debug:
        params['idx_to_feature_count'] = idx_to_feature_count

    return params

def fit_parameter(word_morph_pairs, encoder, tagger, max_epochs=100, verbose=False):

    # initialize
    num_features = len(encoder.feature_dic)
    coef = [0] * num_features

    # prepare tagger
    # tagger = Tagger()

    # iteration
    for epoch in range(1, max_epochs + 1):
        coef, loss = train_epoch(word_morph_pairs, encoder, tagger, coef, epoch, verbose)
        print(epoch)
        continue

    return coef

def train_epoch(word_morph_pairs, encoder, tagger, coef, epoch, verbose):

    # TODO
    loss = 0
    return coef, loss
