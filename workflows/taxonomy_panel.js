export const meta = {
  name: 'inta-taxonomy-panel',
  description: 'Four independent categorisation designs for the int/a AI-safety map, scored by two judges, merged by a synthesiser',
  phases: [
    { title: 'Design', detail: 'four designers, each from a different stance' },
    { title: 'Judge', detail: 'two judges score all four schemes' },
    { title: 'Synthesise', detail: 'one synthesiser builds the final multi-facet taxonomy' },
  ],
}

const DIR = '<scratchpad>'

const PREAMBLE = `Read ${DIR}/context.md first: the project brief, who int/a are, and the four rings of proximity (core, bridge, adjacent, potential). The full roster of 552 organisations is ${DIR}/roster_for_taxonomy.txt: read ALL of it, in chunks, before designing anything. ${DIR}/angle_notes.md holds the discovery agents' notes on each search angle (landscape, gaps); ${DIR}/critic_assessment.md is a completeness critic's view. Skim both.

The categorisation you design will drive two things:
1. A written report organised by the scheme.
2. An interactive map for the int/a community: a radial "field mandala" (angular sectors x concentric rings of proximity to the AI-safety core, so that sparse or empty cells reveal blind spots), faceted filters, a field x problem matrix, and entry points for five personas: funders (existing and new), founders, researchers and practitioners from other fields looking for where they fit, AI-safety insiders looking for blind spots, and int/a community members.

A good scheme is legible to people outside int/a, discriminates (entries don't all pile into one bucket), has 8-14 categories on its main facet so a radial layout works, makes gaps visible, and is faithful to the spirit of the brief: widening the field, not re-describing the classic map's functional categories (advocacy, governance, empirical research...).`

const DESIGNERS = [
  { key: 'disciplines', stance: `Your stance: DISCIPLINES AND TRADITIONS. Organise the space by the body of knowledge, practice or tradition each organisation brings to the AI question (complexity science, life sciences, contemplative traditions, democratic theory...). This is the facet the brief most directly asked for ("mapping adjacent fields"). Design sectors that are balanced, roughly mutually exclusive, recognisable to people inside those fields, and arranged so neighbouring sectors are intellectually adjacent (the angular order matters). Decide how to handle organisations that span several fields.` },
  { key: 'problems', stance: `Your stance: PROBLEMS AND THEORIES OF CHANGE. Organise the space by which part of the "make advanced AI go well" problem each organisation works on, and how it expects to make a difference (e.g. understanding agency and intelligence; what to align to; cooperation among many agents; protecting human minds and relationships; legitimate collective governance; resilience and safety practice; moral status of AI; positive visions; the health and wisdom of the people doing the work). This is the facet founders and funders need: where effort goes, and where it doesn't. Avoid reproducing the classic map's functional categories.` },
  { key: 'integral', stance: `Your stance: INTEGRAL. Use int/a's own frames: Wilber's four quadrants (I: interior-individual; We: interior-collective; It: exterior-individual; Its: exterior-collective), levels or scales (person, group, institution, civilisation, planet; or AI system, human-AI dyad, society), inner vs outer work, and int/a's five principles. Test honestly whether each frame actually discriminates among these 552 entries and whether non-integral readers (a new funder, an aisafety.com editor) would understand it. Keep what works, drop what doesn't, and propose how integral frames can be a lens or colour layer even if they aren't the main facet.` },
  { key: 'navigator', stance: `Your stance: NAVIGATOR. Design for use. Think through each persona's real questions ("I fund AI safety and want to see what I'm missing", "I'm a developmental psychologist: who is already doing this?", "I want to found something: where are the empty niches?", "I'm in int/a Berlin: who is near me?"). Propose the practical facets that answer them: what the organisation does (research, convening, funding, training, advocacy, tooling, care and support, media), how to engage (jobs, fellowships, grants, events, communities), maturity and scale, geography, status. Then propose a main facet for the radial layout that serves navigation best, and the persona entry points.` },
]

