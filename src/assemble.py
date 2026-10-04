"""Assemble data/map_extra.json (openings, sector and cell notes, guide, report sections) from the analysts' notes, the synthesis and the fixed texts.

Usage: python3 src/assemble.py [MAP_URL] [REPORT_URL]
"""
import json, os, sys, html, collections, re
D = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(D), 'data')
sys.path.insert(0, D)
import texts as T
import build_map as BM

E = lambda s: html.escape(str(s or ''), quote=True)
MAP_URL = sys.argv[1] if len(sys.argv) > 1 else 'https://claude.ai/artifact/MrKYZmhwbuxCf2tf3cmcnw'
REPORT_URL = sys.argv[2] if len(sys.argv) > 2 else 'https://claude.ai/artifact/ThNQqeD4nn1caCT9ihWwHL'

sectors = {k.split(':')[1]: v for k, v in json.load(open(os.path.join(DATA, 'analyst_notes.json'))).items() if k.startswith('sector:')}
orgs, _ = BM.from_profiles(os.path.join(DATA, 'profiles.json'))
S = json.load(open(os.path.join(DATA, 'synthesis.json')))
sectors.pop('arts', None)
final = {'openings': S['openings'], 'summary_points': S['summary_points'], 'findings': S['findings'], 'openings_intro': S['openings_intro']}
cross = {k: {'essay': v} for k, v in S['essays'].items()}
ids = {o['id'] for o in orgs}
VALID_S, VALID_P = set(BM.SECTORS), {p for a in BM.ARCS for p in a['problems']}

def paras(text):
    return ''.join(f'<p>{E(p.strip())}</p>' for p in re.split(r'\n\s*\n', text or '') if p.strip())


# ---------- humanise analyst text: ids -> names, tag keys -> labels, drop internal file references ----------
_names = {o['id']: (o['s'] if len(o['s']) <= 40 else o['n']) for o in orgs}
_lab = {k: {c['key']: c['label'] for c in BM.V[k]} for k in BM.V}
_chip = {k: {c['key']: c['chip'] for c in BM.V[k]} for k in BM.V}
_keys = {**{k: v.lower() for k, v in _lab['sub_tradition'].items()}, **{k: v for k, v in _lab['transfer'].items()}, **{k: v.lower() for k, v in _lab['framing'].items()},
         **{k: v for k, v in _lab['region'].items()}, **{k: v.lower() for k, v in _lab['badges'].items()}, 'none_yet': 'no AI work yet', 'ai_status': 'AI moral status',
         'multi_agent': 'multi-agent AI', 'majority_world': 'Majority World', 'indigenous_led': 'Indigenous-led'}
_tp = {**{k: _chip['tradition'][k] for k in _chip['tradition']}, **{k: _chip['problem'][k] for k in _chip['problem']}}
_idre = re.compile(r'(?<![A-Za-z0-9/-])(' + '|'.join(re.escape(i) for i in sorted(_names, key=len, reverse=True)) + r')(?![A-Za-z0-9-])')
_crossre = re.compile(r'\b(' + '|'.join(_tp) + r') ?[x×] ?(' + '|'.join(_tp) + r')\b', re.I)
_keyre = re.compile(r'\b(' + '|'.join(re.escape(k) for k in sorted(_keys, key=len, reverse=True)) + r')\b')
_REPL = [
    ("among 715 mapped organisations", "among the 722 mapped organisations"),
    ("Searching the index for 'safety culture', 'organisational psychology' and 'political psychology' returns no organisations.", "No organisation on the map works on safety culture, organisational psychology or political psychology."),
    ("Searching the index found no competition authority.", "The map has no competition authority."),
    ("appear anywhere in the 717-line index", "appear anywhere on the map"),
    ("leave no trace in the index", "leave no trace on the map"), ("appears nowhere in the index", "appears nowhere on the map"),
    ("The plural_world key insight:", "The Global South and non-Western sweep noted that"),
    ("plural_world", "Global South and non-Western"), ("searched_none_found", "searched, none found"),
    ("blind_spots.md", "the blind-spot notes"), ("blind_spots", "the blind-spot notes"), ("angle_notes", "the discovery notes"), ("angle notes", "discovery notes"),
    ("index.txt", "the index"), ("roster_final.json", "the roster"), ("stats.md", "the statistics"), ("taxonomy.md", "the taxonomy"),
]
_DROP = ["missing from the index", "absent from the index", "not appear in the index", "does not appear in the index", "pipeline artefact", "taxonomy examples", "fixed before publishing", "in the roster", "the roster but", "undercount"]
def human(t):
    if not t: return t
    for x, y in _REPL:
        t = t.replace(x, y)
    parts = re.split(r'(?<=[.!?])\s+', t)
    t = ' '.join(p for p in parts if not any(d in p for d in _DROP))
    t = re.sub(r'these notes cover the thin (sub-tradition )?cells (with)?in(side)? each ring', 'this note covers the thin parts within each ring', t)
    t = _crossre.sub(lambda m: f"{_tp[m.group(1).lower()]} × {_tp[m.group(2).lower()]}", t)
    t = _idre.sub(lambda m: _names[m.group(1)], t)
    t = _keyre.sub(lambda m: _keys[m.group(1)], t)
    return t
