export const meta = {
  name: 'inta-profile-and-verify-b',
  description: 'Research and tag every organisation on the int/a AI-safety map in batches of 7, then adversarially fact-check each batch',
  phases: [
    { title: 'Profile', detail: '79 batches of 7 organisations' },
    { title: 'Verify', detail: 'an independent fact-checker per batch' },
  ],
}

const DIR = '<scratchpad>'
const BATCHES = Array.from({ length: args.end - args.start }, (_, i) => args.start + i)

const PROFILE = {
  type: 'object',
  properties: {
    id: { type: 'string', description: 'The roster id, unchanged' },
    include: { type: 'boolean', description: 'false only if it does not exist, is out of scope, or is closed with no lasting relevance' },
    exclude_reason: { type: 'string' },
    name: { type: 'string', description: 'Official name; acronym in parentheses if commonly used' },
    short_name: { type: 'string', description: 'Label for a map, at most 24 characters (acronym or short form)' },
    url: { type: 'string', description: 'Official homepage (or programme page) that resolves today' },
    summary: { type: 'string', description: '2-3 plain sentences: what it is and what it concretely does. Specific, no hype, no adjectives like leading/pioneering unless quantified.' },
    why_it_matters: { type: 'string', description: '1-2 sentences: what it brings to making AI go well that the mainstream AI-safety field lacks, or why an int/a reader should care. Concrete.' },
    key_work: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, year: { type: 'string' }, url: { type: 'string' } }, required: ['title', 'year'] }, description: '1-4 notable outputs, programmes, papers or events' },
    people: { type: 'array', items: { type: 'string' }, description: '1-4 key people as "Name (role)"' },
    founded: { type: 'string', description: 'Year, or "" if unknown' },
    hq: { type: 'string', description: '"City, Country", or "Distributed"' },
    scale: { type: 'string', enum: ['solo or tiny (<5)', 'small (5-25)', 'medium (25-100)', 'large (100+)', 'programme in a larger org', 'network or community', 'unknown'] },
    funding: { type: 'string', description: 'Known funders, budget or grant sizes, with years; "" if unknown' },
    status_evidence: { type: 'string', description: 'Most recent dated activity you found, e.g. "Sep 2026: published X"' },
    on_classic_map: { type: 'boolean', description: 'Listed in aisafety_map.json (check by name)' },
    engage: { type: 'array', items: { type: 'string' }, description: 'Verified ways to get involved: fellowships, jobs, grants, events, communities, newsletters, with timing where known' },
    caveats: { type: 'string', description: 'Controversies, pivots, uncertainty, or reasons for caution; "" if none' },
    tags: { type: 'object', description: 'Keys from taxonomy.md only', properties: {
      tradition: { type: 'array', items: { type: 'string' }, description: 'Home first, then 0-2 secondary (up to 4 for generalist funders)' },
      sub_tradition: { type: 'string', description: 'Within the home tradition (key prefix matches home)' },
      ring: { type: 'string', enum: ['core', 'bridge', 'adjacent', 'potential'] },
      problems: { type: 'array', items: { type: 'string' }, description: '1-3, primary first' },
      quadrants: { type: 'array', items: { type: 'string', enum: ['I', 'We', 'It', 'Its'] }, description: '1-2, main first' },
      roles: { type: 'array', items: { type: 'string' }, description: '1-3, main first' },
      org_type: { type: 'string' },
      transfer: { type: 'string' },
      framing: { type: 'string' },
      way_of_knowing: { type: 'string' },
      region: { type: 'string', enum: ['north_america', 'uk_ireland', 'europe', 'asia_pacific', 'africa', 'latin_america', 'mena', 'global'] },
      standpoint: { type: 'string', enum: ['indigenous_led', 'majority_world', 'neither'] },
      inta_hubs: { type: 'array', items: { type: 'string', enum: ['london', 'berlin', 'paris', 'online'] } },
      engagement: { type: 'array', items: { type: 'string', enum: ['jobs', 'fellowships', 'grants', 'events', 'courses', 'community', 'contribute', 'partner'] } },
      status: { type: 'string', enum: ['active', 'new', 'dormant', 'changed', 'unverified'] },
      badges: { type: 'array', items: { type: 'string', enum: ['full_spectrum', 'speed_of_wisdom', 'recoupling', 'fractal', 'inner_outer'] }, description: 'Rare: about one entry in ten, at most two' },
    }, required: ['tradition', 'sub_tradition', 'ring', 'problems', 'quadrants', 'roles', 'org_type', 'transfer', 'framing', 'way_of_knowing', 'region', 'standpoint', 'inta_hubs', 'engagement', 'status', 'badges'] },
    tag_notes: { type: 'string', description: 'One sentence of evidence each for home, ring and transfer; rule codes used; the transferable method if ring = potential; MISFIT flags' },
    sources: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['id', 'include', 'name', 'short_name', 'url', 'summary', 'why_it_matters', 'key_work', 'people', 'founded', 'hq', 'scale', 'funding', 'status_evidence', 'on_classic_map', 'engage', 'caveats', 'tags', 'tag_notes', 'sources', 'confidence'],
}
const PROFILES = { type: 'object', properties: { profiles: { type: 'array', items: PROFILE } }, required: ['profiles'] }