const DESIGN = {
  type: 'object',
  properties: {
    scheme_name: { type: 'string' },
    thesis: { type: 'string', description: '2-4 sentences: why this organises the space well' },
    facets: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' }, name: { type: 'string' }, question: { type: 'string', description: 'The question this facet answers for a user' },
      cardinality: { type: 'string', enum: ['one', 'many'] },
      categories: { type: 'array', items: { type: 'object', properties: {
        key: { type: 'string' }, label: { type: 'string', description: 'At most 4 words' },
        definition: { type: 'string' }, boundary: { type: 'string', description: 'What looks similar but belongs elsewhere' },
        exemplar_ids: { type: 'array', items: { type: 'string' } },
      }, required: ['key', 'label', 'definition', 'boundary', 'exemplar_ids'] } },
    }, required: ['key', 'name', 'question', 'cardinality', 'categories'] } },
    primary_facet: { type: 'string' },
    assignments: { type: 'string', description: 'EVERY one of the 552 roster ids assigned to one category of the primary facet, as "id=categorykey; id=categorykey; ..."' },
    counts: { type: 'string', description: 'Entries per primary category' },
    what_it_reveals: { type: 'string', description: 'Gaps, blind spots and insights this scheme makes visible, with specifics' },
    weaknesses: { type: 'string' },
  },
  required: ['scheme_name', 'thesis', 'facets', 'primary_facet', 'assignments', 'counts', 'what_it_reveals', 'weaknesses'],
}

phase('Design')
const designs = await parallel(DESIGNERS.map(d => () =>
  agent(`${PREAMBLE}\n\n${d.stance}\n\nDesign a complete scheme: a primary facet plus whatever secondary facets your stance calls for (each with categories, definitions, boundaries and exemplar ids). Assign every roster entry on the primary facet; then count, and if any category holds more than about a fifth of all entries or fewer than about 12, revise. Report what the scheme reveals and where it is weak.`,
    { label: `design:${d.key}`, phase: 'Design', schema: DESIGN }).then(r => ({ key: d.key, r }))))
const ok = designs.filter(x => x && x.r)
log(`${ok.length}/4 designs returned`)

const render = x => `### Scheme "${x.r.scheme_name}" (designer: ${x.key})
Thesis: ${x.r.thesis}
Primary facet: ${x.r.primary_facet}
Facets:
${x.r.facets.map(f => `- ${f.name} [${f.key}; ${f.cardinality}] answers: ${f.question}\n${f.categories.map(c => `   * ${c.label} [${c.key}]: ${c.definition} (Boundary: ${c.boundary}) e.g. ${c.exemplar_ids.join(', ')}`).join('\n')}`).join('\n')}
Counts: ${x.r.counts}
Reveals: ${x.r.what_it_reveals}
Weaknesses: ${x.r.weaknesses}`

const allDesigns = ok.map(render).join('\n\n')

phase('Judge')
const JUDGE = {
  type: 'object',
  properties: {
    scores: { type: 'array', items: { type: 'object', properties: {
      designer: { type: 'string' },
      discriminating: { type: 'integer', minimum: 1, maximum: 10 },
      legibility: { type: 'integer', minimum: 1, maximum: 10 },
      inta_fidelity: { type: 'integer', minimum: 1, maximum: 10 },
      reveals_gaps: { type: 'integer', minimum: 1, maximum: 10 },
      ui_fit: { type: 'integer', minimum: 1, maximum: 10 },
      robustness: { type: 'integer', minimum: 1, maximum: 10, description: 'Would two careful taggers put the same entry in the same place?' },
      comments: { type: 'string' },
    }, required: ['designer', 'discriminating', 'legibility', 'inta_fidelity', 'reveals_gaps', 'ui_fit', 'robustness', 'comments'] } },
    best_ideas_to_graft: { type: 'array', items: { type: 'string' } },
    recommendation: { type: 'string', description: 'Which facet should be the radial sectors, which the colour, which the matrix axes, and why' },
  },
  required: ['scores', 'best_ideas_to_graft', 'recommendation'],
}
const judgeLens = [
  'You judge as a skeptical new funder and an aisafety.com map editor: is it legible, does it help allocate money and attention, is it robust?',
  'You judge as an int/a steward and an interdisciplinary facilitator: does it honour full-spectrum knowing and widening the field, does it surface blind spots, would people from other disciplines recognise themselves in it?',
]
const judgements = await parallel(judgeLens.map((lens, i) => () =>
  agent(`${PREAMBLE}\n\n${lens}\n\nScore each of the following categorisation schemes (1-10 on each criterion), spot-check assignments against the roster file, list the best ideas worth grafting from each, and recommend the final facet roles.\n\n${allDesigns}`,
    { label: `judge:${i + 1}`, phase: 'Judge', schema: JUDGE })))

