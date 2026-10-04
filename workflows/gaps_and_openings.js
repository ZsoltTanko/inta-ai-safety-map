export const meta = {
  name: 'inta-gaps-and-openings',
  description: 'Sector and cross-cutting analysts propose openings for founders, funders and int/a; a synthesiser selects and writes the findings (no per-opening checkers)',
  phases: [
    { title: 'Analyse', detail: '14 sector analysts and 4 cross-cutting analysts' },
    { title: 'Synthesise', detail: 'select, merge and rank openings; write the key findings' },
  ],
}

const DIR = '<scratchpad>'
const SECTORS = ['safety', 'formal', 'life', 'minds', 'psych', 'contemplative', 'religion', 'philosophy', 'arts', 'indigenous', 'law', 'economics', 'democracy', 'peace']

const OPENING = {
  type: 'object',
  properties: {
    id: { type: 'string', description: 'short kebab-case slug' },
    title: { type: 'string', description: 'At most 12 words; names the thing to build or fund' },
    who: { type: 'array', items: { type: 'string', enum: ['founder', 'funder', 'inta'] } },
    summary: { type: 'string', description: 'Two plain sentences: what is missing and what would fill it' },
    detail: { type: 'string', description: '3-5 sentences: why it is open, what exists nearby (name organisations), what success would look like, risks' },
    steps: { type: 'array', items: { type: 'string' }, description: '2-4 concrete first steps' },
    evidence: { type: 'string', description: 'What on the map supports this (counts, empty cells, named entries)' },
    sectors: { type: 'array', items: { type: 'string' }, description: 'tradition keys' },
    problems: { type: 'array', items: { type: 'string' }, description: 'problem keys' },
    related: { type: 'array', items: { type: 'string' }, description: 'roster ids of organisations nearby or who could partner' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['id', 'title', 'who', 'summary', 'detail', 'steps', 'evidence', 'sectors', 'problems', 'related', 'confidence'],
}

const SECTOR_OUT = {
  type: 'object',
  properties: {
    overview: { type: 'string', description: '3-4 plain sentences: what this tradition brings to making AI go well, who the main actors are, how close it sits to the AI-safety core' },
    missing: { type: 'string', description: 'One or two sentences: the most important thing missing here' },
    cell_notes: { type: 'array', items: { type: 'object', properties: { ring: { type: 'string', enum: ['core', 'bridge', 'adjacent', 'potential'] }, note: { type: 'string', description: 'What this empty or sparse cell means: a real opening, or likely a limit of the search, and why' } }, required: ['ring', 'note'] } },
    key_insight: { type: 'string', description: 'The single most surprising or useful observation about this tradition, with a number if possible' },
    openings: { type: 'array', items: OPENING, description: '2-4 openings' },
  },
  required: ['overview', 'missing', 'cell_notes', 'key_insight', 'openings'],
}

const CROSS_OUT = {
  type: 'object',
  properties: {
    essay: { type: 'string', description: 'The analysis asked for, as plain paragraphs separated by blank lines' },
    key_insights: { type: 'array', items: { type: 'string' } },
    openings: { type: 'array', items: OPENING, description: '3-5 openings' },
  },
  required: ['essay', 'key_insights', 'openings'],
}

const COMMON = `Read ${DIR}/context.md (the brief: int/a, the WhatsApp thread, the brief's ask for "a concrete list of problems for founders and opportunities for funders", the brief's point about blind spots) and ${DIR}/taxonomy.md (traditions, problems, rings; use its keys). The whole map is in ${DIR}/gapin/index.txt (one line per organisation: id | name | traditions | ring | problems | roles | transfer | region | MAP if on aisafety.com | status | summary) and the statistics in ${DIR}/gapin/stats.md. Discovery notes are in ${DIR}/angle_notes.md and ${DIR}/blind_spots.md (what was searched and found absent). Today is 2026-10-04.

An "opening" is something specific a founder could build, a funder could fund, or int/a could do, that would widen AI safety by bringing in knowledge the field lacks. It must be grounded in the map (cite counts, empty cells and named organisations by id), concrete enough to act on, and honest about uncertainty. Avoid generic advice ("more research is needed", "build bridges"). Prefer openings where relevant knowledge clearly exists in another field and the bridge to AI is missing or thin. Do quick web searches when you need to check whether something already exists. Write in plain British English.`

phase('Analyse')
const sectorTasks = SECTORS.map(s => ({
  key: 'sector:' + s, kind: 'sector', s,
  prompt: `${COMMON}

You are the analyst for one tradition: "${s}". Its organisations' full profiles are in ${DIR}/gapin/sector-${s}.json (home tradition = ${s}). Read them all, and look in index.txt for organisations elsewhere that draw on ${s} as a secondary tradition.

Write the overview, the most important missing piece, notes on every ring cell of this tradition that is empty or has two or fewer entries (is it a real opening or a search artefact?), one key insight, and 2-4 openings rooted in this tradition.`,
  schema: SECTOR_OUT,
}))
const crossTasks = [
  { key: 'cross:funders', prompt: `${COMMON}\n\nYou are the funders analyst. Read ${DIR}/gapin/funders.json (every funder and fund-giving programme on the map, with whatever is known about money) and scan the funding field across sector files as needed. Write an essay (4-6 paragraphs) for new and existing funders: who funds what across the traditions, where money concentrates, which traditions have no dedicated funder, which large new funders have arrived in 2025-26 and what they fund, and which co-funding partnerships between safety funders and non-safety funders (Templeton, Lloyd's Register Foundation, Humanity AI, Carnegie, Mozilla, faith funders...) are plausible. Then 3-5 openings for funders.` },
  { key: 'cross:bridges', prompt: `${COMMON}\n\nYou are the bridges analyst. Using index.txt and the sector files, find "parallel worlds": problems where several traditions work in parallel with little contact (for example power concentration: core x-risk groups versus antitrust, labour and AI-ethics groups; human minds: UK AISI versus psychoanalysts and child-development researchers). Name the organisations on each side. Write an essay (4-6 paragraphs) on the most consequential disconnects and what connecting them would yield. Then 3-5 openings that would bridge them (convenings, translation fellowships, joint research agendas, shared evaluations).` },
  { key: 'cross:inta', prompt: `${COMMON}\n\nYou are the int/a analyst. int/a's principles are in context.md. Look at what the map shows about int/a's own milieu (the Contemplative tradition, integral and metamodern bodies, entries with int/a badges, entries near London, Berlin and Paris) and where int/a's way of working (full-spectrum knowing, speed of wisdom, recoupling, fractal altruism, inner work and outer change) could add something no one else is adding. Consider the suggestion in the brief that the int/a project could be the mapping itself, as an interdisciplinary exercise, and the brief's idea of a one-pager and a jointly written Substack or EA Forum piece. Write an essay (4-6 paragraphs) on int/a's specific role. Then 3-5 openings that int/a itself (volunteers, small budget, a community in London, Berlin and Paris) could take on in the next 6-12 months.` },
  { key: 'cross:people', prompt: `${COMMON}\n\nYou are the analyst for the people doing the work: the wellbeing, inner development, conscience and practical wisdom of those who build, govern, fund and research AI (problem key "people"), plus the data-labelling workforce. Read the relevant profiles (search index.txt for problem "people" and roles "care", "educate"). The seed list documents high burnout (59% in a 2026 survey write-up), NDA-bound stress, doom distress, and a cautionary case (MAPLE's alleged high-control dynamics). Write an essay (4-6 paragraphs) on what exists, what failed or closed (AI Safety Support), what other fields (clinical psychology, chaplaincy, climate psychology, contemplative training, whistleblower support, professional ethics in medicine and engineering) already know, and what is missing. Then 3-5 openings, with explicit safeguards.` },
].map(t => ({ ...t, kind: 'cross', schema: CROSS_OUT }))

const TEST = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['holds', 'narrowed', 'refuted'] },
    revised_title: { type: 'string' },
    revised_summary: { type: 'string' },
    prior_work: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, url: { type: 'string' }, one_line: { type: 'string' }, on_map: { type: 'boolean' } }, required: ['name', 'url', 'one_line', 'on_map'] } },
    reasoning: { type: 'string' },
  },
  required: ['verdict', 'revised_title', 'revised_summary', 'prior_work', 'reasoning'],
}
const testPrompt = (op) => `You are an adversarial checker. Someone claims the following is an open niche in widening AI safety. Your job is to find out whether it is already being done. Search the web hard (at least 6 queries, including the obvious names for such a thing; load WebSearch with ToolSearch if deferred) and check ${DIR}/gapin/index.txt (organisations already on the map). Default to finding prior work.

Verdict: "holds" if nothing substantial already does it; "narrowed" if something exists but a clearly defined part remains open (then rewrite the title and summary to the part that remains); "refuted" if it is substantially being done. List the prior work you found (name, url, one line, whether it is already on the map). Keep revised_title and revised_summary equal to the originals if the verdict is "holds".

OPENING:
${JSON.stringify(op, null, 1)}`

