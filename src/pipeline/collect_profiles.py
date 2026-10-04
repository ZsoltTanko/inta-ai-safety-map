"""Collect profiles and fact-check verdicts from a profile workflow journal, apply corrections.

Usage: python3 collect_profiles.py JOURNAL [JOURNAL...] > writes profiles_final.json, verify_log.json
Later journals override earlier ones for the same id.
"""
import json, sys, os, copy

D = os.path.dirname(os.path.abspath(__file__))
profiles, verdicts = {}, {}
for J in sys.argv[1:]:
    labels = {}
    for line in open(J):
        d = json.loads(line)
        if d.get('type') == 'started':
            labels[d['key']] = d.get('label', '')
        elif d.get('type') == 'result':
            lab = labels.get(d['key'], '')
            r = d.get('result') or {}
            if lab.startswith('profile') and isinstance(r, dict):
                for p in r.get('profiles', []):
                    profiles[p['id']] = p
            elif lab.startswith('verify') and isinstance(r, dict):
                for v in r.get('verdicts', []):
                    verdicts[v['id']] = v

def apply(p, corr):
    for k, v in corr.items():
        if k.startswith('tags.'):
            p.setdefault('tags', {})[k[5:]] = v
        elif k == 'tags' and isinstance(v, dict):
            p.setdefault('tags', {}).update(v)
        else:
            p[k] = v

log = {'ok': 0, 'corrected': 0, 'reject': 0, 'unverified': 0, 'bad_json': [], 'fields': {}, 'rejected': [], 'notes': {}}
out = []
for pid, p in profiles.items():
    p = copy.deepcopy(p)
    v = verdicts.get(pid)
    if not v:
        log['unverified'] += 1
        p['_verify'] = 'none'
    else:
        log[v['verdict']] = log.get(v['verdict'], 0) + 1
        log['notes'][pid] = v.get('notes', '')
        p['_verify'] = v['verdict']
        if v['verdict'] == 'reject':
            p['include'] = False
            p['exclude_reason'] = 'fact-check: ' + v.get('notes', '')[:300]
            log['rejected'].append((pid, v.get('notes', '')[:300]))
        try:
            corr = json.loads(v.get('corrections') or '{}')
        except Exception:
            corr = {}
            log['bad_json'].append(pid)
        if isinstance(corr, dict) and corr:
            for k in corr:
                log['fields'][k] = log['fields'].get(k, 0) + 1
            apply(p, corr)
    out.append(p)

json.dump(out, open(os.path.join(D, 'profiles_final.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(log, open(os.path.join(D, 'verify_log.json'), 'w'), indent=1, ensure_ascii=False)
inc = sum(1 for p in out if p.get('include', True))
print(f"{len(out)} profiles ({inc} included); verdicts ok={log['ok']} corrected={log['corrected']} reject={log['reject']} unverified={log['unverified']}")
print('most corrected fields:', sorted(log['fields'].items(), key=lambda x: -x[1])[:12])
