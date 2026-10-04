"""Render the README graphics from the built pages with headless Chrome, ffmpeg and ImageMagick.

Usage: python3 src/media/make_media.py   (writes into docs/media/)
"""
import os, subprocess, tempfile, json, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'docs', 'media')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
SKELETON = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
TMP = tempfile.mkdtemp(prefix='widerfield-')
os.makedirs(OUT, exist_ok=True)

def page(src, inject='', hash_=''):
    body = open(os.path.join(ROOT, 'dist', src)).read()
    path = os.path.join(TMP, f'p{abs(hash(inject + hash_ + src))}.html')
    open(path, 'w').write(SKELETON + body + inject + '</body></html>')
    return 'file://' + path + (('#' + hash_) if hash_ else '')

def shot(url, out, w, h, dark=False, scale=2, budget=5000):
    args = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--window-size={w},{h}', f'--force-device-scale-factor={scale}',
            f'--virtual-time-budget={budget}', f'--screenshot={out}']
    args.append('--blink-settings=preferredColorScheme=%d' % (0 if dark else 1))
    subprocess.run(args + [url], check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    return out

def magick(*a):
    subprocess.run(['magick', *a], check=True)

# ---------- hero: the field widening, ring by ring ----------
HERO_CSS = """<style>
.top,.filters,.panel,.legend,.foot,.active-filters,.lens,#tip{display:none!important}
html,body{height:100%;overflow:hidden}
.app{min-height:0}
.main{display:block!important}
.stage{padding:0!important;display:grid!important;grid-template-columns:600px 1000px;align-items:center;gap:20px;padding-inline:20px!important}
#hero{display:flex;flex-direction:column;gap:18px;padding-left:36px}
#hero .eb{font:500 15px/1 var(--mono);letter-spacing:.18em;text-transform:uppercase;color:var(--ink-3)}
#hero .num{font:500 150px/0.9 var(--display);letter-spacing:-.03em;color:var(--ink);font-variant-numeric:lining-nums}
#hero .cap{font:400 36px/1.22 var(--display);color:var(--ink);max-width:16ch;text-wrap:balance}
#hero .key{font:400 16px/1.5 var(--sans);color:var(--ink-3);max-width:40ch;margin-top:18px}
.wheel-box{max-width:none!important;width:1000px!important}
.hide-off #wheel g[data-id]:not(.cmg) > .dot,.hide-off #wheel g[data-id]:not(.cmg) > .fund{opacity:.1!important}
</style>"""

def hero_inject(step):
    rings = [[], ['core'], ['core', 'bridge'], ['core', 'bridge', 'adjacent'], []][step]
    caps = ['organisations appear on the standard map of the AI-safety field.',
            'exist to make advanced AI go well: the core.',
            'once you add those rooted in other fields who work on AI safety.',
            'with those studying AI’s effects on people and society from their own traditions.',
            'when you count the knowledge that hasn’t reached AI yet. This is the wider field.']
    return HERO_CSS + """<script>setTimeout(()=>{
const step=%d, rings=%s, cap=%s;
const stage=document.querySelector('.stage');
const h=document.createElement('div'); h.id='hero';
h.innerHTML='<div class="eb">The Wider Field</div><div class="num"></div><div class="cap"></div><div class="key">Each dot is an organisation. Sectors are traditions of knowledge; rings are distance from the AI-safety core.</div>';
stage.insertBefore(h, stage.firstChild);
rings.forEach(r=>{const b=document.querySelector('.fchip[data-f="r"][data-k="'+r+'"]'); if(b) b.click();});
let n;
if(step===0){const D=JSON.parse(document.getElementById('wf-data').textContent); const cm=new Set(D.orgs.filter(o=>o.cm).map(o=>o.id));
document.querySelectorAll('#wheel g[data-id]').forEach(g=>{if(cm.has(g.dataset.id)) g.classList.add('cmg');}); document.body.classList.add('hide-off'); n=cm.size;}
else if(rings.length){n=parseInt(document.getElementById('fcount').textContent);}
else{n=parseInt(document.getElementById('fcount').textContent.split(' of ')[1]);}
h.querySelector('.num').textContent=n; h.querySelector('.cap').textContent=cap;
},400)</script>""" % (step, json.dumps(rings), json.dumps(caps[step]))

def hero(dark):
    tag = 'dark' if dark else 'light'
    frames = []
    for step in range(5):
        f = shot(page('wider-field-map.html', hero_inject(step)), os.path.join(TMP, f'hero-{tag}-{step}.png'), 1660, 1040, dark=dark)
        frames.append(f)
    # frame durations (seconds): hold the classic map and the final frame longer
    durs = [2.6, 1.7, 1.7, 1.7, 3.6]
    lst = os.path.join(TMP, f'hero-{tag}.txt')
    with open(lst, 'w') as fh:
        for f, d in zip(frames, durs):
            fh.write(f"file '{f}'\nduration {d}\n")
        fh.write(f"file '{frames[-1]}'\n")
    out = os.path.join(OUT, f'hero-{tag}.gif')
    vf = 'scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', vf, '-loop', '0', out], check=True)
    shutil.copy(frames[-1], os.path.join(TMP, f'hero-{tag}-final.png'))
    return out

