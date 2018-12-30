import json
import os

installpath = os.path.sep.join(
    os.path.dirname(os.path.realpath(__file__)).split(os.path.sep)[:-1])

def rules_to_strf(rules):
    def concatenate(l, r):
        return '%s+%s' % (l,r)
    return {key:[concatenate(l,r) for l,r in values] for key, values in rules.items()}

def load_rules(path):
    def parse(lr_list):
        return tuple(tuple(lr.split('+')) for lr in lr_list)

    with open(path, encoding='utf-8') as f:
        rules = json.load(f)
    rules = {k:parse(v) for k,v in rules.items()}
    return rules

def write_rules(rules, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('{\n')
        n = len(rules)
        rules = list(rules.items())
        for key, values in rules[:-1]:
            f.write('  "{}": [{}],\n'.format(key, ','.join(['"%s"' % v for v in values])))
        f.write('  "{}": [{}]\n'.format(rules[-1][0], ','.join(['"%s"' % v for v in rules[-1][1]])))
        f.write('}\n')