const results = await parallel([...sectorTasks, ...crossTasks].map(t => () =>
  agent(t.prompt, { label: t.key, phase: 'Analyse', schema: t.schema }).then(r => ({ key: t.key, kind: t.kind, s: t.s, r }))))
const done = results.filter(x => x && x.r)
const survivors = done.flatMap(d => (d.r.openings || []).map(op => ({ ...op, source: d.key })))
log(`${done.length} analysts returned ${survivors.length} openings`)

phase('Synthesise')
const FINAL = {
  type: 'object',
  properties: {
    openings: { type: 'array', items: { ...OPENING, properties: { ...OPENING.properties, rank_reason: { type: 'string' } } } },
    summary_points: { type: 'array', items: { type: 'string' }, description: '6-8 headline findings for a summary, each one sentence with a number where possible' },
    findings: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, body: { type: 'string', description: '2-4 sentences with evidence (counts, named organisations)' } }, required: ['title', 'body'] }, description: '8-10 numbered findings' },
    openings_intro: { type: 'string', description: 'One paragraph introducing the openings and how they were tested' },
  },
  required: ['openings', 'summary_points', 'findings', 'openings_intro'],
}
const insights = done.map(d => d.kind === 'sector' ? `- ${d.s}: ${d.r.key_insight}` : (d.r.key_insights || []).map(k => `- (${d.key}) ${k}`).join('\n')).join('\n')
const final = await agent(`${COMMON}

You are the synthesiser. Below are ${survivors.length} openings proposed by the analysts (they were not individually tested, so drop or narrow any you know to be already well covered, and say so in rank_reason), and the analysts' key insights. Select the strongest 20-28 openings, merging duplicates (keep the best wording and union the related ids and sectors), and order them from most to least promising for the int/a audience (funders, founders and int/a itself). Each must stay concrete and grounded in the map. Then write 6-8 summary points and 8-10 findings about what the map shows, using ${DIR}/gapin/stats.md for numbers (quote them exactly). Plain British English; no hype.

KEY INSIGHTS:
${insights}

OPENINGS:
${JSON.stringify(survivors.map(o => ({ id: o.id, title: o.title, who: o.who, summary: o.summary, detail: o.detail, steps: o.steps, evidence: o.evidence, sectors: o.sectors, problems: o.problems, related: o.related, confidence: o.confidence })), null, 1)}`,
  { label: 'synthesise', phase: 'Synthesise', schema: FINAL })

return { proposed: survivors.length, final_openings: final ? final.openings.length : 0 }