const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' },
      verdict: { type: 'string', enum: ['ok', 'corrected', 'reject'] },
      corrections: { type: 'string', description: 'JSON object of field -> corrected value (same field names and types as the profile, tags as a whole object if changed); "{}" if none' },
      notes: { type: 'string', description: 'What you checked, what was wrong, and your sources' },
    }, required: ['id', 'verdict', 'corrections', 'notes'] } },
  },
  required: ['verdicts'],
}

const profilePrompt = (n) => `Read ${DIR}/context.md (the brief and scope) and ${DIR}/taxonomy.md (the controlled vocabularies and tagging guide; use ONLY its keys in tags). ${DIR}/aisafety_map.json is the classic aisafety.com map, for on_classic_map.

Your batch is ${DIR}/batches/batch-${String(n).padStart(2, '0')}.json: 7 organisations found by discovery agents, each with a draft description, evidence URLs and sometimes merged sub-entries ("merged_from", which you should fold into one profile). Today is 2026-10-04.

For each organisation, research it properly: open its official site and at least one independent or recent source (load WebSearch and WebFetch with ToolSearch if deferred). Confirm it exists, what it actually does, who runs it, when and where it was founded, how it is funded, and whether it is active in 2026 (find the most recent dated activity). Then tag it, following the tagging guide in taxonomy.md rule by rule (each entry carries a provisional_home from the taxonomy panel: a starting point, not a decision). Then write the profile. Write plainly and specifically, in British English; describe what the organisation is, not how impressive it is. Don't invent: leave a field empty rather than guess, and lower confidence when sources are thin. Set include=false only for entries that don't exist, are clearly out of scope, or closed without lasting relevance (a closed organisation whose absence is itself informative, like AI Safety Support, stays in with status closed).

Return one profile per roster id, ids unchanged.`

const verifyPrompt = (n, profiles) => `You are an adversarial fact-checker. Read ${DIR}/context.md and ${DIR}/taxonomy.md. Below are 7 organisation profiles written by another agent for a public map. Your job is to find what is wrong. Today is 2026-10-04.

For each profile, check independently with WebSearch/WebFetch (load them via ToolSearch if deferred): does the URL resolve to the official site; is the status right (look for the most recent dated activity yourself); are founded year, location, key people and funding claims right; is any key_work misattributed or misdated; does the summary overstate; is the ring right (core = AI-safety org; bridge = rooted elsewhere but explicitly working on AI safety or AI going well; adjacent = AI's human or societal effects without an x-risk framing; potential = relevant knowledge, little AI engagement); are tags valid keys from taxonomy.md and sensible. Return verdict ok, corrected (with a JSON object of corrected fields) or reject (doesn't exist / out of scope), with brief notes and sources. Be concrete; don't rewrite style for its own sake.

PROFILES (batch ${n}):
${JSON.stringify(profiles, null, 1)}`

phase('Profile')
const results = await pipeline(
  BATCHES.map(n => ({ n })),
  b => agent(profilePrompt(b.n), { label: `profile:${String(b.n).padStart(2, '0')}`, phase: 'Profile', schema: PROFILES }),
  (r, b) => r ? agent(verifyPrompt(b.n, r.profiles), { label: `verify:${String(b.n).padStart(2, '0')}`, phase: 'Verify', schema: VERDICTS, effort: 'medium' })
    .then(v => ({ n: b.n, profiles: r.profiles, verdicts: v ? v.verdicts : [] })) : null,
)

const done = results.filter(Boolean)
const missing = BATCHES.filter(n => !done.find(d => d.n === n))
let corrected = 0, rejected = 0
for (const d of done) for (const v of d.verdicts) { if (v.verdict === 'corrected') corrected++; if (v.verdict === 'reject') rejected++ }
log(`${done.length}/${BATCHES.length} batches done; ${corrected} corrected, ${rejected} rejected; missing batches: ${missing.join(',') || 'none'}`)
return { batches_done: done.length, missing, corrected, rejected }
