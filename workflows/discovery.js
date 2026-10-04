export const meta = {
  name: 'inta-ai-safety-discovery',
  description: 'Sweep 18 adjacent-field angles for integral-flavoured AI safety organisations, then a completeness critic and a gap-filling second round',
  phases: [
    { title: 'Sweep', detail: '18 finders, one per adjacent field or angle' },
    { title: 'Critique', detail: 'completeness critic over the merged list' },
    { title: 'Fill gaps', detail: 'second-round finders for the blind spots the critic names' },
  ],
}

const DIR = '<scratchpad>'

const CANDIDATE = {
  type: 'object',
  properties: {
    name: { type: 'string', description: 'Official name, acronym in parentheses' },
    url: { type: 'string' },
    kind: { type: 'string', enum: ['nonprofit/research org', 'academic lab/centre', 'programme/fellowship', 'funder', 'network/community/coalition', 'company/startup', 'publication/media', 'project/initiative'] },
    one_line: { type: 'string', description: 'What it is and does, concretely, in one sentence' },
    field_lens: { type: 'string', description: 'Which adjacent field(s) or tradition(s) it draws on' },
    ai_connection: { type: 'string', description: 'How its work bears on making advanced AI go well; name specific outputs, programmes or papers' },
    ring: { type: 'string', enum: ['core', 'bridge', 'adjacent', 'potential'] },
    on_classic_map: { type: 'boolean', description: 'Listed in aisafety_map.json' },
    location: { type: 'string' },
    status: { type: 'string', enum: ['active', 'inactive/closed', 'unclear'] },
    evidence_urls: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'], description: 'Confidence that it exists, is current, and fits the scope' },
  },
  required: ['name', 'url', 'kind', 'one_line', 'field_lens', 'ai_connection', 'ring', 'on_classic_map', 'status', 'evidence_urls', 'confidence'],
}

const FINDINGS = {
  type: 'object',
  properties: {
    candidates: { type: 'array', items: CANDIDATE },
    notable_people: { type: 'array', items: { type: 'string' }, description: 'Individuals central to this angle (with affiliation) who are not organisations' },
    angle_notes: { type: 'string', description: 'The landscape of this angle: where relevant knowledge lives, which bridges to AI safety exist, which obvious bridges are missing (gaps for founders or funders), and surprises' },
  },
  required: ['candidates', 'angle_notes'],
}