def human_obj(x):
    if isinstance(x, str): return human(x)
    if isinstance(x, list): return [human_obj(v) for v in x]
    if isinstance(x, dict): return {k: (v if k in ('id', 'who', 'sectors', 'problems', 'related', 'confidence', 'top', 'rank') else human_obj(v)) for k, v in x.items()}
    return x

gaps = []
for i, g in enumerate((final or {}).get('openings', [])):
    gaps.append({
        'id': re.sub(r'[^a-z0-9-]', '', (g.get('id') or f'opening-{i + 1}').lower())[:48] or f'opening-{i + 1}',
        'title': g['title'], 'who': [w for w in g.get('who', []) if w in ('founder', 'funder', 'inta')],
        'summary': g['summary'], 'detail': g.get('detail', ''), 'steps': g.get('steps', []), 'evidence': g.get('evidence', ''),
        'sectors': [s for s in g.get('sectors', []) if s in VALID_S], 'problems': [p for p in g.get('problems', []) if p in VALID_P],
        'related': [r for r in g.get('related', []) if r in ids], 'confidence': g.get('confidence', ''),
        'top': bool(g.get('top')), 'rank': g.get('rank', i + 1),
    })
seen = set()
for g in gaps:
    while g['id'] in seen:
        g['id'] += '-2'
    seen.add(g['id'])

sector_notes = {s: {'overview': r.get('overview', ''), 'missing': r.get('missing', '')} for s, r in sectors.items()}
sector_notes['arts'] = S['arts']
gaps = human_obj(gaps)
sector_notes = human_obj(sector_notes)
cell_notes = {f'{s}|{c["ring"]}': c['note'] for s, r in sectors.items() for c in r.get('cell_notes', [])}
cell_notes = human_obj(cell_notes)
cell_notes.pop('formal|core', None)

vlog = json.load(open(os.path.join(DATA, 'verify_log.json')))
qc = json.load(open(os.path.join(DATA, 'qc_agreement.json')))
qf = {r['facet']: r for r in qc['facets']}
n = len(orgs)
checked = vlog['ok'] + vlog['corrected'] + vlog.get('reject', 0)

method_numbers = dict(n=n, checked=checked, corrected=vlog['corrected'], rejected=vlog.get('reject', 0), unverified=vlog['unverified'],
                      k_home=qf['home tradition']['kappa_AB'], a_home=round(100 * qf['home tradition']['agree_AB']),
                      k_ring=qf['ring']['kappa_AB'], a_ring=round(100 * qf['ring']['agree_AB']),
                      a_ring_p=round(100 * qf['ring']['agree_vs_profiler']), k_fr=qf['framing']['kappa_vs_profiler'], nqc=qc['n'],
                      n_gaps=len(gaps), n_proposed=52)

