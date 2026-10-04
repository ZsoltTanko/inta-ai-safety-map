export const meta = {
  name: 'inta-blind-spot-sweep',
  description: 'Second discovery pass over traditions, disciplines and regions the first sweep missed, with explicit searched-none-found notes',
  phases: [
    { title: 'Sweep', detail: '10 finders over absent traditions and regions' },
  ],
}

const DIR = '<scratchpad>'

const CANDIDATE = {
  type: 'object',
  properties: {
    name: { type: 'string' }, url: { type: 'string' },
    kind: { type: 'string', enum: ['nonprofit/research org', 'academic lab/centre', 'programme/fellowship', 'funder', 'network/community/coalition', 'company/startup', 'publication/media', 'project/initiative', 'membership body', 'public body'] },
    one_line: { type: 'string' }, field_lens: { type: 'string' }, ai_connection: { type: 'string' },
    ring: { type: 'string', enum: ['core', 'bridge', 'adjacent', 'potential'] },
    proposed_home: { type: 'string', description: 'Home tradition key from taxonomy.md' },
    location: { type: 'string' },
    status: { type: 'string', enum: ['active', 'inactive/closed', 'unclear'] },
    evidence_urls: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['name', 'url', 'kind', 'one_line', 'field_lens', 'ai_connection', 'ring', 'proposed_home', 'status', 'evidence_urls', 'confidence'],
}
const OUT = {
  type: 'object',
  properties: {
    candidates: { type: 'array', items: CANDIDATE },
    searched: { type: 'array', items: { type: 'object', properties: {
      sub_angle: { type: 'string' },
      result: { type: 'string', enum: ['found', 'searched_none_found', 'thin'] },
      note: { type: 'string', description: 'What exists, what does not, and what that means for the map (one or two sentences)' },
    }, required: ['sub_angle', 'result', 'note'] } },
  },
  required: ['candidates', 'searched'],
}

const ANGLES = [
  { key: 'education', title: 'Education and the learning sciences', subs: 'AI literacy and AI-risk education for publics and schools; teachers and their unions on AI; learning scientists studying cognitive offloading and deskilling; university-level AI-safety curricula outside CS (e.g. MIT RAISE / Day of AI, TeachAI, Digital Promise, AI4K12, EDUCAUSE, OECD education).' },
  { key: 'anthropology', title: 'Anthropology, history and archaeology of technology', subs: 'Anthropologists and ethnographers of AI labs and AI safety communities; historians of technology and of risk (nuclear, biotech) writing on AI; societies such as SHOT, EASST, 4S, EPIC; projects on the history of AI risk ideas.' },
  { key: 'language', title: 'Linguistics and the language sciences', subs: 'Linguists and language-science societies engaging LLM risks, meaning, language endangerment by AI, and language-model interpretability from linguistics (e.g. Linguistic Society of America, ACL ethics, computational semantics groups).' },
  { key: 'library', title: 'Library, archive and information science', subs: 'Libraries, archives and information-science bodies on AI provenance, knowledge commons, data stewardship and information integrity (e.g. IFLA, Internet Archive, Data Provenance Initiative, Library Futures, Software Heritage).' },
  { key: 'audit', title: 'Accounting, audit, actuarial science and finance', subs: 'Professional bodies and standards setters for audit and assurance of AI (ICAEW, IIA, AICPA, IAASB), actuarial work on AI risk (Institute and Faculty of Actuaries, Society of Actuaries), central-bank and financial-stability work on AI systemic risk (BIS, FSB, Bank of England).' },
  { key: 'statistics', title: 'Statistics, operations research and decision analysis', subs: 'Royal Statistical Society, American Statistical Association, INFORMS, decision-analysis and expert-elicitation communities, and reliability statisticians engaging AI evaluation, uncertainty and risk.' },
  { key: 'epidemiology', title: 'Epidemiology and public health of AI harms', subs: 'Public-health framings of AI (harm surveillance, population mental health, a "public health approach" to AI), WHO and national public-health institutes on AI, epidemiologists studying chatbot-associated harms, toxicology-style approaches.' },
  { key: 'faiths', title: 'Under-covered faith and contemplative traditions', subs: 'Hindu, Sikh, Jain, Shinto and Bahá\'í institutions on AI; Sufi orders and Islamic spirituality; Christian contemplative networks (e.g. Center for Action and Contemplation, Contemplative Outreach, Benedictine and Jesuit work on AI); Daoist and Confucian thought applied to AI (beyond Berggruen and Beijing-AISI); Japanese Buddhist and Shinto robotics/AI ethics.' },
  { key: 'europe', title: 'Continental Europe, especially Berlin and Paris (int/a hubs)', subs: 'AI-safety, AI-and-society, contemplative, metamodern and interdisciplinary groups based in Berlin, Paris and wider Germany and France (and Amsterdam, Copenhagen, Vienna, Zurich) that bring non-ML disciplines to AI risk: e.g. interface (formerly SNV), AI Safety Berlin, Paris AI safety groups, ENS and Sorbonne centres, Max Planck institutes, Fondation Jean-Jaurès, Institut Montaigne, Agence Française de Développement, Zurich and ETH centres.' },
  { key: 'asia_latam', title: 'Japan, South and Southeast Asia, and Latin America', subs: 'Japan AISI and RIKEN AIP ELSI, Japanese philosophy-of-technology groups, Korean and Singaporean AI-safety and ethics centres with interdisciplinary angles, Indian contemplative or civilisational perspectives on AI, Latin American AI-safety and AI-ethics groups (Brazil, Mexico, Chile, Argentina, Colombia) beyond those already listed.' },
]

const prompt = a => `Read ${DIR}/context.md (scope and the four rings) and skim ${DIR}/taxonomy.md (the traditions; give each candidate a proposed_home key from it). ${DIR}/roster_names.txt lists the 552 organisations already on the map: return only organisations NOT on it (check names and URLs).

This is a blind-spot sweep. The first sweep missed this area entirely or nearly so:
${a.title}
Sub-angles to cover: ${a.subs}

Search thoroughly (at least 15 WebSearch queries, in other languages where it helps; load WebSearch and WebFetch with ToolSearch if they are deferred). Confirm each candidate on its own site or a recent source, and confirm its AI engagement concretely. Return every organisation that fits the scope, including ring "potential" ones whose knowledge is plainly relevant (name the transferable method in ai_connection). For each sub-angle, also report whether you found something, found it thin, or searched and found nothing: an honest "searched, none found" is a result the map will show. Don't pad.`

phase('Sweep')
const res = await parallel(ANGLES.map(a => () => agent(prompt(a), { label: `blind:${a.key}`, phase: 'Sweep', schema: OUT }).then(r => ({ key: a.key, r }))))
const ok = res.filter(x => x && x.r)
log(`${ok.length}/${ANGLES.length} finders returned; ${ok.reduce((n, x) => n + x.r.candidates.length, 0)} candidates`)
return { counts: ok.map(x => `${x.key}: ${x.r.candidates.length}`) }
