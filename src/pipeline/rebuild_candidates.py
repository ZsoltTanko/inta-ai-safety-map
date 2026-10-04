"""Rebuild the merged candidate list from the discovery workflow's journal."""
import json, re, sys

JOURNAL = sys.argv[1]
OUT = sys.argv[2]

def norm(s):
    s = (s or '').lower()
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'^the\s+', '', s)
    return re.sub(r'[^a-z0-9]', '', s)

def host(u):
    m = re.match(r'^(?:https?://)?(?:www\.)?([^/?#]+)(/[^?#]*)?', (u or '').lower())
    return (m.group(1) + (m.group(2) or '').rstrip('/')) if m else ''

labels, results = {}, []
for line in open(JOURNAL):
    d = json.loads(line)
    if d.get('type') == 'started':
        labels[d['key']] = d.get('label', '')
    if d.get('type') in ('completed', 'result', 'finished') or 'result' in d:
        results.append(d)

merged, by_host, notes, people = {}, {}, {}, {}
for d in results:
    label = labels.get(d.get('key'), d.get('label', ''))
    r = d.get('result')
    if isinstance(r, str):
        try:
            r = json.loads(r)
        except Exception:
            continue
    if not isinstance(r, dict) or 'candidates' not in r:
        continue
    angle = label.split(':', 1)[1] if ':' in label else label
    notes[angle] = r.get('angle_notes', '')
    people[angle] = r.get('notable_people', [])
    for c in r['candidates']:
        k, h = norm(c.get('name')), host(c.get('url'))
        e = merged.get(k) or (by_host.get(h) if h else None)
        if e:
            if angle not in e['found_by']:
                e['found_by'].append(angle)
            e.setdefault('alt_descriptions', []).append({'angle': angle, 'one_line': c.get('one_line'), 'ai_connection': c.get('ai_connection'), 'ring': c.get('ring')})
            for u in c.get('evidence_urls', []):
                if u not in e['evidence_urls']:
                    e['evidence_urls'].append(u)
            continue
        e = dict(c, found_by=[angle])
        merged[k] = e
        if h:
            by_host[h] = e

cands = list(merged.values())
json.dump({'candidates': cands, 'angle_notes': notes, 'notable_people': people}, open(OUT, 'w'), indent=1)
print(len(cands), 'candidates;', len(notes), 'angles')
