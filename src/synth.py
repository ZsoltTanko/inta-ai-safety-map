"""Synthesis written in the main session (the workflow's synthesiser and five analysts declined to run).
Selects, merges and ranks the analysts' openings, adds the missing arts note and cross-cutting essays, and computes the numbers quoted."""
import json, os, collections, copy
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
raw = json.load(open(os.path.join(D, 'analyst_notes.json')))
P = [p for p in json.load(open(os.path.join(D, 'profiles.json'))) if p.get('include', True)]
T = lambda p: p['tags']
home = lambda p: T(p)['tradition'][0]
ops = {o['id']: o for k, r in raw.items() if k.startswith('sector:') and k != 'sector:arts' for o in r.get('openings', [])}

# ---------- numbers ----------
n = len(P)
cm = sum(p['on_classic_map'] for p in P)
FAM = {'sciences': ['safety', 'formal', 'life'], 'inner': ['minds', 'psych', 'contemplative', 'religion'], 'humanities': ['philosophy', 'arts', 'indigenous'], 'society': ['law', 'economics', 'democracy', 'peace']}
GEN = {'future-of-life-institute', 'coefficient-giving', 'survival-and-flourishing-fund', 'schmidt-sciences', 'openai-foundation', 'cifar', 'humanity-ai', 'john-templeton-foundation'}
W = [p for p in P if p['id'] not in GEN]
def fam_share(f):
    l = [p for p in W if home(p) in FAM[f]]
    return round(100 * sum(p['on_classic_map'] for p in l) / len(l)), len(l)
sec = lambda s: [p for p in W if home(p) == s]
ring = lambda s, r: sum(T(p)['ring'] == r for p in sec(s))
N = dict(
    n=n, cm=cm, cmpct=round(100 * cm / n),
    sci=fam_share('sciences')[0], inner=fam_share('inner')[0], hum=fam_share('humanities')[0], soc=fam_share('society')[0],
    law=len(sec('law')), law_core=ring('law', 'core'), law_cat=sum(T(p)['framing'] == 'catastrophic' for p in sec('law')),
    rel=len(sec('religion')), rel_core=ring('religion', 'core'), ind=len(sec('indigenous')), ind_core=ring('indigenous', 'core'),
    minds=len(sec('minds')), minds_core=ring('minds', 'core'), minds_cm=sum(p['on_classic_map'] for p in sec('minds')),
    formal=len(sec('formal')), formal_core=ring('formal', 'core'), formal_cm=sum(p['on_classic_map'] for p in sec('formal')), formal_adj=ring('formal', 'adjacent'),
    cont=len(sec('contemplative')), cont_pot=ring('contemplative', 'potential'), cont_core=ring('contemplative', 'core'),
    safety=len(sec('safety')), safety_cm=sum(p['on_classic_map'] for p in sec('safety')),
    econ=len(sec('economics')), econ_ma=sum('multi_agent' in T(p)['problems'] for p in sec('economics')),
    adj=sum(T(p)['ring'] == 'adjacent' for p in W),
    builders=sum(T(p)['transfer'] == 'into_builders' for p in P), model=sum(T(p)['transfer'] == 'into_model' for p in P),
    inner_n=len([p for p in W if home(p) in FAM['inner']]), inner_conv=sum(T(p)['transfer'] == 'convening' for p in W if home(p) in FAM['inner']),
    care=sum('care' in T(p)['roles'] for p in P), io=sum('inner_outer' in T(p)['badges'] for p in P),
    naук=0,
    na_uk=round(100 * sum(T(p)['region'] in ('north_america', 'uk_ireland') for p in P) / n), mw=sum(T(p)['standpoint'] != 'neither' for p in P),
    new=sum(T(p)['status'] == 'new' for p in P), ma=sum('multi_agent' in T(p)['problems'] for p in W),
    peace=len(sec('peace')), peace_sec=sum(T(p)['problems'][:1] == ['security'] for p in sec('peace')),
    minds_status=sum('ai_status' in T(p)['problems'] for p in sec('minds')), psych=len(sec('psych')), psych_minds=sum('minds' in T(p)['problems'] for p in sec('psych')),
    bio=len([p for p in sec('philosophy') if T(p)['sub_tradition'] == 'phil_bioethics']), bio_adj=sum(T(p)['ring'] == 'adjacent' for p in sec('philosophy') if T(p)['sub_tradition'] == 'phil_bioethics'),
    dem_cm=sum(p['on_classic_map'] for p in sec('democracy')), dem_cm_ep=sum(p['on_classic_map'] and T(p)['sub_tradition'] == 'dem_epistemics' for p in sec('democracy')),
    hub_l=sum('london' in T(p)['inta_hubs'] for p in P), hub_p=sum('paris' in T(p)['inta_hubs'] for p in P), hub_b=sum('berlin' in T(p)['inta_hubs'] for p in P),
)
N.pop('naук')
print(json.dumps(N, indent=0))

