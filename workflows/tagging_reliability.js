export const meta = {
  name: 'inta-tagging-reliability',
  description: 'Two independent coders re-tag a stratified sample of 84 organisations without seeing the original tags, to measure agreement',
  phases: [{ title: 'Code', detail: '12 batches x 2 independent coders' }],
}

const DIR = '<scratchpad>'
const N = args.count

const CODES = {
  type: 'object',
  properties: {
    codes: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' },
      tradition: { type: 'array', items: { type: 'string' }, description: 'Home first, then 0-2 secondary' },
      ring: { type: 'string', enum: ['core', 'bridge', 'adjacent', 'potential'] },
      problems: { type: 'array', items: { type: 'string' }, description: '1-3, primary first' },
      quadrants: { type: 'array', items: { type: 'string', enum: ['I', 'We', 'It', 'Its'] } },
      roles: { type: 'array', items: { type: 'string' } },
      org_type: { type: 'string' },
      transfer: { type: 'string' },
      framing: { type: 'string' },
      way_of_knowing: { type: 'string' },
    }, required: ['id', 'tradition', 'ring', 'problems', 'quadrants', 'roles', 'org_type', 'transfer', 'framing', 'way_of_knowing'] } },
  },
  required: ['codes'],
}

const prompt = (n, coder) => `You are coder ${coder} in a reliability check. Read ${DIR}/taxonomy.md carefully: the facet definitions and the tagging guide, rule by rule. Then read ${DIR}/qc/qc-${String(n).padStart(2, '0')}.json: 7 organisations, each with a description but no tags. Tag each one on the facets in the schema, using only keys from taxonomy.md and following the tagging guide's rules and tie-breakers. You may open an organisation's website if the description leaves a facet undecidable. Work independently: do not look for or read any other tagging files in the directory.`

phase('Code')
const res = await parallel(Array.from({ length: N }, (_, n) => n).flatMap(n => ['A', 'B'].map(c => () =>
  agent(prompt(n, c), { label: `code:${String(n).padStart(2, '0')}:${c}`, phase: 'Code', schema: CODES, effort: 'medium' }).then(r => ({ n, c, r })))))
const ok = res.filter(x => x && x.r)
log(`${ok.length}/${N * 2} coding runs returned`)
return { runs: ok.length }
