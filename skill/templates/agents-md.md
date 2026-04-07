# {wiki_name} Knowledge Base

> Tool-agnostic wiki. Any AI tool reading this file can operate this wiki.

## About

Git-based markdown wiki. Sources in `sources/`, generated pages in `wiki/`. Config in `.llm-wiki.toml`.

## Conventions

- **Filenames:** `kebab-case.md` (e.g., `api-gateway-overview.md`)
- **Frontmatter:** Every wiki page MUST have YAML frontmatter with: `title`, `type`, `tags`, `created`, `updated`
- **Cross-refs:** Use `[[page-name]]` wikilinks (Obsidian compatible). Target = filename without `.md`
- **Confidence:** Tag pages `confidence: high|medium|low`. Default: `medium`
- **Language:** {language}

## Workflows

### Ingest (script — no AI needed)
1. Run: `python scripts/ingest.py <file_or_url> --category <category>`
2. Script parses file → saves markdown to `sources/<category>/`
3. No AI involvement. Pure file conversion.

### Batch-Ingest
1. Run: `python scripts/ingest.py <folder> --category <category>`
2. Processes all supported files in folder. Pauses every 5 for progress report.

### Compile (AI-powered)
1. Scan `sources/` for files not yet summarized in `wiki/summaries/`
2. For each uncompiled source:
   - **Long content (>1000 chars):** Create `wiki/summaries/<name>.md` + extract entities → `wiki/entities/` + extract concepts → `wiki/concepts/` + add `[[wikilinks]]`
   - **Short content (≤1000 chars):** Create summary only, mark concepts as `[pending]`
3. **Update detection:** Check `wiki/summaries/` for existing page with same source in frontmatter `sources` field → UPDATE don't duplicate
4. Run: `python scripts/update-index.py`
5. Append to `log.md`: `| <date> | compile | <details> | <author> |`
6. Git commit: `docs: compile N new sources`

### Query (AI-powered — mandatory feedback loop)
1. Search wiki: read `index.md`, grep for keywords, or `qmd query` if available
2. Read relevant pages → synthesize answer for user
3. **MANDATORY:** Evaluate: "Does this answer contain NEW insights not in wiki?"
   - **YES →** Create new page (synthesis/concept) + update cross-refs + update index + log mutation
   - **NO →** Done (no log — queries are reads, not mutations)

### Digest (AI-powered — deep synthesis)
1. Read ALL sources and wiki pages related to `<topic>`
2. Cross-reference, find patterns, contradictions, gaps
3. Create comprehensive report: `wiki/syntheses/digest-<topic>.md`
4. Always creates a page. Always logs to `log.md`.

### Lint
1. Run: `python scripts/lint.py`
2. Review output: orphans, broken links, stale pages, missing frontmatter
3. Fix issues. Run lint again until clean.

### Graph
1. Run: `python scripts/graph.py`
2. Generates `wiki/knowledge-graph.md` with Mermaid diagram of all wikilinks

## Page Types

| Type | Dir | Use for |
|------|-----|---------|
| summary | wiki/summaries/ | Source document summaries |
| entity | wiki/entities/ | People, systems, tools, services |
| concept | wiki/concepts/ | Ideas, patterns, methodologies |
| comparison | wiki/comparisons/ | X vs Y analysis |
| synthesis | wiki/syntheses/ | Cross-source insights, digests |
| chronicle | wiki/chronicles/ | Timeline events, milestones |
| adr | wiki/decisions/ | Architecture Decision Records |
| runbook | wiki/runbooks/ | How-to procedures |
| postmortem | wiki/postmortems/ | Incident analysis |

See `_template.md` in each subdirectory for frontmatter schema.

## log.md Rules

Log MUTATIONS only: ingest, compile, digest, lint-fix, direct edits.
Do NOT log read-only queries. Log page creation from query feedback loop.
Format: `| YYYY-MM-DD | action | details | author |`

## Scripts

| Command | Description |
|---------|-------------|
| `python scripts/ingest.py <file>` | Parse file → markdown |
| `python scripts/update-index.py` | Rebuild index.md |
| `python scripts/lint.py` | Check wiki health |
| `python scripts/stats.py` | Wiki statistics |
| `python scripts/graph.py` | Generate knowledge graph |
| `bash scripts/setup-qmd.sh` | Setup qmd search (optional) |

## Search Strategy

- **< 100 pages:** Read `index.md` + `grep -ri "keyword" wiki/`
- **100+ pages:** Use `qmd query "question"` if available, fallback grep
- **qmd commands:** `qmd query "question" --collection wiki` | `qmd search "keyword" --collection wiki`

## Directory Structure

```
sources/          — Raw parsed documents (8 categories)
  product/ design/ architecture/ development/
  operations/ meetings/ references/ data/
wiki/             — AI-generated pages (9 types + glossary)
  summaries/ entities/ concepts/ comparisons/
  syntheses/ chronicles/ decisions/ runbooks/ postmortems/
  glossary.md
scripts/          — Python utilities
index.md          — Auto-maintained catalog
log.md            — Append-only mutation log
```