# ---------- openings ----------
def take(i, **edit):
    o = copy.deepcopy(ops[i]); o.update(edit); return o
def drop_sentence(o, field, needle):
    o[field] = ' '.join(s for s in o[field].split('. ') if needle not in s)
    return o

clin = take('clinical-ai-vigilance'); drop_sentence(clin, 'detail', 'CHT wound down')
care_a, care_b = ops['clearance-aware-field-care'], ops['safeguarded-contemplative-support-ai-staff']
field_care = {
    'id': 'field-care-with-safeguards', 'title': 'Clearance-aware care for AI-safety staff, with a safeguarding standard',
    'who': ['founder', 'funder', 'inta'],
    'summary': 'Psychological support built for AI-safety workers has shrunk while the field has grown, and nobody serves people whose stress is locked behind NDAs or infohazard rules. A small, clinically governed service, an AI-safety cohort in an existing peer programme, and a safeguarding standard for the contemplative and coaching programmes the field refers people to would fill the gap.',
    'detail': 'Of the 10 organisations on the map that offer direct care, AI Safety Support has been paused since July 2023, Upgradable has done little since February 2025, Mental Health Navigator runs on about £1,200 a year and does not vet its listings, and Rethink Wellbeing is not AI-specific. The knowledge exists elsewhere: humanitarian staff-care practice, security-cleared clinicians who serve government staff, climate psychology\'s groups for distress about the future, and parliamentary mindfulness programmes with a long track record (The Mindfulness Initiative, Garrison Institute\'s resilience training). The contemplative programmes aimed at AI people are small, expensive or closed, and the most visible one, MAPLE, faces serious public allegations of high-control dynamics. Success would be a confidential service with a published confidentiality framework, a pilot cohort, a yearly wellbeing survey with validated instruments, and a safeguarding checklist that referring organisations actually use.',
    'steps': ['int/a convenes Rethink Wellbeing, Climate Psychology Alliance facilitators and BACP to design an AI-safety CBT cohort and a facilitated "AI café" format, and pilots both in London.',
              'Commission an employment lawyer and a clinical supervisor to draft a confidentiality framework under which vetted therapists can hear NDA-bound material, drawing on how security-cleared clinicians work.',
              'int/a drafts, with clinicians, a safeguarding checklist for contemplative and coaching programmes serving AI people: governance independent of the teacher, complaint routes, no discouraging of outside therapy, norms on sleep and fees.',
              'Run a first field-wide wellbeing survey with clinically validated instruments, repeated yearly.'],
    'evidence': care_a['evidence'], 'sectors': ['psych', 'contemplative'], 'problems': ['people'],
    'related': ['rethink-wellbeing', 'mental-health-navigator', 'ai-safety-support', 'upgradable', 'climate-psychology-alliance', 'british-association-for-counselling-and-psychoth', 'the-mindfulness-initiative', 'garrison-institute', 'monastic-academy-for-the-preservation-of-life-on', 'the-ai-whistleblower-initiative'],
    'confidence': 'high'}
