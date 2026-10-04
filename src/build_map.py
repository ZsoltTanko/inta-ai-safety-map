"""Build the map's data bundle and inject it into map_template.html.

Usage: python3 src/build_map.py [data/profiles.json] [dist/wider-field-map.html]
Pass "-" as the profiles file to build a provisional bundle from the initial roster, for layout testing only.
"""
import json, os, sys, collections

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(D)
DATA = os.path.join(ROOT, 'data')
vocab_all = json.load(open(os.path.join(DATA, 'vocab.json')))
V = vocab_all['vocab']
GEN = set(json.load(open(os.path.join(DATA, 'taxonomy_home.json')))['gen'])

SECTORS = ['safety', 'formal', 'life', 'minds', 'psych', 'contemplative', 'religion', 'philosophy', 'arts', 'indigenous', 'law', 'economics', 'democracy', 'peace']
FAMILIES = [
    {'key': 'sciences', 'label': 'Sciences & engineering', 'sectors': ['safety', 'formal', 'life']},
    {'key': 'inner', 'label': 'Minds & inner life', 'sectors': ['minds', 'psych', 'contemplative', 'religion']},
    {'key': 'humanities', 'label': 'Humanities & cultures', 'sectors': ['philosophy', 'arts', 'indigenous']},
    {'key': 'society', 'label': 'Society & institutions', 'sectors': ['law', 'economics', 'democracy', 'peace']},
]
ARCS = [
    {'key': 'ai', 'label': 'The AI itself', 'problems': ['agency', 'values', 'assurance', 'ai_status']},
    {'key': 'minds', 'label': 'Human minds & meaning', 'problems': ['minds', 'meaning', 'people']},
    {'key': 'together', 'label': 'Living & deciding together', 'problems': ['epistemics', 'democracy', 'justice', 'power']},
    {'key': 'civ', 'label': 'Cooperation, conflict & civilisation', 'problems': ['multi_agent', 'security', 'systemic']},
]
FIELD = {'tradition': 'tr', 'sub_tradition': 'st', 'ring': 'r', 'problems': 'p', 'quadrants': 'q', 'roles': 'ro', 'org_type': 'ot', 'transfer': 'tf', 'framing': 'fr',
         'way_of_knowing': 'wk', 'region': 'rg', 'standpoint': 'sp', 'inta_hubs': 'hb', 'engagement': 'eg', 'status': 'ss', 'badges': 'b'}
VOCAB_OF = {'tradition': 'tradition', 'sub_tradition': 'sub_tradition', 'ring': 'ring', 'problems': 'problem', 'quadrants': 'quadrant', 'roles': 'role', 'org_type': 'org_type',
            'transfer': 'transfer', 'framing': 'framing', 'way_of_knowing': 'way_of_knowing', 'region': 'region', 'standpoint': 'standpoint', 'inta_hubs': 'inta_hub',
            'engagement': 'engagement', 'status': 'status', 'badges': 'badges'}
KEYS = {f: {c['key'] for c in V[v]} for f, v in VOCAB_OF.items()}
LIST_FIELDS = {'tradition', 'problems', 'quadrants', 'roles', 'inta_hubs', 'engagement', 'badges'}


def clean_tags(tags, problems_log, pid):
    out = {}
    for f in FIELD:
        val = tags.get(f)
        if f in LIST_FIELDS:
            vals = val if isinstance(val, list) else ([val] if val else [])
            good = []
            for x in vals:
                if x in KEYS[f] and x not in good:
                    good.append(x)
                elif x:
                    problems_log[f].append((pid, x))
            out[FIELD[f]] = good
        else:
            if val in KEYS[f]:
                out[FIELD[f]] = val
            else:
                if val:
                    problems_log[f].append((pid, val))
                out[FIELD[f]] = ''
    return out