const ANGLES = [
  { key: 'complexity', title: 'Complexity science, physics, mathematics of agency, cybernetics',
    detail: 'Organisations applying complex-systems science, statistical physics, dynamical systems, category theory, information theory, cybernetics or theoretical biology to agency, intelligence and alignment.',
    seeds: 'Alignment of Complex Systems (ACS, Prague); Principles of Intelligence (Princint, formerly PIBBSS); Simplex; Timaeus; Santa Fe Institute; Complexity Science Hub Vienna; Topos Institute; Basis Research Institute; Equilibria Network; Dovetail; Iliad; ARIA Safeguarded AI' },
  { key: 'biology', title: 'Biology, basal cognition, evolution, artificial life, active inference',
    detail: 'Organisations drawing on developmental and evolutionary biology, collective intelligence in living systems, artificial life, the free-energy principle and active inference to think about alignment, agency and multi-agent AI.',
    seeds: 'Softmax; Michael Levin lab / Allen Discovery Center (Tufts); Center for the Study of Apparent Selves; Cross Labs (Kyoto); Active Inference Institute; Karl Friston and collaborators; International Society for Artificial Life' },
  { key: 'neuro', title: 'Neuroscience, cognitive science, consciousness science',
    detail: 'NeuroAI safety, brain-inspired alignment, cognitive-science approaches to values and agency, and consciousness science as it bears on AI.',
    seeds: 'Amaranth Foundation NeuroAI-for-safety work; Astera (Steve Byrnes, brain-like AGI safety); AE Studio (neglected approaches, self-other overlap); California Institute for Machine Consciousness; Conscium; PRISM (Partnership for Research Into Sentient Machines); Sussex Centre for Consciousness Science; Qualia Research Institute; NYU Center for Mind, Ethics, and Policy' },
  { key: 'contemplative', title: 'Contemplative traditions, wisdom science, meaning',
    detail: 'Buddhist, contemplative, wisdom-science and meaning-centred approaches to alignment and to AI going well, including artificial-wisdom research and wisdom evaluations.',
    seeds: 'Meaning Alignment Institute; Center for the Study of Apparent Selves; Ruben Laukkonen contemplative-AI programme; Igor Grossmann Wisdom & Culture Lab; Vervaeke Foundation; Buddhism & AI Initiative; MAPLE (flagged); Mind & Life Institute; Compassion Aligned Machine Learning (CaML); Templeton-funded AI and wisdom projects' },
  { key: 'minds', title: 'Developmental and clinical psychology; protecting human minds, attention, relationships and children',
    detail: 'Organisations working on AI psychological harms, AI companions and attachment, cognitive atrophy, AI psychosis, child development and human agency.',
    seeds: 'AI Psychological Harms Research Coalition (Zak Stein); Center for Humane Technology; Fairplay; Common Sense Media AI risk work; American Psychological Association AI advisories; MIT Media Lab Advancing Humans with AI; Stanford Brainstorm lab' },
  { key: 'inner', title: 'Inner development, culture and mental health of the people building and governing AI (field health)',
    detail: 'Support, wellbeing, inner-development, leadership and culture initiatives for AI safety researchers, lab staff and policymakers; developmental and contemplative training for technologists; burnout and doom-distress support.',
    seeds: 'Inner Development Goals; Presencing Institute; Rethink Wellbeing; Mental Health Navigator; Upgradable; AI Safety Support (closed); Center for Applied Rationality; integral altruism itself; retreats or coaching specifically for AI safety people' },
  { key: 'collective', title: 'Collective intelligence, deliberative democracy, civic tech, pluralism',
    detail: 'Participatory and deliberative alignment, collective-intelligence infrastructure, plural governance of AI, AI-assisted deliberation.',
    seeds: 'Collective Intelligence Project; AI Objectives Institute; Plurality Institute; Metagov; Computational Democracy Project (Pol.is); Stanford Deliberative Democracy Lab; DemocracyNext; g0v / vTaiwan; Remesh; Nesta Centre for Collective Intelligence Design; UK AI4CI hub; DeepMind Habermas Machine' },
  { key: 'economics', title: 'Economics, mechanism design, game theory, political economy, power concentration',
    detail: 'Cooperative AI, multi-agent incentives, post-AGI economics, gradual disempowerment, lock-in, windfall distribution, democratic political economy of AI.',
    seeds: 'Cooperative AI Foundation; FOCAL (CMU); Center on Long-Term Risk; RadicalxChange; Anton Korinek / economics of TAI; Windfall Trust; Forethought; gradual-disempowerment researchers (Jan Kulveit, ACS); Formation Research; Modeling Cooperation; Stanford Digital Economy Lab' },
  { key: 'philosophy', title: 'Philosophy, ethics, religion and theology',
    detail: 'Philosophical, ethical and faith-based organisations working on AI and the human future, moral status, and what AI should be aligned to.',
    seeds: 'Oxford Institute for Ethics in AI; Berggruen Institute; Cosmos Institute; NYU Center for Mind, Ethics, and Policy; AI and Faith; Rome Call for AI Ethics / Pontifical Academy for Life; Vatican doctrinal note Antiqua et Nova; Templeton foundations; Center for Theology and the Natural Sciences' },
  { key: 'metacrisis', title: 'Metacrisis, systems thinking, civilisational design, metamodernism, Game B, ecology',
    detail: 'Metacrisis and civilisational-design organisations engaging AI; systems-thinking and ecological framings of AI risk; planetary-computation thinking.',
    seeds: 'Consilience Project; Civilization Research Institute; Perspectiva; Life Itself / Second Renaissance; Metamoderna; Emerge; The Stoa; Antikythera (Berggruen); Long Now Foundation; Club of Rome; Stockholm Resilience Centre; Cultural Evolution Society' },
  { key: 'sociotech', title: 'Law, rights and sociotechnical AI governance outside the x-risk canon',
    detail: 'AI-ethics, rights, justice and sociotechnical-governance organisations whose knowledge AI safety under-uses, and orgs bridging the ethics/safety divide.',
    seeds: 'Ada Lovelace Institute; AI Now Institute; Data & Society; DAIR; Mozilla Foundation; Humane Intelligence; Partnership on AI; Berkman Klein Center; Global Center on AI Governance; Leverhulme Centre for the Future of Intelligence; Oxford Martin AI Governance Initiative' },
  { key: 'peace', title: 'Peace, conflict, diplomacy, international relations, security studies',
    detail: 'Peacebuilding, conflict-resolution, Track II diplomacy, arms-control and multilateral organisations engaging AI risk; trust-building between rival powers.',
    seeds: 'Safe AI Forum (International Dialogues on AI Safety); Concordia AI; Simon Institute for Longterm Governance; SIPRI; PRIO; UNIDIR; Geneva Centre for Security Policy; Build Up; Beyond Conflict; Search for Common Ground; Stanford CISAC; Institute for Security and Technology' },
  { key: 'safetysci', title: 'Safety science, systems engineering, public health, risk and resilience',
    detail: 'Organisations bringing lessons from aviation, nuclear, medicine, high-reliability organisations, systems-theoretic safety (STAMP), epidemiology, incident reporting and resilience engineering to AI.',
    seeds: 'MIT systems-safety group (Nancy Leveson, STAMP/STPA for AI); Responsible AI Collaborative (AI Incident Database); UL Research Institutes Digital Safety Research Institute; Johns Hopkins Center for Health Security; ALLFED; SaferAI; Centre for Long-Term Resilience; Lloyd\'s Register Foundation' },
  { key: 'humanities', title: 'Humanities, arts, narrative, anthropology, STS, media',
    detail: 'Worldbuilding, narrative, art, anthropology and science-and-technology-studies organisations shaping how humanity imagines and relates to advanced AI.',
    seeds: 'Foresight Existential Hope; FLI Superintelligence Imagined; Leverhulme CFI Global AI Narratives; Better Images of AI; Serpentine Arts Technologies; ASU Center for Science and the Imagination; Cosmos Institute; anthropologists studying AI labs' },
  { key: 'plural_world', title: 'Indigenous, Global South and non-Western knowledge systems',
    detail: 'Indigenous-led AI research, data sovereignty, African, Asian and Latin American AI safety and governance groups, and non-Western ethical frameworks (Ubuntu, Confucian, Buddhist, Islamic) applied to AI.',
    seeds: 'Indigenous Protocol and AI Working Group; Abundant Intelligences; Te Hiku Media; Masakhane; Concordia AI; AI Safety Asia; ILINA Program; Research ICT Africa; Global Center on AI Governance; Tierra Común; Lelapa AI' },
  { key: 'cooperative', title: 'Cooperative AI, multi-agent safety, AI welfare and the human–AI relationship',
    detail: 'Multi-agent risk, cooperation research, AI moral status and welfare, digital minds, and relational framings of human–AI coexistence.',
    seeds: 'Cooperative AI Foundation; FOCAL (CMU); Center on Long-Term Risk; Eleos AI Research; Equilibria Network; Sentience Institute; Rethink Priorities digital-minds work; Sentient Futures; Cooperative AI Summer School; Multi-Agent Risks report authors' },
  { key: 'funders', title: 'Funders, fellowships and field-builders for interdisciplinary and integral AI safety work',
    detail: 'Philanthropies, government programmes, regranters, fellowships and field-building programmes that fund or train people bringing other disciplines into AI safety, or that fund wisdom, meaning, contemplative, democratic or civilisational work on AI. Note each funder\'s relevant programme and rough scale where known.',
    seeds: 'Templeton World Charity Foundation; John Templeton Foundation; FLI; Future of Life Foundation; Coefficient Giving (Project Tailwind); Survival and Flourishing Fund; Longview; Astralis; Navigation Fund; Omidyar Network; Fetzer Institute; 1440 Foundation; Berggruen; Schmidt Sciences; Patrick J. McGovern Foundation; Mind & Life grants; Cosmos grants; Foresight grants; Manifund; ARIA; AI2050; Project Liberty; Princint fellowship; FLF fellowship' },
  { key: 'epistemics', title: 'Epistemics, sensemaking and AI for human reasoning',
    detail: 'Organisations building AI tools and institutions for better collective reasoning, forecasting, deliberation and sensemaking as part of navigating advanced AI.',
    seeds: 'Forethought; Future of Life Foundation AI for Human Reasoning fellowship and its alumni projects; Elicit; Sage (AI Digest); Society Library; QURI; Metaculus; Sentinel; Community Notes research; TruthfulAI' },
]