fa, fb = ops['faith-model-spec-review'], ops['multi-tradition-model-spec-review']
spec_review = {
    'id': 'multi-tradition-model-spec-review', 'title': 'Independent multi-tradition review of published model specs, turned into open evals',
    'who': ['founder', 'funder'],
    'summary': 'Labs now publish long value documents (Anthropic\'s constitution runs to 79 pages) that are applied moral philosophy in all but name, and consult religious figures about them privately. No standing body reviews them in public against virtue, care, Confucian, Islamic, Buddhist, Jewish, Hindu or Ubuntu ethics and turns each critique into a test. A small pluralist panel paired with eval builders would fill the gap.',
    'detail': 'The commentary that exists comes from law and EA circles, and the lab consultations reported in 2026 are closed-door and Christian-heavy. On the map, the traditions with the deepest accounts of character and practical wisdom have no route into the model: the Jubilee Centre has measures of practical wisdom but no AI project, and the faith-university benchmark consortium CEFEAI measures how models represent religions, not how they reason morally. Builders who could supply the eval half are nearby: Sophron Research, Compassion Aligned Machine Learning (whose benchmarks already run in UK AISI\'s Inspect), MINT Lab and Civic AI / 6-Pack of Care. Success would be an annual public review of the main published specs, each tradition\'s dissent recorded, with the critiques released as open eval tasks.',
    'steps': ['Recruit a pilot panel from the Jubilee Centre, the Center for Practical Wisdom, Civic AI, CILE (Doha), Kalam Research & Media, CSAS/84000 and a Confucian and an Ubuntu scholar, to review one section of one published constitution (honesty, or handling of religious questions).',
              'Pair each reviewer with an eval builder from Sophron Research or CaML to turn three critiques each into test scenarios, extending CEFEAI\'s open items into moral-reasoning tasks in several languages.',
              'Publish the review and the evals openly (for example as Inspect tasks), keeping disagreements visible, and repeat yearly.'],
    'evidence': fb['evidence'] + ' ' + fa['evidence'], 'sectors': ['philosophy', 'religion', 'contemplative'], 'problems': ['values', 'assurance', 'justice'],
    'related': list(dict.fromkeys(fb['related'] + fa['related'])), 'confidence': 'medium'}
cont = take('contemplative-self-preservation-evals',
    summary='Contemplative groups claim that training AI in non-attachment to self, paired with care, would weaken the self-preservation drive behind shutdown resistance and deception. A 2026 ICML paper has begun probing "attached" versus "detached" persona framings, but no one has tested contemplative training itself against the safety field\'s shutdown, agentic-misalignment and sycophancy evaluations. A pre-registered fine-tuning comparison would show whether the idea has substance.')
narrative = {
    'id': 'narrative-craft-for-alignment-data', 'title': 'Writers and narratologists on alignment pretraining data',
    'who': ['founder', 'funder'],
    'summary': 'Geodesic Research has shown that how AI is described in training data shapes how models behave, and Hyperstition AI now generates whole novels about kind AI to shift that balance. Neither works with professional writers, narratologists or game designers, the people who know how stories form character. A pilot pairing them would test whether crafted narrative moves model behaviour more than generated text does.',
    'detail': 'The arts tradition on the map is dominated by work on how publics and decision-makers picture AI (35 of its 46 entries tag sensemaking), and only two entries move narrative into the model. Narrative scholarship that could inform this sits nearby: the Center for Digital Narrative in Bergen (with its AI STORIES project), Arizona State\'s Center for Science and the Imagination, and Mark Riedl\'s lab at Georgia Tech, whose earlier work taught agents values from stories. Success would be a pre-registered comparison on an open-weight model of crafted, generated and baseline corpora against misalignment evaluations, with the corpus released under an open licence. Risks: effects may be small; such data could slide into public relations; writers\' consent and pay must be explicit.',
    'steps': ['Convene Geodesic Research and Hyperstition AI with Riedl\'s lab, the Center for Digital Narrative and ASU\'s Center for Science and the Imagination to agree a protocol.',
              'Commission a few hundred short works under an open licence, with writers paid and credited, alongside generated and baseline controls.',
              'Run the comparison on an open-weight model with standard misalignment and sycophancy evaluations, and publish null results as readily as positive ones.'],
    'evidence': 'Arts tradition: 46 entries, 35 tagged sensemaking, 2 that move knowledge into the model (geodesic-research, hyperstition-ai). Arts x people and arts x AI moral status are empty cells.',
    'sectors': ['arts', 'psych'], 'problems': ['values', 'agency'],
    'related': ['geodesic-research', 'hyperstition-ai', 'georgia-tech-human-centered-ai-lab', 'center-for-digital-narrative-and-erc-project-ai', 'center-for-science-and-the-imagination-arizona-s', 'hitrecord'],
    'confidence': 'medium'}