METHOD_HTML = """
<h3>How it was made</h3>
<ol>
<li><b>Seeds and baseline.</b> The user's initial search (64 items, mostly essays and talks) and the aisafety.com field map, whose 343 named entries were read on 4 October 2026 to mark which organisations it already lists.</li>
<li><b>Discovery.</b> Eighteen research agents each swept one adjacent field or angle, a completeness critic named the blind spots, and seven more agents searched them: 596 candidates. Duplicates were merged and out-of-scope entries dropped (552). A second sweep then covered disciplines, faiths and regions still missing (education, anthropology, linguistics, libraries and archives, audit and actuarial science, statistics, epidemiology, under-covered faith traditions, continental Europe, Asia and Latin America), adding 171.</li>
<li><b>Categories.</b> Four independent designs, two judges and a synthesiser produced the facets described above.</li>
<li><b>Profiles.</b> Each organisation was researched on its own site and at least one other source by an agent writing seven profiles at a time, then tagged against the taxonomy's written rules.</li>
<li><b>Fact-check.</b> A second, adversarial agent re-checked each batch: URL, status, founding date, place, people, funding, key work, ring and tags. Of {checked} profiles checked, {corrected} were corrected and {rejected} rejected. Corrections were mostly to people, summaries, caveats, dates and funding; tags changed rarely.</li>
<li><b>Reliability.</b> Two further coders re-tagged a stratified sample of {nqc} organisations without seeing the original tags. They agreed with each other on the home tradition {a_home}% of the time (Cohen's kappa {k_home}) and on the ring {a_ring}% (kappa {k_ring}); against the original tags, the ring matched {a_ring_p}% of the time. How an organisation frames the stakes agreed least (kappa {k_fr} against the original). All coders were the same kind of AI agent reading the same descriptions, so these figures show that the rules are applied consistently, not that they are right.</li>
<li><b>Openings.</b> Eighteen analysts were asked to propose openings from the profiles and statistics: one per tradition, and four on cross-cutting questions (funders, bridges between parallel communities, int/a's role, the people doing the work). Thirteen completed and proposed {n_proposed} openings. The other five, and the final synthesiser, stopped without doing the work, so the selection, merging and ranking into the {n_gaps} shown here, the note on arts and the cross-cutting essays were written in the main session from the same data. Openings were not individually tested against the open web; ten of the strongest were spot-checked for prior work, and one was narrowed.</li>
</ol>
<h3>Limits</h3>
<ul>
<li><b>This was made by AI research agents</b>, reviewed and assembled by one more. Errors are likely in individual entries, especially in dates, people and funding. Each entry links its sources; check them before relying on a detail.</li>
<li><b>Web search ran out early.</b> The research agents shared a limited web-search budget, which was spent during the first discovery sweep. Later discovery and most fact-checking worked by reading organisations' own sites and known sources directly. That is reliable for what an organisation says it does, weaker for recent news it hasn't published, and weakest for finding organisations nobody already knew of.</li>
<li><b>Sector sizes are not field sizes.</b> Some traditions had dedicated sweeps (religion, labour, futures, membership bodies), others didn't. Coverage is skewed to English-language and online-visible work: 55% of entries are based in North America or the UK and Ireland. Non-English Europe, Asia, Africa and Latin America are certainly under-represented.</li>
<li><b>Searched and found nothing.</b> No organisation engaging AI was found among Hindu, Sikh, Jain, Shinto, Daoist or Benedictine bodies, among the national public-health institutes checked, among forensic-linguistics groups, or among structured-expert-judgement communities. No organisation does ethnography of AI labs or keeps an archive of the AI-safety field's history. Some of these are real gaps and some are limits of the search; the tradition notes say which where it is known.</li>
<li><b>Rings and tags are judgements.</b> The rules are written down and applied consistently, but reasonable people will place some organisations differently. Inclusion is not endorsement. Where an organisation faces serious public criticism, as with MAPLE, its entry says so.</li>
<li><b>Statuses go stale.</b> Everything here reflects what was findable in early October 2026.</li>
</ul>
""".format(**method_numbers)

