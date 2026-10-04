# The Wider Field

A map of organisations that bring knowledge from outside mainstream AI safety to making advanced AI go well, made for the integral altruism (int/a) community in October 2026.

- **Interactive map:** https://claude.ai/artifact/MrKYZmhwbuxCf2tf3cmcnw
- **Report:** https://claude.ai/artifact/ThNQqeD4nn1caCT9ihWwHL

722 organisations are placed by the tradition of knowledge they bring (14 traditions in four families) and by their distance from the AI-safety core (four rings: core, bridge, adjacent, potential). The report adds findings, 42 ranked openings for founders, funders and int/a, a funders section, and the method and its limits.

## Layout

| Path | What it is |
|---|---|
| `dist/` | The built pages, as published: `wider-field-map.html` and `wider-field-report.html` |
| `src/` | Templates and build scripts for both pages |
| `src/pipeline/` | Scripts that ran against the research agents' outputs during the original session; kept as a record, not runnable from this repo |
| `data/` | The verified dataset (`profiles.json`), the taxonomy, the analysts' notes, the synthesis, and fact-check and reliability results |
| `research/` | The brief, the seed list, discovery notes, candidate lists and the categorisation panel's output |
| `workflows/` | The multi-agent workflow scripts that did the discovery, categorisation, profiling, fact-checking and gap analysis (their `DIR` paths pointed at a scratch folder) |

## Rebuilding the pages

Python 3, no dependencies.

```bash
python3 src/synth.py
```

```bash
python3 src/assemble.py
```

```bash
python3 src/build_map.py
```

```bash
python3 src/build_report.py
```

`synth.py` selects and ranks the openings and writes the findings and essays into `data/synthesis.json`. `assemble.py` combines that with the analysts' notes and the fixed texts in `src/texts.py` into `data/map_extra.json`. The two build scripts write the pages into `dist/`. `assemble.py` takes the map and report links as optional arguments.

To change an organisation, edit its entry in `data/profiles.json` (tags must use keys from `data/taxonomy.md`) and rebuild.

## How it was made, and its limits

AI research agents swept 18 adjacent fields and then a second set of blind spots, profiled each organisation from its own site and other sources, and tagged it against the written rules in `data/taxonomy.md`. A second agent fact-checked every profile and corrected 268 of them. Two further coders re-tagged a sample blind to check consistency. The full method is in the report.

- Expect errors in individual entries, especially dates, people and funding. Every entry lists its sources.
- The research agents' web-search budget ran out early, so most checking was done by reading organisations' own sites.
- Coverage leans English-language: 55% of entries are in North America or the UK and Ireland.
- The openings were not individually tested against the open web; ten were spot-checked.
- The aisafety.com field map was used to mark which organisations it already lists; that copy is not included here.