dsweep = ops['deliberation-practitioner-sweep']
mapping = {
    'id': 'keep-the-map-as-inta-practice', 'title': 'Make the mapping itself int/a\'s interdisciplinary practice',
    'who': ['inta', 'funder'],
    'summary': 'This map is a first pass made by AI research agents. int/a could turn it into a living, human practice: one session per tradition in which practitioners from that field correct their sector, name what the search missed and say which openings are real, with a post for the int/a Substack or the EA Forum after each.',
    'detail': 'The brief suggested that the int/a project might be the mapping itself, done as an interdisciplinary exercise, and the aisafety.com team said adjacent fields were not their focus. The map has known holes that people would close faster than agents: the democracy analyst found that newDemocracy, MASS LBP, Involve, the Sortition Foundation and Participedia are all missing, and non-English Europe is the weakest part of the search, which int/a\'s Berlin and Paris communities could sweep in German and French. Each session also builds the cross-field relationships the openings depend on. Success would be a map corrected by practitioners in all 14 traditions within a year, a short post per tradition, a one-page brief for funders, and an offer to the aisafety.com team of an adjacent-fields layer. Risks: volunteer burnout and drift; it needs a named owner and a fixed rhythm.',
    'steps': ['Name an owner and a quarterly rhythm; start with Contemplative (int/a\'s own milieu) and Democracy (where the practitioner gaps are best documented).',
              'Berlin and Paris hubs run German- and French-language sweeps of their own tradition-by-tradition gaps.',
              'Publish one post per tradition with its corrected sector and openings, plus a funders\' one-pager.',
              'Share the corrected map with the aisafety.com team as a proposed adjacent-fields layer.'],
    'evidence': dsweep['evidence'] + ' The blind-spot notes call non-English Europe "the weakest part of the sweep".',
    'sectors': ['contemplative', 'democracy'], 'problems': ['epistemics', 'people'],
    'related': ['integral-altruism', 'people-powered', 'democracy-x', 'democracynext', 'make-org', 'caf-ia', 'connected-by-data'],
    'confidence': 'high'}

ORDER = [
    take('ai-confidential-reporting-and-investigation'), cont, clin, take('system-safety-placement-fellowship'), take('cross-cultural-wisdom-evals'),
    take('comparative-cognition-evals'), take('ai-mediator-audit-lab'), field_care, mapping, take('mind-attribution-clinical-bridge'),
    take('macroprudential-frontier-ai'), spec_review, take('bioethics-oversight-for-frontier-ai'), take('psychology-of-the-race'), take('homeostatic-objectives'),
    take('relational-alignment-fellowship'), take('faith-frontier-risk-desk'), take('contemplative-funders-ai-call'), take('mediating-the-ai-race'), take('sts-observatory-of-ai-safety'),
    take('actuarial-foundation-model-catastrophe-scenarios'), take('ai-harms-epidemiology-unit'), take('uncertainty-reporting-for-capability-evals'), take('dmdu-for-safety-frameworks'), take('introspection-validity-evals'),
    take('ai-consciousness-adversarial-collaboration'), take('agent-population-ecology'), take('mediation-science-for-multi-agent-ai'), take('agent-market-collusion-monitoring'), take('open-endedness-safety-alife'),
    take('social-choice-for-model-specs'), take('frontier-risk-global-deliberation-2027'), take('ai-moral-status-consensus-conference'), take('chaplaincy-spiritual-crisis-evals'), take('community-governed-red-teaming'),
    take('indigenous-consent-signals-in-training-data'), narrative, take('verification-practitioner-fellowship'), take('lab-safety-bargaining-clauses'), take('frontier-human-rights-due-diligence'),
    take('litigation-evidence-desk'), take('african-philosophy-in-ai-safety'),
]
for i, o in enumerate(ORDER):
    o['top'] = i < 10
    o['rank'] = i + 1