const finderPrompt = (a, extra) => `Read ${DIR}/context.md first: it is the project brief, the scope definition and the four rings. ${DIR}/aisafety_map.json is the classic aisafety.com map (use it for on_classic_map); ${DIR}/seed_list.md is what the user already has.

Your angle: ${a.title}
${a.detail}
Starting points (verify them, but your value is in finding what is NOT on this list): ${a.seeds}
${extra || ''}
Search the web thoroughly: at least 15 distinct WebSearch queries, including searches for 2025-2026 launches, organisations outside the US and UK, academic centres, small or new groups, and funders or fellowships in this angle. Load WebSearch and WebFetch with ToolSearch if they are deferred. Open each candidate's site or a recent source to confirm it exists, what it actually does, and whether it is still active in 2026. Prefer primary sources.

Return 15-45 candidates. Include ring "potential" organisations only where the knowledge is clearly relevant and you can name the specific AI-safety problem it bears on. Be honest in confidence. Don't pad: a precise list of 20 beats a loose list of 45. In angle_notes, describe the landscape of this angle: where relevant knowledge lives, which bridges to AI safety exist, and which obvious bridges are missing (gaps a founder or funder could fill).`

const norm = s => (s || '').toLowerCase().replace(/\([^)]*\)/g, '').replace(/^the\s+/, '').replace(/[^a-z0-9]/g, '')
const host = u => { const m = (u || '').toLowerCase().match(/^(?:https?:\/\/)?(?:www\.)?([^\/?#]+)(\/[^?#]*)?/); return m ? m[1] + ((m[2] || '').replace(/\/$/, '')) : '' }

const merged = new Map()
const byHost = new Map()
function addAll(list, angleKey) {
  let fresh = 0
  for (const c of list || []) {
    const k = norm(c.name), h = host(c.url)
    const existing = merged.get(k) || (h && byHost.get(h))
    if (existing) {
      if (!existing.found_by.includes(angleKey)) existing.found_by.push(angleKey)
      continue
    }
    const entry = { ...c, found_by: [angleKey] }
    merged.set(k, entry)
    if (h) byHost.set(h, entry)
    fresh++
  }
  return fresh
}

phase('Sweep')
const round1 = await parallel(ANGLES.map(a => () =>
  agent(finderPrompt(a), { label: `find:${a.key}`, phase: 'Sweep', schema: FINDINGS })
    .then(r => ({ key: a.key, r }))))
const notes = {}
for (const x of round1.filter(Boolean)) {
  if (!x.r) continue
  addAll(x.r.candidates, x.key)
  notes[x.key] = x.r.angle_notes
}
log(`Round 1: ${merged.size} distinct candidates from ${round1.filter(x => x && x.r).length}/${ANGLES.length} finders`)

phase('Critique')
const roster = [...merged.values()].map(c => `${c.name} [${c.ring}; ${c.field_lens}]`).join('\n')
const CRITIC = {
  type: 'object',
  properties: {
    gap_angles: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string', description: 'short slug' },
      title: { type: 'string' },
      detail: { type: 'string', description: 'What to search for and why it is missing' },
      seeds: { type: 'string', description: 'Specific organisation names or search leads' },
    }, required: ['key', 'title', 'detail', 'seeds'] } },
    named_missing: { type: 'array', items: { type: 'string' }, description: 'Specific organisations you believe fit the scope and are missing, each with a URL if known' },
    overall_assessment: { type: 'string' },
  },
  required: ['gap_angles', 'named_missing', 'overall_assessment'],
}
const critic = await agent(`Read ${DIR}/context.md. Eighteen finders have swept adjacent fields for integral-flavoured AI safety organisations. Below is the merged roster (name [ring; field lens]) and each finder's notes on its angle.

Your job is to find what is missing. Think about disciplines, traditions, regions, organisation types (funders, fellowships, academic centres, startups, coalitions, media), languages, and rings (especially "potential" bridge partners in adjacent fields) that the sweep under-covers. Check your hunches with web searches before naming organisations. Propose 4-7 gap angles, each with a concrete search brief, and list up to 40 specific named organisations that fit and are missing.

ROSTER (${merged.size}):
${roster}

FINDER NOTES:
${Object.entries(notes).map(([k, v]) => `## ${k}\n${v}`).join('\n\n')}`, { label: 'completeness-critic', phase: 'Critique', schema: CRITIC })

phase('Fill gaps')
const already = [...merged.values()].map(c => c.name).join('; ')
const gapAngles = (critic && critic.gap_angles || []).slice(0, 7)
const namedMissing = (critic && critic.named_missing || [])
const round2 = await parallel([
  ...gapAngles.map(g => () =>
    agent(finderPrompt(g, `\nThese are already found; return only organisations NOT in this list: ${already}\n`), { label: `gap:${g.key}`, phase: 'Fill gaps', schema: FINDINGS })
      .then(r => ({ key: 'gap:' + g.key, r }))),
  () => agent(finderPrompt({ title: 'Verify named leads from the completeness critic', detail: 'Check each lead below: does it exist, is it active in 2026, does it fit the scope? Return the ones that do as candidates (full fields), and add any closely related organisations you discover on the way.', seeds: namedMissing.join('; ') }, `\nAlready found (skip these): ${already}\n`), { label: 'gap:named-leads', phase: 'Fill gaps', schema: FINDINGS })
    .then(r => ({ key: 'gap:named-leads', r })),
])
let fresh2 = 0
for (const x of round2.filter(Boolean)) {
  if (!x.r) continue
  fresh2 += addAll(x.r.candidates, x.key)
  notes[x.key] = x.r.angle_notes
}
log(`Round 2 added ${fresh2}; total ${merged.size} distinct candidates`)

const all = [...merged.values()]
const ringCounts = {}
for (const c of all) ringCounts[c.ring] = (ringCounts[c.ring] || 0) + 1
return {
  total: all.length,
  ringCounts,
  critic_assessment: critic && critic.overall_assessment,
  gap_angles: gapAngles.map(g => g.title),
  names: all.map(c => `${c.name} | ${c.ring} | ${c.found_by.join(',')}`),
}