def from_profiles(path):
    profs = json.load(open(path))
    orgs, log = [], collections.defaultdict(list)
    for p in profs:
        if not p.get('include', True):
            continue
        t = clean_tags(p.get('tags', {}), log, p['id'])
        o = {
            'id': p['id'], 'n': p['name'], 's': p.get('short_name') or p['name'], 'u': p.get('url', ''),
            'sum': p.get('summary', ''), 'why': p.get('why_it_matters', ''),
            'kw': [[k.get('title', ''), k.get('year', ''), k.get('url', '')] for k in p.get('key_work', []) if k.get('title')],
            'pp': p.get('people', []), 'f': p.get('founded', ''), 'hq': p.get('hq', ''), 'sc': p.get('scale', ''),
            'fu': p.get('funding', ''), 'se': p.get('status_evidence', ''), 'cm': bool(p.get('on_classic_map')),
            'en': p.get('engage', []), 'cv': p.get('caveats', ''), 'src': p.get('sources', []), 'cf': p.get('confidence', ''),
            'gf': p['id'] in GEN,
        }
        o.update(t)
        orgs.append(o)
    return orgs, log


def provisional():
    roster = json.load(open(os.path.join(ROOT, 'research', 'roster_initial.json')))
    home = json.load(open(os.path.join(DATA, 'taxonomy_home.json')))['home']
    arcmap = {'formal': 'agency', 'life': 'agency', 'minds': 'ai_status', 'psych': 'minds', 'contemplative': 'values', 'religion': 'meaning', 'philosophy': 'values',
              'arts': 'epistemics', 'indigenous': 'justice', 'law': 'justice', 'economics': 'power', 'democracy': 'democracy', 'peace': 'security', 'safety': 'assurance'}
    orgs = []
    for c in roster:
        h = home.get(c['id'], 'law')
        orgs.append({'id': c['id'], 'n': c['name'], 's': c['name'][:24], 'u': c['url'], 'sum': c['one_line'], 'why': c.get('ai_connection', ''), 'kw': [], 'pp': [],
                     'f': '', 'hq': c.get('location', ''), 'sc': '', 'fu': '', 'se': '', 'cm': bool(c.get('on_classic_map')), 'en': [], 'cv': '', 'src': c.get('evidence_urls', [])[:3],
                     'cf': c.get('confidence', ''), 'gf': c['id'] in GEN, 'tr': [h], 'st': '', 'r': c['ring'], 'p': [arcmap[h]], 'q': [], 'ro': [], 'ot': '', 'tf': '', 'fr': '',
                     'wk': '', 'rg': '', 'sp': '', 'hb': [], 'eg': [], 'ss': 'active', 'b': []})
    return orgs, {}


def stats(orgs):
    wheel = [o for o in orgs if not o['gf']]
    fam_of = {s: f['key'] for f in FAMILIES for s in f['sectors']}
    out = []
    n, cm = len(orgs), sum(o['cm'] for o in orgs)
    out.append({'value': str(n), 'text': f'organisations across 14 traditions. Only {cm} of them ({round(100 * cm / n)}%) are on the aisafety.com field map.'})
    share = {}
    for f in FAMILIES:
        l = [o for o in wheel if fam_of.get(o['tr'][0]) == f['key']]
        share[f['key']] = (round(100 * sum(o['cm'] for o in l) / max(1, len(l))), len(l))
    lo = min(share, key=lambda k: share[k][0]); hi = max(share, key=lambda k: share[k][0])
    lab = {f['key']: f['label'] for f in FAMILIES}
    out.append({'value': f'{share[lo][0]}%', 'text': f'of {lab[lo]} entries appear on the classic map, against {share[hi][0]}% of {lab[hi]}.'})
    nocore = [s for s in SECTORS if not any(o['tr'][0] == s and o['r'] == 'core' for o in wheel)]
    if nocore:
        names = {c['key']: c['chip'] for c in V['tradition']}
        out.append({'value': str(len(nocore)), 'text': 'traditions have no core AI-safety organisation at all: ' + ', '.join(names[s] for s in nocore) + '.'})
    newc = sum(1 for o in orgs if o.get('ss') == 'new')
    if newc:
        out.append({'value': str(newc), 'text': 'entries launched in 2025 or 2026; the field is still forming.'})
    na = sum(1 for o in orgs if o.get('rg') in ('north_america', 'uk_ireland'))
    if na:
        out.append({'value': f'{round(100 * na / n)}%', 'text': 'are based in North America or the UK and Ireland. Treat thin regions as a limit of the search as much as of the world.'})
    return out