# ---------- sector note for arts (its analyst declined) ----------
arts = {'overview': 'Arts, narrative and futures brings imagination as a working method: the scenarios, wargames and stories through which publics and decision-makers picture AI, and the futures and technology-assessment bodies that turn foresight into policy. The map holds 46 organisations here (9 core, 11 bridge, 20 adjacent, 7 potential; 5 on the aisafety.com map). The core is scenario and narrative work inside the safety community, such as the AI Futures Project, Intelligence Rising, Existential Hope, Tarbell and Geodesic Research. The outer rings hold futures institutes (Copenhagen Institute for Futures Studies, Institute for the Future, Sitra, Europe\'s parliamentary technology-assessment offices), arts institutions (Serpentine Arts Technologies, AIxDESIGN, Better Images of AI) and the translators\' and linguists\' professional bodies.',
        'missing': 'Narrative craft has barely met the finding that stories in training data shape model behaviour, and the futures profession itself (the World Futures Studies Federation, UNESCO Futures Literacy, the School of International Futures) has no sustained AI-risk programme, so the field\'s scenarios come almost entirely from forecasters inside it.'}

# ---------- essays ----------
FUNDERS = f"""Money for this wider field comes from three groups that rarely fund together. The AI-safety funders (the Survival and Flourishing Fund, Coefficient Giving, the Future of Life Institute, Macroscopic Ventures, Longview and the Navigation Fund) fund almost entirely in the core and bridge rings, and mostly in the formal and life sciences, consciousness and AI welfare, and forecasting. Public research money for AI safety, such as ARIA's £59 million Safeguarded AI programme and the £27 million Alignment Project led by the UK AI Security Institute, follows similar lines with a stronger pull towards mathematics and verification.

The second group funds the adjacent ring and frames AI as present harm or public interest. Humanity AI has committed $500 million over five years from ten foundations, Current AI reports $404 million pledged for public-interest AI, Omidyar Network, Mozilla and the European AI & Society Fund back rights and accountability groups, and Anthropic's Economic Futures programme has a $200 million research fund. These funders reach the law, economics and democracy traditions that hold most of the map's organisations, but rarely the questions about the AI itself.

The third group funds the traditions this map is about without any AI-safety framing. Templeton World Charity Foundation put about $2.8 million into three Diverse Intelligences hubs in 2025, and the John Templeton Foundation's Future of Intelligence venture will give more than $60 million over 2026 to 2028. Lilly Endowment gave $50.8 million to Notre Dame's DELTA network for faith-based formation in an age of AI. Lloyd's Register Foundation (a £300 million grant portfolio, with £13.9 million to York's Centre for Assuring Autonomy) and UL Research Institutes fund engineering safety, and Carnegie Corporation funds the AI-and-nuclear work of the peace tradition.

Some traditions have no dedicated funder for AI work at all. The contemplative world's grant-makers (Fetzer, Kalliopeia, 1440, Hemera, Templeton Religion Trust) were found to make no AI grants, which helps explain why {N['cont_pot']} of the {N['cont']} contemplative organisations sit in the potential ring. No AI-safety funder backs any of the Indigenous-led organisations, and the psychological support services for the field's own workers run on very little.

The most promising moves for funders are co-funding pairs that cross these groups: a safety funder with Templeton on comparative cognition and consciousness science; with Lloyd's Register Foundation or UL Research Institutes on placing system-safety engineers; with Carnegie Corporation on verification expertise; with Mind & Life and the contemplative funders on a contemplative-science call; and with faith funders on carrying frontier-risk concerns into religious norm-setting. The newest and largest funder of all, the OpenAI Foundation, holds a stake in OpenAI worth more than $100 billion, and where it chooses to sit among these groups will matter more than any single grant."""