# ---------- feature tiles ----------
def tile(name, inject='', hash_='', w=1500, h=940, dark=False):
    raw = shot(page('wider-field-map.html', inject, hash_), os.path.join(TMP, name + '-raw.png'), w, h, dark=dark)
    out = os.path.join(OUT, name + '.png')
    magick(raw, '-resize', '1500x', '-strip', '-define', 'png:compression-level=9', out)
    return out

def tiles():
    tile('map-entry', hash_='center-for-the-study-of-apparent-selves')
    tile('map-matrix', hash_='matrix')
    tile('map-openings', hash_='openings')

# ---------- report ----------
def report():
    raw = shot(page('wider-field-report.html'), os.path.join(TMP, 'report-raw.png'), 1400, 1500)
    magick(raw, '-resize', '1400x', '-strip', '-define', 'png:compression-level=9', os.path.join(OUT, 'report.png'))
    only = "<script>const m=document.querySelector('main'),a=document.getElementById('atlas'),s=document.getElementById('sector-contemplative');[...m.children].forEach(c=>{if(c!==a)c.remove()});[...a.children].forEach(c=>{if(c!==s)c.remove()});</script>"
    raw2 = shot(page('wider-field-report.html', only), os.path.join(TMP, 'report-atlas-raw.png'), 1400, 1500)
    magick(raw2, '-resize', '1400x', '-strip', '-define', 'png:compression-level=9', os.path.join(OUT, 'report-atlas.png'))

# ---------- lens grid: the same field through four entry points ----------
WHEEL_CSS = """<style>.top,.filters,.panel,.legend,.foot,.active-filters,.lens,#tip{display:none!important}
html,body{height:100%;overflow:hidden}.main{display:block!important}.stage{padding:0!important}
.wheel-box{max-width:none!important;width:1000px!important}.w-slabel,.w-flabel,.w-farc,.w-gap,.w-band,#wheel .fund{display:none}</style>"""

LENSES = [
    ('insider', 'AI-safety insider', 'Work on the AI itself from outside the core', 266),
    ('inta', 'int/a member', 'Active in London, Berlin, Paris or online', 243),
    ('field', 'From another field', 'With fellowships, courses, events or communities', 407),
    ('funder', 'AI-safety funder', 'Everything the standard map leaves out', 658),
]

