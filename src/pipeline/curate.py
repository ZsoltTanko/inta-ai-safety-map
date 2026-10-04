import json, re
d = json.load(open('candidates_raw.json'))
cs = d['candidates']
for i, c in enumerate(cs): c['_idx'] = i

MERGES = {  # target: [sources]
 190: [109, 254], 108: [253], 141: [409], 352: [339], 420: [381], 419: [97, 397],
 151: [337, 338], 185: [186], 349: [357], 463: [573], 464: [571], 566: [451], 567: [585],
 469: [555], 472: [447], 113: [193, 403], 354: [593], 110: [263, 356], 249: [519],
 25: [533], 103: [102], 73: [232], 231: [423], 51: [344], 69: [346], 437: [484], 497: [496, 456],
}
RENAME = {
 190: 'Templeton World Charity Foundation (TWCF): Diverse Intelligences and related programmes',
 108: 'John Templeton Foundation (JTF): Future of Intelligence venture',
 352: 'Cape Institute for Safe AI (CISAI), formerly AI Safety South Africa',
 420: 'Coefficient Giving (formerly Open Philanthropy): Project Tailwind and AI-for-epistemics funding',
 419: 'Future of Life Institute (FLI): grants, Futures Program and Religious Projects',
 151: 'Cooperative AI Foundation (CAIF)',
 185: 'NOOMA Labs (successor to Cross Labs)',
 103: 'Holy See: Rome Call for AI Ethics, Antiqua et Nova and Magnifica Humanitas',
 73: 'UK AI Security Institute (UK AISI): societal resilience team and the Alignment Project',
 231: 'ARIA: Safeguarded AI and Scaling Trust',
 51: 'Rethink Priorities: AI Cognition Initiative and Digital Consciousness Model',
 69: 'Neuromatch (incl. AI Sentience Scholars)',
 437: 'The Millennium Project (incl. the UNCPGA High-Level Expert Panel on AGI)',
 497: 'European Parliamentary Technology Assessment network (EPTA): TAB, Rathenau Instituut, STOA and peers',
 39: 'Foresight Institute: AI safety grants (incl. Neurotechnology for Safe AI)',
 380: 'Effective Institutions Project (EIP), incl. the Checks & Balances RFP with CIP',
 113: 'Leverhulme Centre for the Future of Intelligence (CFI)',
 249: 'Mind & Life Institute (and Mind & Life Europe)',
 110: 'Berggruen Institute (incl. Noema and the Peking University centre)',
 354: 'Beijing Institute of AI Safety and Governance (Beijing-AISI) and Center for Long-term AI',
}
DROP = {17, 24, 94, 95, 210, 211, 165, 296, 320, 321, 523, 540, 580, 581, 584, 592, 371}

ADD = [
 dict(name='Civic AI / 6-Pack of Care (Audrey Tang and Caroline Green)', url='https://6pack.care/', kind='project/initiative', ring='bridge',
      one_line="Audrey Tang and Caroline Green's project at Oxford's Institute for Ethics in AI that turns Joan Tronto's care ethics into six principles for aligning and governing AI.", field_lens='care ethics, civic technology, democratic theory', ai_connection='Proposes care-based alignment and governance principles (attentiveness, responsibility, competence, responsiveness, solidarity, symbiosis); book due 2027.'),
 dict(name='Life Itself (incl. the Second Renaissance community)', url='https://lifeitself.org/', kind='network/community/coalition', ring='potential',
      one_line="Rufus Pollock's metamodern community and research collective working on a 'second renaissance' of culture and values, with residential hubs.", field_lens='metamodernism, cultural change, wisdom culture', ai_connection='Its Second Renaissance forum has critiqued the Full-Stack Alignment programme; engagement with AI safety is light so far.'),
 dict(name='Metamoderna (Hanzi Freinacht)', url='https://metamoderna.org/', kind='nonprofit/research org', ring='potential',
      one_line='Think tank of Daniel Görtz and Emil Ejner Friis (writing as Hanzi Freinacht) developing metamodern political philosophy and "political metamodernism".', field_lens='metamodernism, developmental politics', ai_connection='No dedicated AI-safety work found; relevant as a source of developmental and metamodern governance ideas.'),
 dict(name='The Stoa', url='https://www.thestoa.ca/', kind='network/community/coalition', ring='potential',
      one_line="Peter Limberg's online sensemaking and contemplative 'digital monastery', hosting live dialogues with liminal-web thinkers.", field_lens='sensemaking, contemplative practice, liminal web', ai_connection='Hosts sessions on AI and meaning; engagement with AI safety to be verified.'),
 dict(name='Win-Win (Liv Boeree)', url='https://www.winwinpodcast.com/', kind='publication/media', ring='bridge',
      one_line="Liv Boeree's podcast and media project on Moloch, competition and coordination, much of it about the AI race.", field_lens='game theory, coordination, media', ai_connection="Popularises the Moloch / multipolar-trap framing of AI racing (TED talk 'The dark side of competition in AI'); interviews with Emmett Shear and others."),
 dict(name='AI Impacts', url='https://aiimpacts.org/', kind='nonprofit/research org', ring='core',
      one_line='Research project on the likely course and impacts of advanced AI, known for its expert surveys, which ran the 2024 Essay Competition on the Automation of Wisdom and Philosophy.', field_lens='forecasting, philosophy, wisdom', ai_connection="Its wisdom essay competition (winners Oct 2024) framed wisdom and philosophy as targets for differential AI development."),
]

by_idx = {c['_idx']: c for c in cs}
merged_away = set()
for t, srcs in MERGES.items():
    tc = by_idx[t]
    for s in srcs:
        sc = by_idx[s]
        merged_away.add(s)
        tc.setdefault('merged_from', []).append({'name': sc['name'], 'url': sc['url'], 'one_line': sc['one_line'], 'ai_connection': sc['ai_connection']})
        for u in [sc['url']] + sc.get('evidence_urls', []):
            if u and u not in tc['evidence_urls']: tc['evidence_urls'].append(u)
        for a in sc['found_by']:
            if a not in tc['found_by']: tc['found_by'].append(a)
for t, n in RENAME.items(): by_idx[t]['name'] = n

final = [c for c in cs if c['_idx'] not in DROP and c['_idx'] not in merged_away]
for a in ADD:
    a.update(on_classic_map=False, status='active', evidence_urls=[a['url']], confidence='medium', found_by=['seed'], location='')
    final.append(a)

def slug(s):
    s = re.sub(r'\([^)]*\)', '', s).split(':')[0]
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s[:48].rstrip('-')
seen = set()
for c in final:
    s = slug(c['name']); base = s; k = 2
    while s in seen: s = f'{base}-{k}'; k += 1
    seen.add(s); c['id'] = s
    c.pop('_idx', None)
json.dump(final, open('roster_final.json', 'w'), indent=1)
print(len(final), 'entries')
import collections
print(collections.Counter(c['ring'] for c in final))