BRIDGES = f"""Several problems on the map are worked on by two or more communities that barely know each other. Power concentration is the clearest. Inside the safety field, Formation Research, Longview's power-concentration call, the Alignment of Complex Systems group's work on gradual disempowerment and the Post-AGI workshops treat it as a structural risk from advanced AI. Outside it, the Open Markets Institute, the AI Now Institute, MIT's Stone Center, the unions (the TUC, UTAW and Unite at Google DeepMind, the Alphabet Workers Union) and the financial-stability supervisors work on the same concentration with antitrust law, collective bargaining and macroprudential tools. The two sides cite different literatures and meet at different conferences.

The same split runs through human minds. The UK AI Security Institute's societal-resilience team and the AI-welfare groups study persuasion, sycophancy and attribution of mind from the model's side; psychiatrists at King's College London, Aarhus and Beth Israel Deaconess, the psychoanalysts' AI commission, BACP and the child-development groups (Common Sense Media, Fairplay, 5Rights) study the same harms from the person's side. Among consciousness researchers, {N['minds_status']} of {N['minds']} work on AI moral status, while {N['psych_minds']} of {N['psych']} psychology organisations work on protecting minds and none works on moral status, although both study people who come to believe an AI is conscious.

Law repeats the pattern: the x-risk legal groups on the classic map have little contact with the {N['law']} rights, liability and accountability organisations, of which only {N['law_cat']} frame the stakes as catastrophic. Democracy splits between its forecasting strand, which the safety field has adopted ({N['dem_cm_ep']} of the tradition's {N['dem_cm']} classic-map entries are forecasting or epistemics groups), and its legitimacy strand of assemblies and deliberation, which it has not. Peace splits between arms control and Track II diplomacy, which work on AI, and peacebuilding and mediation, which mostly do not.

Connecting these worlds would yield more than goodwill. Each side holds something the other lacks: evaluation methods and threat models on one side, clinical evidence, legal remedies, institutional legitimacy and decades of practice on the other. Several openings below are bridges of exactly this kind: shared evaluations built with clinicians, translation fellowships, joint research agendas and convenings with a fixed output."""

INTA = f"""The map says something specific about int/a's own milieu. Contemplative and integral organisations number {N['cont']}, and {N['cont_pot']} of them are potential partners with little or no AI work; only {N['cont_core']} sit in the core. The int/a principle badges were given sparingly, and only {N['io']} organisations carry the "inner work, outer change" badge: integral altruism itself and Connecting Intelligence. The traditions int/a draws on hold a great deal of relevant knowledge and very few bridges to where AI is being built and governed.

That points to a role suited to a volunteer community with hubs in London ({N['hub_l']} organisations on the map are active there), Paris ({N['hub_p']}) and Berlin ({N['hub_b']}). int/a can translate: write the briefs that restate AI-safety problems in the language of contemplative science, faith traditions or bioethics, and carry them to the people who can act. It can convene where pace and trust matter, such as dialogues between AI-safety and AI-ethics researchers, or workshops joining clinicians and consciousness researchers, in the spirit of moving at the speed of wisdom. And it can model care for the people doing the work, with the safeguards that the MAPLE allegations show are needed.

The suggestion in the brief that the mapping itself could be the int/a project is the strongest of all. This map was made quickly by AI agents; a version corrected tradition by tradition by practitioners would be more accurate, and the process would build the relationships the openings depend on. A post per tradition for the int/a Substack or the EA Forum, and a one-page brief for funders, would make the work legible to new funders, which was the original aim.

Two cautions. The integral and contemplative world has its own failure modes, from guru dynamics to grand theory without evidence, and int/a's credibility with funders depends on holding its own proposals to the same tests it asks of others: the contemplative self-preservation study and the wisdom benchmark below are designed to produce publishable null results as readily as positive ones. And the map should not become a way of claiming the field's adjacent traditions for int/a: most of these organisations have never heard of it, and the first step is listening to them."""