PERSONAS = [
    {'key': 'funder', 'label': 'AI-safety funder', 'question': 'What relevant knowledge are my grantees not using?',
     'how': 'Entries already on the aisafety.com map are hidden, so the wheel shows what the classic map leaves out. Open the Matrix to see which traditions work on the problems you already fund.',
     'notOnMap': True, 'view': 'wheel'},
    {'key': 'newfunder', 'label': 'New funder', 'question': 'Where could money open something untried, and who could I fund with?',
     'how': 'The openings written for funders, each with the part of the map it would fill and who already works nearby. Funders and fellowships are under "What it does: Fund".',
     'view': 'openings', 'opKind': 'funder'},
    {'key': 'founder', 'label': 'Founder', 'question': 'Which niches are empty, and who could I build with?',
     'how': 'The matrix crosses what organisations bring (rows) with what they work on (columns). Small dots mark empty cells. The Openings tab lists the most promising ones.',
     'view': 'matrix', 'opKind': 'founder'},
    {'key': 'field', 'label': 'From another field', 'question': 'Who in my field already works on AI going well, and how do I get in?',
     'how': 'Showing entries with fellowships, courses, events or open communities. Pick your tradition in the filters, or click its name on the wheel to see the whole sector.',
     'filters': {'eg': ['fellowships', 'courses', 'events', 'community']}, 'view': 'wheel'},
    {'key': 'insider', 'label': 'AI-safety insider', 'question': 'What is in my blind spot on the problems I already work on?',
     'how': 'Work on the AI itself (agency, values, assurance, moral status) from outside the core rings. Colour shows what flows where: which traditions already reach the models.',
     'filters': {'p': ['agency', 'values', 'assurance', 'ai_status'], 'r': ['bridge', 'adjacent', 'potential']}, 'layer': 'transfer', 'view': 'wheel'},
    {'key': 'inta', 'label': 'int/a member', 'question': 'Who near me works in this milieu, and where could int/a add something?',
     'how': 'Organisations active in London, Berlin or Paris, or joinable online. Colour shows the integral quadrant each attends to. The Openings tab has a filter for int/a.',
     'filters': {'hb': ['london', 'berlin', 'paris', 'online']}, 'layer': 'quadrant', 'view': 'wheel', 'opKind': 'inta'},
]


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, 'profiles.json')
    prof = None if arg == '-' else arg
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'dist', 'wider-field-map.html')
    orgs, log = from_profiles(prof) if prof else provisional()
    for o in orgs:
        if not o['tr'] or o['tr'][0] not in SECTORS:
            print('WARN no valid home', o['id'], o['tr'])
    extra = {}
    ep = os.path.join(DATA, 'map_extra.json')
    if os.path.exists(ep):
        extra = json.load(open(ep))
    guide = extra.get('guide') or {
        'title': 'About The Wider Field', 'intro': ['Draft.'], 'read': ['Draft.'], 'method': ['Draft.'], 'limits': ['Draft.'],
        'panelTitle': 'A map of AI safety beyond its usual borders', 'panelIntro': 'Draft.', 'compiled': 'Compiled October 2026.'}
    vocab_ui = {k: [{'key': c['key'], 'label': c['label'], 'chip': c['chip'], 'definition': c['definition']} for c in V[k]] for k in V}
    data = {
        'orgs': orgs, 'vocab': vocab_ui, 'sectorOrder': SECTORS, 'families': FAMILIES, 'arcs': ARCS, 'personas': PERSONAS,
        'stats': stats(orgs), 'guide': guide, 'gaps': extra.get('gaps', []), 'sectorNotes': extra.get('sectorNotes', {}),
        'cellNotes': extra.get('cellNotes', {}), 'askExamples': extra.get('askExamples', [
            'Who in Europe works on care-based or compassion-based alignment?',
            'Which organisations bring contemplative practice to people who build AI?',
            'Who could help a funder support psychological safety for AI-safety researchers?',
            'What is happening on AI and religion in the Global South?']),
        'reportNote': extra.get('reportNote', ''), 'reportUrl': extra.get('reportUrl', ''),
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    tpl = open(os.path.join(D, 'map_template.html')).read()
    open(out, 'w').write(tpl.replace('__DATA__', blob))
    print(f'{len(orgs)} orgs, {len(blob) // 1024} KB data ->', out)
    if log:
        for f, items in log.items():
            print('invalid', f, len(items), items[:6])


if __name__ == '__main__':
    main()