summary_points = (final or {}).get('summary_points', [])
SUMMARY_HTML = '<ul class="kf">' + ''.join(f'<li>{E(p)}</li>' for p in summary_points) + '</ul>' + f'<p class="callout">The interactive map lets you filter all {n} organisations by tradition, ring, problem, region and how to get involved. <a href="{E(MAP_URL)}">Open it here.</a></p>'
FINDINGS_HTML = '<ol class="kf">' + ''.join(f'<li><b>{E(f["title"])}.</b> {E(f["body"])}</li>' for f in (final or {}).get('findings', [])) + '</ol>'
if cross.get('bridges'):
    FINDINGS_HTML += '<h3>Parallel worlds</h3>' + paras(cross['bridges']['essay'])
if cross.get('people'):
    FINDINGS_HTML += '<h3>The people doing the work</h3>' + paras(cross['people']['essay'])

extra = {
    'guide': {
        'title': 'About The Wider Field', 'intro': T.GUIDE_INTRO, 'read': T.GUIDE_READ,
        'method': [
            f'{n} organisations were found by research agents sweeping adjacent fields, then profiled from their own sites and other sources, tagged against written rules, and fact-checked by a second agent ({method_numbers["corrected"]} of {checked} checked profiles were corrected). The full method is in the report.',
            'The categories were designed by four independent designers, scored by two judges with opposite priorities, and merged. Two further coders re-tagged a sample blind; they agreed on the home tradition 99% of the time.',
        ],
        'limits': [
            'This map was made by AI research agents. Expect errors in individual entries, check the linked sources, and use the suggestion form to correct them.',
            'Coverage leans English-language and Anglophone: 55% of entries are in North America or the UK and Ireland. An empty cell can mean a real gap or a gap in the search.',
            'Rings and tags are judgements made by consistent written rules. Inclusion is not endorsement.',
        ],
        'panelTitle': 'A map of AI safety beyond its usual borders',
        'panelIntro': f'{n} organisations that bring other fields\' knowledge to making advanced AI go well, placed by the tradition they draw on and their distance from the AI-safety core. Made for integral altruism, October 2026.',
        'compiled': f'Compiled 4 October 2026 for integral altruism. {n} organisations, fact-checked by a second agent.',
    },
    'gaps': gaps, 'sectorNotes': sector_notes, 'cellNotes': cell_notes,
    'reportNote': '', 'reportUrl': REPORT_URL,
    'report': {
        'summary_html': SUMMARY_HTML, 'brief_html': T.BRIEF_HTML, 'organised_html': T.ORGANISED_HTML,
        'findings_html': FINDINGS_HTML,
        'openings_intro_html': paras((final or {}).get('openings_intro', '')),
        'atlas_intro_html': '<p>Organisations are grouped by their home tradition and, within it, by ring. Each entry gives what the organisation is, why it matters for this map, what it works on, its key work and how to get involved. Badges mark entries already on the aisafety.com map and any status worth knowing. Every entry is also in the interactive map, where it can be filtered and compared.</p>',
        'funders_intro_html': paras(cross['funders']['essay']) if cross.get('funders') else '',
        'inta_html': (paras(cross['inta']['essay']) if cross.get('inta') else '') + '<p>Openings marked for int/a in the list above are ones a volunteer community with hubs in London, Berlin and Paris could take on directly.</p>',
        'method_html': METHOD_HTML, 'map_link': MAP_URL, 'date': '4 October 2026',
    },
}
json.dump(extra, open(os.path.join(DATA, 'map_extra.json'), 'w'), indent=1, ensure_ascii=False)
print(f'{len(gaps)} openings, {len(sector_notes)} sector notes, {len(cell_notes)} cell notes, cross: {sorted(cross)}; final present: {final is not None}')