PEOPLE = f"""The people who build, govern, fund and research AI are the least served part of this map. Only {N['care']} organisations offer direct care or support to individuals, and they are fragile: AI Safety Support has been paused since July 2023, Upgradable has done little since early 2025, Mental Health Navigator runs on about £1,200 a year, and Rethink Wellbeing is not specific to AI. The AI Whistleblower Initiative supports insiders who raise concerns, and the Data Labelers Association and the Data Workers' Inquiry speak for the workforce that produces safety-relevant labels.

The need is documented. The seed list cites a 2026 write-up of survey data reporting burnout among 59% of AI-safety respondents, and forum posts describe stress that cannot be taken to an outside therapist because of non-disclosure agreements, anticipatory grief about the future, and isolation outside the main hubs. Psychology on this map studies users, children and patients far more than it studies the people and institutions steering AI: no organisation measures safety culture inside labs or studies how decision-makers perceive the race.

Other fields already know how to do much of this. Humanitarian organisations have staff-care guidelines for people exposed to distressing material; governments have clinicians cleared to hear classified material; climate psychology runs groups for distress about the future; chaplaincy has codified ethics of presence and referral; medicine and engineering have professional oaths and just-culture reporting. None of these has been adapted for AI.

Any support offered to AI people needs safeguards from the start. The most visible contemplative programme for technologists, MAPLE, faces serious, detailed public allegations of high-control dynamics, contested by its supporters. Independent governance, clear complaint routes, no discouraging of outside therapy, and norms on sleep, money and hierarchy are the minimum, and the openings below build them in."""