TOKENS = """:root{--bg:#f1f2ee;--surface:#fafbf8;--ink:#17201e;--ink-2:#46514e;--ink-3:#6c7773;--line:#cdd3cb;--line-2:#e0e4de;--s1:#3c56ac;--s2:#d35985;--s3:#a97416;--s4:#04785d;--s0:#8a918d}
:root.dark{--bg:#0d1117;--surface:#151b1a;--ink:#e4e9e3;--ink-2:#adb6b1;--ink-3:#7f8985;--line:#2d3836;--line-2:#212a28;--s1:#6581d4;--s2:#cf5d85;--s3:#ac7d1b;--s4:#04896a;--s0:#737b77}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"Atkinson Hyperlegible Next",system-ui,sans-serif}"""
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Mono:wght@400;500&family=Atkinson+Hyperlegible+Next:wght@400;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap" rel="stylesheet">'

def lenses():
    imgs = []
    for key, *_ in LENSES:
        inject = WHEEL_CSS + "<script>setTimeout(()=>document.querySelector('[data-p=\"%s\"]').click(),400)</script>" % key
        raw = shot(page('wider-field-map.html', inject), os.path.join(TMP, f'lens-{key}-raw.png'), 1000, 1000)
        sq = os.path.join(TMP, f'lens-{key}.png')
        magick(raw, '-gravity', 'center', '-crop', '1720x1720+0+0', '+repage', '-resize', '840x840', sq)
        imgs.append(sq)
    cells = ''.join(f'<div class="cell"><img src="file://{im}"><div class="txt"><div class="who">{label}</div><div class="q">{q}</div><div class="n">{n} organisations</div></div></div>'
                    for im, (key, label, q, n) in zip(imgs, LENSES))
    css = TOKENS + """
.grid{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;width:1500px;height:940px}
.cell{display:flex;align-items:center;gap:26px;padding:22px 30px;border-right:1px solid var(--line-2);border-bottom:1px solid var(--line-2)}
.cell:nth-child(2n){border-right:0}.cell:nth-child(n+3){border-bottom:0}
.cell img{width:420px;height:420px;flex:none}
.who{font:600 40px/1.1 "Atkinson Hyperlegible Next",sans-serif;margin-bottom:12px}
.q{font:400 30px/1.25 "Newsreader",serif;color:var(--ink-2)}
.n{font:500 21px/1 "Atkinson Hyperlegible Mono",monospace;color:var(--ink-3);margin-top:16px;white-space:nowrap}"""
    html = f'<!doctype html><html><head><meta charset=utf8>{FONTS}<style>{css}</style></head><body><div class="grid">{cells}</div></body></html>'
    path = os.path.join(TMP, 'lenses.html')
    open(path, 'w').write(html)
    raw = shot('file://' + path, os.path.join(TMP, 'lenses-raw.png'), 1500, 940)
    magick(raw, '-resize', '1500x', '-strip', '-define', 'png:compression-level=9', os.path.join(OUT, 'map-lenses.png'))

# ---------- pipeline: every agent as a dot ----------
def dots(n, cls):
    return ''.join(f'<i class="{cls}"></i>' for _ in range(n))

def group(n, cls, label, width=None):
    w = f' style="width:{width}px"' if width else ''
    return f'<div class="grp"><div class="dots"{w}>{dots(n, cls)}</div><div class="gl"><b>{n}</b> {label}</div></div>'

def stage(no, title, desc, swarm, big, out_label, half=False):
    cls = 'stage half' if half else 'stage'
    return (f'<section class="{cls}"><div class="meta"><div class="no">{no}</div><h2>{title}</h2><p>{desc}</p></div>'
            f'<div class="swarm">{swarm}</div><div class="out"><div class="big">{big}</div><div class="ol">{out_label}</div></div></section>')

def flow(text, main=False):
    inner = f'<div class="pill"><span class="ms"></span>{text}</div>' if main else f'<div class="lbl">{text}</div>'
    return f'<div class="flow"><div class="line"></div>{inner}<div class="arrow"></div></div>'

