"""Inter-coder agreement for the reliability sample: Cohen's kappa per facet (coder A vs B, and each coder vs the profiler)."""
import json, sys, os, collections
D = os.path.dirname(os.path.abspath(__file__))
J = sys.argv[1]
labels, codes = {}, collections.defaultdict(dict)
for line in open(J):
    d = json.loads(line)
    if d['type'] == 'started':
        labels[d['key']] = d['label']
    elif d['type'] == 'result' and d.get('result'):
        _, n, c = labels[d['key']].split(':')
        for x in d['result'].get('codes', []):
            codes[c][x['id']] = x
prof = {p['id']: p['tags'] for p in json.load(open(os.path.join(D, 'profiles_final.json')))}
ids = [i for i in json.load(open(os.path.join(D, 'qc', 'sample_ids.json'))) if i in codes['A'] and i in codes['B'] and i in prof]

def kappa(a, b):
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, po

def first(v):
    return (v or [''])[0] if isinstance(v, list) else (v or '')

FACETS = [('home tradition', lambda t: first(t.get('tradition'))), ('ring', lambda t: t.get('ring', '')), ('primary problem', lambda t: first(t.get('problems'))),
          ('primary quadrant', lambda t: first(t.get('quadrants'))), ('transfer', lambda t: t.get('transfer', '')), ('framing', lambda t: t.get('framing', '')),
          ('way of knowing', lambda t: t.get('way_of_knowing', '')), ('organisation type', lambda t: t.get('org_type', ''))]
rows = []
for name, f in FACETS:
    a = [f(codes['A'][i]) for i in ids]; b = [f(codes['B'][i]) for i in ids]; p = [f(prof[i]) for i in ids]
    kab, pab = kappa(a, b); kap, pap = kappa(a, p); kbp, pbp = kappa(b, p)
    rows.append({'facet': name, 'kappa_AB': round(kab, 2), 'agree_AB': round(pab, 2), 'kappa_vs_profiler': round((kap + kbp) / 2, 2), 'agree_vs_profiler': round((pap + pbp) / 2, 2)})

def jacc(x, y):
    x, y = set(x or []), set(y or [])
    return len(x & y) / len(x | y) if x | y else 1.0
setrows = []
for name, key in [('all problems (Jaccard)', 'problems'), ('all traditions (Jaccard)', 'tradition'), ('roles (Jaccard)', 'roles')]:
    ab = sum(jacc(codes['A'][i].get(key), codes['B'][i].get(key)) for i in ids) / len(ids)
    vp = sum((jacc(codes['A'][i].get(key), prof[i].get(key)) + jacc(codes['B'][i].get(key), prof[i].get(key))) / 2 for i in ids) / len(ids)
    setrows.append({'facet': name, 'AB': round(ab, 2), 'vs_profiler': round(vp, 2)})
majority = {}
for name, f in FACETS[:2]:
    majority[name] = sum(1 for i in ids if f(prof[i]) in (f(codes['A'][i]), f(codes['B'][i]))) / len(ids)
out = {'n': len(ids), 'facets': rows, 'sets': setrows, 'profiler_matches_at_least_one_coder': {k: round(v, 2) for k, v in majority.items()}}
json.dump(out, open(os.path.join(D, 'qc', 'agreement.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