summary_points = [
    f"The map holds {n} organisations across 14 traditions. Only {cm} ({N['cmpct']}%) appear on the aisafety.com field map, so most of this landscape is invisible from the field's standard directory.",
    f"Visibility falls with distance from the sciences: {N['sci']}% of Sciences & engineering entries are on the classic map, against {N['inner']}% of Minds & inner life. Consciousness and AI minds has {N['minds_core']} core organisations and none on the classic map.",
    f"The biggest bodies of knowledge sit furthest from the safety frame. Law, rights & society has {N['law']} organisations, {N['law_core']} of them core and {N['law_cat']} framing the stakes as catastrophic. Religion has {N['rel']} and {N['rel_core']} core entry; Indigenous & decolonial knowledges has none.",
    f"Adjacent fields mostly talk to their own people: {N['model']} of {n} organisations move their knowledge into AI models and {N['builders']} into the people who build and govern AI, while {N['inner_conv']} of the {N['inner_n']} in Minds & inner life mainly convene their own community.",
    "AI safety has imported the artefacts of older safety cultures (safety cases, incident databases, risk thresholds) but not their institutions: no confidential near-miss reporting, no independent accident investigation, no measurement of safety culture and no bioethics-style monitoring board was found.",
    f"The inner side of the field is the thinnest part of the map: {N['care']} organisations offer direct care, one of them paused since 2023, and only {N['io']} carry int/a's \"inner work, outer change\" badge.",
    f"Coverage leans Anglophone: {N['na_uk']}% of entries are in North America or the UK and Ireland, and {N['mw']} are Indigenous-led or centred on the Majority World. Some of what looks empty is a limit of the search.",
    f"{len(ORDER)} openings for founders, funders and int/a follow, ranked. The first ten are flagged as places to start.",
]
findings = [
    {'title': 'Most of the wider field is invisible from the standard map', 'body': f"Of {n} organisations, {cm} are on the aisafety.com field map. None of the {N['minds']} consciousness and AI-minds organisations is there although {N['minds_core']} are core, and neither is any of the {N['cont']} contemplative or {N['ind']} Indigenous & decolonial entries. The classic map is a good guide to the core; it is not a guide to the knowledge around it."},
    {'title': 'AI safety has absorbed formal science and little else', 'body': f"The formal and physical sciences are the one tradition the field already owns: {N['formal_core']} of {N['formal']} organisations are core, {N['formal_cm']} are on the classic map and only {N['formal_adj']} is adjacent. Much of the new money of 2025 and 2026 has gone to mathematics, learning theory and verification, for example Coefficient Giving's $10 million to the new Mathematical AI Safety Institute and ARIA's £59 million Safeguarded AI programme."},
    {'title': 'The largest knowledge bases are furthest out', 'body': f"The adjacent ring is the largest, with {N['adj']} organisations. Law ({N['law']}), democracy and collective intelligence (68), psychology ({N['psych']}) and economics ({N['econ']}) are the biggest traditions, and all of them sit mostly outside the safety frame. Their methods (litigation, assemblies, clinical evidence, antitrust and supervision) are tested at scale but rarely applied to frontier AI."},
    {'title': 'Knowledge rarely reaches the builders', 'body': f"Only {N['builders']} organisations change the people who build, govern and fund AI, against {N['model']} that work on the models and many more that inform institutions or convene their own community. Psychology studies users and children; nobody on the map studies the psychology of the labs and governments steering AI."},
    {'title': 'Artefacts without institutions', 'body': f"The safety and risk sciences have {N['safety']} organisations on the map, {N['safety_cm']} of them on the classic map. Frontier AI has taken their safety cases, risk thresholds and incident databases, but not confidential near-miss reporting, independent investigation, just culture or peer review. Philosophy shows the same split: AI safety adopted its theories of value, while {N['bio_adj']} of the {N['bio']} applied-ethics and bioethics bodies, which hold fifty years of oversight practice, sit in the adjacent ring."},
    {'title': 'Two communities study the same people from opposite sides', 'body': f"{N['minds_status']} of the {N['minds']} consciousness organisations work on AI moral status; {N['psych_minds']} of the {N['psych']} psychology organisations work on protecting human minds, and none on moral status. Both study people who come to believe an AI is conscious, the welfare researchers to take the belief seriously and the clinicians to treat its harms, and they do not work together."},
    {'title': "int/a's own milieu is mostly potential", 'body': f"{N['cont_pot']} of the {N['cont']} contemplative and integral organisations ({round(100 * N['cont_pot'] / N['cont'])}%) are potential partners, the highest share of any tradition, and only {N['cont_core']} are core. The contemplative world's funders make no AI grants, and the groups turning contemplative insight into alignment proposals have not yet tested them against the safety field's own evaluations."},
    {'title': 'Religion has reach, and a shallow bridge', 'body': f"The {N['rel']} religious organisations include norm-setters that speak for billions and have already issued AI rulings (the Holy See's Magnifica Humanitas, the International Islamic Fiqh Academy's Resolution 258, ICESCO's Riyadh Charter), but none of those rulings addresses loss of control. The main bridge to AI safety is a single round of FLI grants to faith communities (16 grants, about $1.36 million)."},
    {'title': "Democracy's forecasting strand made it in; its legitimacy strand didn't", 'body': f"{N['dem_cm_ep']} of the {N['dem_cm']} democracy and collective-intelligence organisations on the classic map are forecasting or epistemics groups. Assemblies, deliberative polling and consensus conferences, the tradition's machinery of legitimacy, have not reached the decisions the safety field cares most about, such as capability thresholds, pauses or AI moral status."},
    {'title': 'Multi-agent risk is thinly staffed across traditions', 'body': f"Only {N['ma']} organisations work on populations of interacting AI agents. Economics has {N['econ_ma']} of {N['econ']}; peace has none, though conflict between parties is its core subject; collective-behaviour biologists and evolutionary game theorists sit in the potential ring. The disciplines that study cooperation and conflict among many agents are mostly not yet looking at AI agents."},
]
openings_intro = f"Eighteen analysts, one for each tradition and four for cross-cutting questions, read the profiles and statistics and proposed {sum(len(r.get('openings', [])) for k, r in raw.items() if k.startswith('sector:'))} openings. Five of the eighteen and the final synthesiser did not complete their work, so the selection, merging and ranking below, the arts note and the cross-cutting essays were done in the main session. Each opening names the part of the map it would fill and who is nearby. They were not individually tested against the open web; ten of the strongest were spot-checked for prior work, and one was narrowed as a result. Treat each as a well-grounded hypothesis to check before acting."

json.dump({'openings': ORDER, 'arts': arts, 'essays': {'funders': FUNDERS, 'bridges': BRIDGES, 'inta': INTA, 'people': PEOPLE},
           'summary_points': summary_points, 'findings': findings, 'openings_intro': openings_intro, 'numbers': N},
          open(os.path.join(D, 'synthesis.json'), 'w'), indent=1, ensure_ascii=False)
print(len(ORDER), 'openings written')