PIPE_CSS = TOKENS + """
body{width:1400px;padding:56px 64px 64px}
header{text-align:center;margin-bottom:36px}
.eb{font:500 15px/1 "Atkinson Hyperlegible Mono",monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-3)}
h1{font:500 64px/1.05 "Newsreader",serif;margin:14px 0;letter-spacing:-.01em}
.lede{font:400 27px/1.45 "Newsreader",serif;color:var(--ink-2);max-width:880px;margin:0 auto 26px}
.legend{display:flex;justify-content:center;flex-wrap:wrap;gap:12px 26px;font-size:20px;color:var(--ink-2)}
.legend span{display:inline-flex;align-items:center;gap:8px}
i{display:inline-block;width:12px;height:12px;border-radius:50%;flex:none}
i.a{background:var(--s1)}i.r{background:var(--s2)}i.s{background:var(--s3)}i.c{background:var(--s4)}i.x{border:1.6px solid var(--s0);background:transparent}
.inputs{display:flex;justify-content:center;gap:14px}
.inputs span{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:10px 20px;font-size:20px;color:var(--ink-2)}
.stage{display:grid;grid-template-columns:360px 1fr 270px;gap:30px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:26px 30px}
.meta .no{font:500 15px/1 "Atkinson Hyperlegible Mono",monospace;color:var(--ink-3);margin-bottom:8px}
.meta h2{font:500 34px/1.1 "Newsreader",serif;margin:0 0 10px}
.meta p{margin:0;font-size:20px;line-height:1.45;color:var(--ink-2)}
.swarm{display:flex;flex-wrap:wrap;gap:20px 28px;align-items:flex-start}
.grp .dots{display:flex;flex-wrap:wrap;gap:5px;max-width:368px}
.grp .gl{font-size:19px;color:var(--ink-2);margin-top:9px}
.grp .gl b{font:600 19px "Atkinson Hyperlegible Mono",monospace;color:var(--ink)}
.out{text-align:right}
.out .big{white-space:nowrap;font:500 52px/1 "Newsreader",serif;letter-spacing:-.01em;font-variant-numeric:lining-nums}
.out .ol{font-size:19px;line-height:1.35;color:var(--ink-3);margin-top:8px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.stage.half{grid-template-columns:1fr;gap:16px;align-items:start}
.stage.half .out{text-align:left;display:flex;align-items:baseline;gap:14px}
.stage.half .out .ol{margin:0}
.flow{display:flex;flex-direction:column;align-items:center;padding:6px 0}
.flow .line{width:2px;height:22px;background:var(--line)}
.flow .arrow{width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-top:10px solid var(--line)}
.flow .lbl{font:italic 400 22px/1.3 "Newsreader",serif;color:var(--ink-3);padding:6px 0}
.flow .pill{display:inline-flex;align-items:center;gap:10px;border:1.5px dashed var(--ink-3);border-radius:999px;padding:10px 20px;font-size:19px;color:var(--ink);background:var(--bg);margin:4px 0}
.flow .pill .ms{width:14px;height:14px;border-radius:50%;border:3px solid var(--ink);flex:none}
.flow .pill::before{content:"Main session";font:500 13px "Atkinson Hyperlegible Mono",monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
.outputs{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.outputs div{border:2px solid var(--ink);border-radius:14px;padding:24px 28px;background:var(--surface)}
.outputs h3{font:500 32px/1.1 "Newsreader",serif;margin:0 0 10px}
.outputs p{margin:0;font-size:20px;line-height:1.5;color:var(--ink-2)}"""