phase('Synthesise')
const FINAL = {
  type: 'object',
  properties: {
    facets: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' }, name: { type: 'string' }, question: { type: 'string' },
      cardinality: { type: 'string', enum: ['one', 'many'] },
      role_in_ui: { type: 'string' },
      categories: { type: 'array', items: { type: 'object', properties: {
        key: { type: 'string', description: 'short kebab-case' }, label: { type: 'string', description: 'At most 4 words' }, chip: { type: 'string', description: 'At most 2 words' },
        definition: { type: 'string' }, boundary: { type: 'string' }, exemplar_ids: { type: 'array', items: { type: 'string' } },
      }, required: ['key', 'label', 'chip', 'definition', 'boundary', 'exemplar_ids'] } },
    }, required: ['key', 'name', 'question', 'cardinality', 'role_in_ui', 'categories'] } },
    radial_layout: { type: 'object', properties: {
      sector_facet: { type: 'string' }, ring_facet: { type: 'string' }, color_facet: { type: 'string' },
      sector_order: { type: 'array', items: { type: 'string' } }, order_rationale: { type: 'string' },
    }, required: ['sector_facet', 'ring_facet', 'color_facet', 'sector_order', 'order_rationale'] },
    matrix: { type: 'object', properties: { rows_facet: { type: 'string' }, cols_facet: { type: 'string' }, why: { type: 'string' } }, required: ['rows_facet', 'cols_facet', 'why'] },
    tagging_guide: { type: 'string', description: 'Precise instructions a profiler follows to tag one organisation on every facet, with tie-breakers and worked examples' },
    persona_entry_points: { type: 'array', items: { type: 'object', properties: {
      persona: { type: 'string' }, their_question: { type: 'string' }, view: { type: 'string', description: 'Which view and filters answer it' },
    }, required: ['persona', 'their_question', 'view'] } },
    rationale: { type: 'string' },
    open_questions: { type: 'string' },
  },
  required: ['facets', 'radial_layout', 'matrix', 'tagging_guide', 'persona_entry_points', 'rationale', 'open_questions'],
}
const final = await agent(`${PREAMBLE}\n\nYou are the synthesiser. Four designers proposed schemes and two judges scored them. Build the final multi-facet taxonomy: take the strongest primary facet, graft the best ideas, and keep it buildable. Requirements:
- Facets must include: the main field/tradition facet (8-14 categories, for the radial sectors, single-valued "home" plus optional secondary), the ring facet (core, bridge, adjacent, potential: keep these four exactly, with sharpened definitions), a problem/aim facet (multi-valued), an integral quadrant facet (I, We, It, Its; multi-valued) if the judges found it useful as a lens, a role facet (what the organisation does; multi-valued), and an organisation-type facet. Add others only if they clearly earn their place.
- Every category gets a key, label, chip, definition, boundary and exemplar ids taken from the roster.
- Give the angular order of the sectors so neighbours are intellectually adjacent.
- Write a tagging guide precise enough that ~80 different profiling agents tag consistently.

DESIGNS:
${allDesigns}

JUDGEMENTS:
${judgements.filter(Boolean).map((j, i) => `Judge ${i + 1}:\n${j.scores.map(s => `- ${s.designer}: disc ${s.discriminating}, leg ${s.legibility}, int/a ${s.inta_fidelity}, gaps ${s.reveals_gaps}, ui ${s.ui_fit}, robust ${s.robustness}. ${s.comments}`).join('\n')}\nGraft: ${j.best_ideas_to_graft.join(' | ')}\nRecommendation: ${j.recommendation}`).join('\n\n')}`,
  { label: 'synthesise', phase: 'Synthesise', schema: FINAL })

return { final, designs: ok.map(x => ({ key: x.key, scheme_name: x.r.scheme_name, primary_facet: x.r.primary_facet, counts: x.r.counts, assignments: x.r.assignments, reveals: x.r.what_it_reveals })), judgements }
