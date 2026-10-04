"""Build the findings report (static HTML) from data/profiles.json and data/map_extra.json.

Usage: python3 src/build_report.py [data/profiles.json] [dist/wider-field-report.html]
"""
import json, os, sys, html, collections, re

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import build_map as BM

E = lambda s: html.escape(str(s or ''), quote=True)
V = BM.V
LAB = {k: {c['key']: c for c in V[k]} for k in V}
lab = lambda f, k: (LAB[f].get(k) or {}).get('label', k)
chip = lambda f, k: (LAB[f].get(k) or {}).get('chip', lab(f, k))
defn = lambda f, k: re.sub(r'^\[[^\]]*\]\s*', '', re.sub(r'^Wheel \d+ \([^)]*\)\.\s*', '', (LAB[f].get(k) or {}).get('definition', '')))
RINGS = ['core', 'bridge', 'adjacent', 'potential']
RL = {'core': 'Core', 'bridge': 'Bridge', 'adjacent': 'Adjacent', 'potential': 'Potential'}


def para(t):
    return ''.join(f'<p>{E(x)}</p>' for x in (t if isinstance(t, list) else [t]) if x)


def main():
    prof = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BM.DATA, 'profiles.json')
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BM.ROOT, 'dist', 'wider-field-report.html')
    orgs, _ = BM.from_profiles(prof)
    orgs = [o for o in orgs if o['tr'] and o['tr'][0] in BM.SECTORS]
    by = {o['id']: o for o in orgs}
    X = json.load(open(os.path.join(BM.DATA, 'map_extra.json'))) if os.path.exists(os.path.join(BM.DATA, 'map_extra.json')) else {}
    R = X.get('report', {})
    gaps = X.get('gaps', [])
    notes = X.get('sectorNotes', {})
    wheel = [o for o in orgs if not o['gf']]
    fam_of = {s: f['key'] for f in BM.FAMILIES for s in f['sectors']}
    n = len(orgs)
    cm = sum(o['cm'] for o in orgs)

    # ---------- figures ----------
    cell = collections.Counter((o['tr'][0], o['r']) for o in wheel)
    cellcm = collections.Counter((o['tr'][0], o['r']) for o in wheel if o['cm'])
    mx = max(cell.values()) if cell else 1
    fig1 = ['<table class="fig-table"><thead><tr><th scope="col">Tradition</th>' + ''.join(f'<th scope="col">{RL[r]}</th>' for r in RINGS) + '<th scope="col">Total</th><th scope="col">On classic map</th></tr></thead><tbody>']
    for fm in BM.FAMILIES:
        fig1.append(f'<tr class="fam"><th colspan="7">{E(fm["label"])}</th></tr>')
        for s in fm['sectors']:
            tot = sum(cell[(s, r)] for r in RINGS)
            tcm = sum(cellcm[(s, r)] for r in RINGS)
            row = f'<tr><th scope="row"><a href="#sector-{s}">{E(chip("tradition", s))}</a></th>'
            for r in RINGS:
                c = cell[(s, r)]
                row += f'<td class="{"zero" if not c else ""}"><span class="cellbar" style="--w:{round(100 * c / mx)}%"></span><span class="num">{c or "–"}</span></td>'
            row += f'<td class="num">{tot}</td><td class="num">{tcm} <span class="pct">({round(100 * tcm / max(1, tot))}%)</span></td></tr>'
            fig1.append(row)
    fig1.append('</tbody></table>')
    fig1 = ''.join(fig1)

    famrows = []
    for fm in BM.FAMILIES:
        l = [o for o in wheel if fam_of[o['tr'][0]] == fm['key']]
        sh = round(100 * sum(o['cm'] for o in l) / max(1, len(l)))
        core = round(100 * sum(o['r'] == 'core' for o in l) / max(1, len(l)))
        famrows.append((fm['label'], len(l), sh, core))
    fig2 = '<div class="bars">' + ''.join(f'<div class="brow"><span class="bl">{E(a)}</span><span class="bt"><i style="width:{s}%"></i></span><span class="bv">{s}% on map · {c}% core · {k} entries</span></div>' for a, k, s, c in famrows) + '</div>'

    probs = [p for a in BM.ARCS for p in a['problems']]
    mcount = collections.Counter((o['tr'][0], p) for o in wheel for p in o['p'])
    mmax = max(mcount.values()) if mcount else 1
    fig3 = ['<div class="scroll"><table class="mx"><thead><tr><th></th>' + ''.join(f'<th scope="col"><span>{E(chip("problem", p))}</span></th>' for p in probs) + '</tr></thead><tbody>']
    for fm in BM.FAMILIES:
        for s in fm['sectors']:
            fig3.append(f'<tr><th scope="row">{E(chip("tradition", s))}</th>' + ''.join(
                (f'<td title="{E(chip("tradition", s))} × {E(chip("problem", p))}: {mcount[(s, p)]}"><i style="--d:{max(5, round(22 * (mcount[(s, p)] / mmax) ** .5))}px"></i></td>' if mcount[(s, p)] else '<td class="z"><b></b></td>') for p in probs) + '</tr>')
    fig3.append('</tbody></table></div>')
    fig3 = ''.join(fig3)

    TF = ['into_model', 'into_builders', 'into_institutions', 'protecting', 'convening', 'none_yet']
    tfc = collections.Counter((fam_of[o['tr'][0]], o['tf']) for o in wheel)
    fig4 = ['<table class="fig-table tf"><thead><tr><th scope="col">Family</th>' + ''.join(f'<th scope="col">{E(chip("transfer", t))}</th>' for t in TF) + '</tr></thead><tbody>']
    for fm in BM.FAMILIES:
        tot = sum(tfc[(fm['key'], t)] for t in TF) or 1
        fig4.append(f'<tr><th scope="row">{E(fm["label"])}</th>' + ''.join(f'<td><span class="cellbar" style="--w:{round(100 * tfc[(fm["key"], t)] / tot)}%"></span><span class="num">{round(100 * tfc[(fm["key"], t)] / tot)}%</span></td>' for t in TF) + '</tr>')
    fig4.append('</tbody></table>')
    fig4 = ''.join(fig4)

    # ---------- entries ----------
    def entry(o):
        meta = [chip('org_type', o['ot']) if o['ot'] else '', o['hq'], ('founded ' + o['f']) if o['f'] else '']
        st = '' if o['ss'] in ('active', '') else f'<span class="badge warn">{E(chip("status", o["ss"]))}</span>'
        kw = '; '.join((f'<a href="{E(k[2])}">{E(k[0])}</a>' if k[2] else E(k[0])) + (f' ({E(k[1])})' if k[1] else '') for k in o['kw'][:3])
        eng = '; '.join(E(x) for x in o['en'][:3])
        sec = ', '.join(E(chip('tradition', t)) for t in o['tr'][1:])
        return f'''<article class="entry" id="{E(o['id'])}">
<h4><a href="{E(o['u'])}">{E(o['n'])}</a> <span class="badge ring">{RL[o['r']]}</span>{'<span class="badge cm">On aisafety.com</span>' if o['cm'] else ''}{st}</h4>
<p class="meta">{' · '.join(E(m) for m in meta if m)}{(' · also draws on ' + sec) if sec else ''}</p>
<p>{E(o['sum'])}</p>
{f'<p class="why">{E(o["why"])}</p>' if o['why'] else ''}
<p class="small"><span class="k">Works on</span> {', '.join(E(chip('problem', p)) for p in o['p'])}{(' · <span class="k">Key work</span> ' + kw) if kw else ''}{(' · <span class="k">Get involved</span> ' + eng) if eng else ''}</p>
{f'<p class="small caveat"><span class="k">Note</span> {E(o["cv"])}</p>' if o['cv'] else ''}
</article>'''

    chapters = []
    for fm in BM.FAMILIES:
        chapters.append(f'<h2 class="fam-h" id="family-{fm["key"]}">{E(fm["label"])}</h2>')
        for s in fm['sectors']:
            l = [o for o in wheel if o['tr'][0] == s]
            nt = notes.get(s, {})
            rings = ''
            for r in RINGS:
                rl = sorted([o for o in l if o['r'] == r], key=lambda o: o['n'].lower())
                if rl:
                    rings += f'<h3 class="ring-h">{RL[r]} ring <span>{len(rl)}</span></h3>' + ''.join(entry(o) for o in rl)
                else:
                    rings += f'<h3 class="ring-h empty">{RL[r]} ring <span>none found</span></h3>'
            ops = [g for g in gaps if s in (g.get('sectors') or [])]
            chapters.append(f'''<section class="sector" id="sector-{s}">
<p class="eyebrow">{E(fm['label'])} · {len(l)} organisations · {sum(o['cm'] for o in l)} on the classic map</p>
<h2>{E(lab('tradition', s))}</h2>
<p class="lede">{E(nt.get('overview') or defn('tradition', s))}</p>
{f'<p class="missing"><b>What is missing.</b> {E(nt["missing"])}</p>' if nt.get('missing') else ''}
{('<p class="small"><span class="k">Openings here</span> ' + '; '.join(f'<a href="#op-{E(g["id"])}">{E(g["title"])}</a>' for g in ops) + '</p>') if ops else ''}
{rings}
</section>''')

    funders = [o for o in orgs if 'fund' in o['ro']]
    funders.sort(key=lambda o: (not o['gf'], o['n'].lower()))
    ftab = '<div class="scroll"><table class="fig-table funders"><thead><tr><th scope="col">Funder or programme</th><th scope="col">Traditions</th><th scope="col">What is known about the money</th></tr></thead><tbody>' + ''.join(
        f'<tr><th scope="row"><a href="#{E(o["id"])}">{E(o["n"])}</a>{" <span class=badge>generalist</span>" if o["gf"] else ""}</th><td>{E(", ".join(chip("tradition", t) for t in o["tr"]))}</td><td>{E(o["fu"] or o["why"])}</td></tr>' for o in funders) + '</tbody></table></div>'

    opcards = ''.join(f'''<article class="op" id="op-{E(g['id'])}">
<p class="eyebrow">{str(g.get('rank', '')) + ' · ' if g.get('rank') else ''}{'Start here · ' if g.get('top') else ''}{' · '.join(E({'founder': 'For founders', 'funder': 'For funders', 'inta': 'For int/a'}.get(w, w)) for w in g.get('who', []))}{(' · ' + E(g['confidence']) + ' confidence') if g.get('confidence') else ''}</p>
<h3>{E(g['title'])}</h3>
<p>{E(g['summary'])}</p>
{f'<p>{E(g["detail"])}</p>' if g.get('detail') else ''}
{('<ul>' + ''.join(f'<li>{E(x)}</li>' for x in g.get('steps', [])) + '</ul>') if g.get('steps') else ''}
{f'<p class="small"><span class="k">Evidence</span> {E(g["evidence"])}</p>' if g.get('evidence') else ''}
<p class="small"><span class="k">Where on the map</span> {', '.join(f'<a href="#sector-{s}">{E(chip("tradition", s))}</a>' for s in g.get('sectors', []))}{(' · <span class="k">Nearby</span> ' + ', '.join(f'<a href="#{E(i)}">{E(by[i]["s"] or by[i]["n"])}</a>' for i in g.get('related', []) if i in by)) if g.get('related') else ''}</p>
</article>''' for g in gaps)

    index = sorted(orgs, key=lambda o: o['n'].lower())
    idx_html = '<div class="index">' + ''.join(f'<a href="#{E(o["id"])}">{E(o["n"])}</a>' for o in index) + '</div>'

    toc = [('summary', 'Summary'), ('brief', 'The brief'), ('organised', 'How the map is organised'), ('findings', 'What the map shows'), ('openings', 'Openings'), ('atlas', 'The atlas')]
    toc_html = ''.join(f'<li><a href="#{a}">{E(b)}</a></li>' for a, b in toc)
    toc_html += '<li class="sub">' + ''.join(f'<a href="#sector-{s}">{E(chip("tradition", s))}</a>' for fm in BM.FAMILIES for s in fm['sectors']) + '</li>'
    toc_html += ''.join(f'<li><a href="#{a}">{E(b)}</a></li>' for a, b in [('funders', 'Funders'), ('inta', 'Taking it forward'), ('method', 'Method and limits'), ('index', 'Index A–Z')])

    tpl = open(os.path.join(D, 'report_template.html')).read()
    rep = {
        '__N__': str(n), '__CM__': str(cm), '__CMPCT__': str(round(100 * cm / n)),
        '__TOC__': toc_html,
        '__SUMMARY__': R.get('summary_html', '<p>Draft.</p>'),
        '__BRIEF__': R.get('brief_html', '<p>Draft.</p>'),
        '__ORGANISED__': R.get('organised_html', '<p>Draft.</p>'),
        '__FIG1__': fig1, '__FIG2__': fig2, '__FIG3__': fig3, '__FIG4__': fig4,
        '__FINDINGS__': R.get('findings_html', '<p>Draft.</p>'),
        '__OPENINGS_INTRO__': R.get('openings_intro_html', ''),
        '__OPENINGS__': opcards or '<p>Draft.</p>',
        '__ATLAS_INTRO__': R.get('atlas_intro_html', ''),
        '__ATLAS__': ''.join(chapters),
        '__FUNDERS_INTRO__': R.get('funders_intro_html', ''),
        '__FUNDERS__': ftab,
        '__INTA__': R.get('inta_html', '<p>Draft.</p>'),
        '__METHOD__': R.get('method_html', '<p>Draft.</p>'),
        '__INDEX__': idx_html,
        '__MAPLINK__': R.get('map_link', '#'),
        '__DATE__': R.get('date', '4 October 2026'),
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    open(out, 'w').write(tpl)
    print(f'{n} orgs -> {out} ({len(tpl) // 1024} KB)')


if __name__ == '__main__':
    main()
