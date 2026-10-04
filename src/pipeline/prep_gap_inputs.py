"""Write the inputs the gap-analysis workflow reads: per-sector profile files, a one-line-per-org index, funders, and map statistics."""
import json, os, sys, collections
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import build_map as BM

orgs, _ = BM.from_profiles(os.path.join(D, 'profiles_final.json'))
orgs = [o for o in orgs if o['tr'] and o['tr'][0] in BM.SECTORS]
os.makedirs(os.path.join(D, 'gapin'), exist_ok=True)
chip = {k: {c['key']: c['chip'] for c in BM.V[k]} for k in BM.V}

def compact(o):
    return {k: o[k] for k in ['id', 'n', 'u', 'sum', 'why', 'pp', 'f', 'hq', 'fu', 'se', 'cm', 'en', 'cv', 'tr', 'st', 'r', 'p', 'q', 'ro', 'ot', 'tf', 'fr', 'wk', 'rg', 'sp', 'hb', 'eg', 'ss', 'b', 'gf']} | {'kw': [k[0] + (' (' + k[1] + ')' if k[1] else '') for k in o['kw']]}

for s in BM.SECTORS:
    l = [compact(o) for o in orgs if o['tr'][0] == s]
    json.dump(l, open(os.path.join(D, 'gapin', f'sector-{s}.json'), 'w'), indent=1, ensure_ascii=False)

with open(os.path.join(D, 'gapin', 'index.txt'), 'w') as f:
    f.write('id | name | home>secondary traditions | ring | problems | roles | transfer | region | classic map | status | summary\n')
    for o in orgs:
        f.write(' | '.join([o['id'], o['n'], '>'.join(o['tr']), o['r'], ','.join(o['p']), ','.join(o['ro']), o['tf'], o['rg'], 'MAP' if o['cm'] else '-', o['ss'], o['sum'][:160]]) + '\n')

json.dump([compact(o) for o in orgs if 'fund' in o['ro'] or o['gf']], open(os.path.join(D, 'gapin', 'funders.json'), 'w'), indent=1, ensure_ascii=False)

# statistics
wheel = [o for o in orgs if not o['gf']]
fam_of = {s: f['key'] for f in BM.FAMILIES for s in f['sectors']}
L = []
L.append(f'Total organisations: {len(orgs)} ({len(wheel)} placed in sectors, {len(orgs) - len(wheel)} generalist funders). On the aisafety.com map: {sum(o["cm"] for o in orgs)}.')
L.append('Ring totals: ' + ', '.join(f'{r} {sum(o["r"] == r for o in wheel)}' for r in ['core', 'bridge', 'adjacent', 'potential']))
L.append('\nSector x ring (core/bridge/adjacent/potential | on classic map):')
for s in BM.SECTORS:
    l = [o for o in wheel if o['tr'][0] == s]
    L.append(f'  {s}: ' + '/'.join(str(sum(o['r'] == r for o in l)) for r in ['core', 'bridge', 'adjacent', 'potential']) + f' | {sum(o["cm"] for o in l)} of {len(l)}')
L.append('\nFamily: share on classic map, share core, n')
for fm in BM.FAMILIES:
    l = [o for o in wheel if fam_of[o['tr'][0]] == fm['key']]
    L.append(f'  {fm["label"]}: {round(100 * sum(o["cm"] for o in l) / max(1, len(l)))}% on map, {round(100 * sum(o["r"] == "core" for o in l) / max(1, len(l)))}% core, n={len(l)}')
L.append('\nTransfer by family (counts):')
for fm in BM.FAMILIES:
    l = [o for o in wheel if fam_of[o['tr'][0]] == fm['key']]
    c = collections.Counter(o['tf'] for o in l)
    L.append(f'  {fm["label"]}: ' + ', '.join(f'{k} {v}' for k, v in c.most_common()))
L.append('\nProblem coverage (all values / primary):')
for a in BM.ARCS:
    for p in a['problems']:
        L.append(f'  {p}: {sum(p in o["p"] for o in wheel)} / {sum(o["p"][:1] == [p] for o in wheel)}')
L.append('\nEmpty tradition x problem cells (all values):')
probs = [p for a in BM.ARCS for p in a['problems']]
cnt = collections.Counter((o['tr'][0], p) for o in wheel for p in o['p'])
L.append('  ' + '; '.join(f'{s} x {p}' for s in BM.SECTORS for p in probs if not cnt[(s, p)]))
L.append('\nRegion counts: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(o['rg'] for o in orgs).most_common()))
L.append('Standpoint: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(o['sp'] for o in orgs).most_common()))
L.append('Status: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(o['ss'] for o in orgs).most_common()))
L.append('Framing: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(o['fr'] for o in wheel).most_common()))
L.append('Quadrant (primary): ' + ', '.join(f'{k} {v}' for k, v in collections.Counter((o['q'] or [''])[0] for o in wheel).most_common()))
L.append('Badges: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(b for o in orgs for b in o['b']).most_common()))
L.append('int/a hubs: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(h for o in orgs for h in o['hb']).most_common()))
L.append('Roles: ' + ', '.join(f'{k} {v}' for k, v in collections.Counter(r for o in orgs for r in o['ro']).most_common()))
open(os.path.join(D, 'gapin', 'stats.md'), 'w').write('\n'.join(L))
print('\n'.join(L))
