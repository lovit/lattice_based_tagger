from collections import Counter


def scan_features(feature_seqs, min_count=1):
    """
    >>> idx_to_feature, feature_to_idx, idx_to_count = scan_features(
            seqs, min_count)
    """
    counter = Counter(
        feature for seq in feature_seqs
        for features in seq for feature in features)
    counter = {k:v for k,v in counter.items() if v >= min_count}
    idx_to_feature = [feature for feature, _ in sorted(
        counter.items(), key=lambda x:(x[0][0], -x[1]))]
    idx_to_count = [counter[f] for f in idx_to_feature]
    feature_to_idx = {feature:idx for idx, feature in enumerate(idx_to_feature)}

    return idx_to_feature, feature_to_idx, idx_to_count