def pipeline(dark):
    body = ''.join([
        '<header><div class="eb">How it was made</div><h1>342 agents, one map</h1>'
        '<p class="lede">Every dot is one AI agent. A main Claude session planned each stage, ran the agents as parallel workflows, and did the curating, ranking and building in between.</p>'
        '<div class="legend"><span><i class="a"></i>Searching, writing, analysing</span><span><i class="r"></i>Critiquing, judging</span><span><i class="s"></i>Synthesising</span>'
        '<span><i class="c"></i>Checking, coding</span><span><i class="x"></i>Duplicate, stopped or declined</span></div></header>',
        '<div class="inputs"><span>The brief, from the int/a Europe chat</span><span>A seed list of 64 items</span><span>The aisafety.com field map, 343 entries</span></div>',
        flow('what to look for, and what is already known'),
        stage(1, 'Discovery sweep', 'Eighteen agents each searched one adjacent field. A critic read the merged list for blind spots, and seven more agents searched them.',
              group(18, 'a', 'field finders') + group(1, 'r', 'critic') + group(7, 'a', 'gap finders'), '596', 'candidate organisations'),
        flow('duplicates merged, out-of-scope entries dropped: 552 organisations', main=True),
        stage(2, 'Categorisation panel', 'Four designers proposed rival schemes: by discipline, by problem, through integral frames, and by reader. Two judges with opposite priorities scored them, and a synthesiser merged the best.',
              group(4, 'a', 'designers') + group(2, 'r', 'judges') + group(1, 's', 'synthesiser'), '14 · 14 · 4', 'traditions, problems and rings, plus int/a lenses'),
        flow('a taxonomy with written tagging rules'),
        stage(3, 'Blind-spot sweep', 'Ten agents searched what the first sweep missed: education, libraries, actuaries, linguistics, epidemiology, under-covered faiths, continental Europe, Asia and Latin America.',
              group(10, 'a', 'finders'), '+171', 'organisations, out of 203 found'),
        flow('723 organisations, in batches of seven'),
        stage(4, 'Profiles and fact-checks', 'One agent researched and tagged each batch of seven organisations, and an independent agent then tried to find what it got wrong. Three workflows ran side by side.',
              group(104, 'a', 'profile writers', 368) + group(104, 'c', 'fact-checkers', 368) + group(36, 'x', 'duplicate or stopped', 132), '268', 'profiles corrected · 722 kept'),
        flow('a blind sample re-tagged, and every profile read for gaps; the two ran in parallel'),
        '<div class="pair">',
        stage('5a', 'Reliability check', 'Two coders re-tagged a sample of 83 organisations without seeing the original tags.', group(24, 'c', 'coders', 170), '99%', 'agreement on home tradition', half=True),
        stage('5b', 'Gaps and openings', 'One analyst per tradition proposed openings. Six agents declined, and a first run of twelve was stopped.', group(13, 'a', 'analysts', 120) + group(18, 'x', 'declined or stopped', 140), '52', 'openings proposed', half=True),
        '</div>',
        flow('merged, ranked and spot-checked on the web; essays written; both pages built', main=True),
        '<div class="outputs"><div><h3>The interactive map</h3><p>722 organisations on a wheel of 14 traditions and 4 rings, with filters, lenses, a matrix and the openings.</p></div>'
        '<div><h3>The report</h3><p>Findings, 42 ranked openings, the funders, the full atlas, and the method and its limits.</p></div></div>',
    ])
    html = f'<!doctype html><html class="{"dark" if dark else ""}"><head><meta charset=utf8>{FONTS}<style>{PIPE_CSS}</style></head><body>{body}</body></html>'
    tag = 'dark' if dark else 'light'
    path = os.path.join(TMP, f'pipeline-{tag}.html')
    open(path, 'w').write(html)
    raw = shot('file://' + path, os.path.join(TMP, f'pipeline-{tag}-raw.png'), 1400, 3400, dark=dark)
    bg = '#0d1117' if dark else '#f1f2ee'
    magick(raw, '-background', bg, '-bordercolor', bg, '-trim', '+repage', '-border', '64', '-resize', '1600x', '-strip', '-define', 'png:compression-level=9', os.path.join(OUT, f'pipeline-{tag}.png'))

if __name__ == '__main__':
    import sys
    parts = sys.argv[1:] or ['hero', 'tiles', 'lenses', 'report', 'pipeline']
    if 'hero' in parts:
        for d in (False, True):
            print(hero(d))
    if 'tiles' in parts:
        tiles()
    if 'lenses' in parts:
        lenses()
    if 'report' in parts:
        report()
    if 'pipeline' in parts:
        for d in (False, True):
            pipeline(d)
    for f in sorted(os.listdir(OUT)):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, 'KB')
