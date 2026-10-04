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
    tile('map-lens', inject="<script>setTimeout(()=>document.querySelector('[data-p=\"inta\"]').click(),400)</script>")
    tile('map-matrix', hash_='matrix')
    tile('map-openings', hash_='openings')

# ---------- report ----------
def report():
    raw = shot(page('wider-field-report.html'), os.path.join(TMP, 'report-raw.png'), 1400, 1500)
    magick(raw, '-resize', '1400x', '-strip', '-define', 'png:compression-level=9', os.path.join(OUT, 'report.png'))
    only = "<script>const m=document.querySelector('main'),a=document.getElementById('atlas'),s=document.getElementById('sector-contemplative');[...m.children].forEach(c=>{if(c!==a)c.remove()});[...a.children].forEach(c=>{if(c!==s)c.remove()});</script>"
    raw2 = shot(page('wider-field-report.html', only), os.path.join(TMP, 'report-atlas-raw.png'), 1400, 1500)
    magick(raw2, '-resize', '1400x', '-strip', '-define', 'png:compression-level=9', os.path.join(OUT, 'report-atlas.png'))

# ---------- icon: the wheel alone ----------
ICON_CSS = """<style>.top,.filters,.panel,.legend,.foot,.active-filters,.lens,#tip{display:none!important}
html,body{height:100%;overflow:hidden}.main{display:block!important}.stage{padding:0!important}
.wheel-box{max-width:none!important;width:1000px!important}.w-slabel,.w-flabel,.w-farc,.w-gap{display:none}</style>"""

def icon():
    raw = shot(page('wider-field-map.html', ICON_CSS), os.path.join(TMP, 'icon-raw.png'), 1000, 1000, dark=True)
    # crop to the rings (labels hidden), round the corners
    magick(raw, '-gravity', 'center', '-crop', '1720x1720+0+0', '+repage', '-resize', '512x512', os.path.join(TMP, 'icon-sq.png'))
    magick(os.path.join(TMP, 'icon-sq.png'), '(', '+clone', '-alpha', 'transparent', '-fill', 'white', '-draw', 'roundrectangle 0,0 511,511 100,100', ')',
           '-compose', 'DstIn', '-composite', '-resize', '256x256', os.path.join(OUT, 'icon.png'))

if __name__ == '__main__':
    icon()
    for d in (False, True):
        print(hero(d))
    tiles()
    report()
    for f in sorted(os.listdir(OUT)):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, 'KB')
    print('frames kept in', TMP)
