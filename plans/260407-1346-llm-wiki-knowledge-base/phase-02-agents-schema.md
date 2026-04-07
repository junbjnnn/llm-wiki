# Phase 2: AGENTS.md Schema & Page Templates

## Context Links
- [Schema Compatibility Research](../reports/researcher-01-markitdown-and-schema-compatibility.md)
- [Wiki Patterns Research](../reports/researcher-260407-qmd-and-wiki-patterns.md)
- [AGENTS.md spec](https://github.com/agentsmd/agents.md)

## Overview
- **Priority:** P1 (schema is the brain of the wiki)
- **Status:** Complete
- **Effort:** 3h
- **Description:** Write AGENTS.md (universal schema), create index.md, log.md, page templates

## Key Insights
- AGENTS.md must be self-contained — any AI tool reading it should know how to operate the wiki without additional context
- Keep < 200 lines (adherence drops with larger files per Claude research)
- Three core workflows: Ingest, Query, Lint (from Karpathy)
- 10 page types with strict frontmatter schema
- [[wikilink]] cross-refs (Obsidian compatible, widely understood by LLMs)

## Requirements

### Functional
- AGENTS.md covering: wiki conventions, page naming, frontmatter schema, cross-ref rules, all 3 workflows (ingest/query/lint), page type templates
- index.md initial structure (auto-maintained catalog)
- log.md initial structure (append-only activity log)
- Example pages in wiki/ demonstrating each page type

### Non-Functional
- AGENTS.md must be parseable by generate-tool-configs.py (Phase 4) — use clear section headers
- Instructions must be imperative and unambiguous (AI tools follow literal instructions)

## Architecture

### AGENTS.md Section Structure
```
# [Wiki Name] Knowledge Base

## About This Wiki
## Conventions
  ### Page Naming
  ### Frontmatter Schema
  ### Cross-References
  ### Confidence Levels
## Workflows
  ### Ingest
  ### Query
  ### Lint
## Page Types
  ### summary | entity | concept | comparison | synthesis | chronicle | adr | runbook | postmortem
## Scripts
## Directory Structure
```

### Data Flow: Ingest Workflow (raw → sources/)
```
User provides file → scripts/ingest.py parses to markdown →
save parsed markdown to sources/{category}/ → done (no AI yet)
```

### Data Flow: Compile Workflow (sources/ → wiki/)
```
AI reads uncompiled sources (not yet in wiki) →
AI creates summary page in wiki/summaries/ →
AI creates/updates entity + concept pages →
AI adds [[wikilinks]] cross-references →
AI updates index.md → AI appends to log.md → git commit
```

### Data Flow: Query Workflow (with mandatory feedback loop)
```
User asks question → AI searches wiki (index.md/grep/qmd) →
AI reads relevant pages → AI synthesizes answer →
AI evaluates: "Does this answer contain NEW insights?" →
  YES → create wiki page (synthesis/concept) + update cross-refs →
         update index.md → log mutation to log.md
  NO  → done (no log — queries are reads, not mutations)
This feedback loop is MANDATORY, not optional.
```

### Data Flow: Compile Update Detection
```
New source ingested → AI scans existing wiki/summaries/ →
  Check: any page with similar source in frontmatter `sources` field?
  YES → UPDATE existing page (don't create duplicate) + update sources field
  NO  → CREATE new summary + entity/concept pages
```

### log.md Rules
log.md tracks MUTATIONS only (state changes to wiki):
- ingest, compile, digest, lint-fix, direct edits → log
- query (read-only) → do NOT log
- query that creates new page → log the page creation, not the query

## Related Code Files

### Files to Create
```
AGENTS.md
CLAUDE.md              # Claude-specific additions (maintained manually, not auto-generated)
index.md
log.md
wiki/summaries/_template.md
wiki/entities/_template.md
wiki/concepts/_template.md
wiki/comparisons/_template.md
wiki/syntheses/_template.md
wiki/chronicles/_template.md
wiki/decisions/_template.md
wiki/runbooks/_template.md
wiki/postmortems/_template.md
wiki/glossary.md
```

## Implementation Steps

1. **Write AGENTS.md** — the core schema file:
   - Header: wiki name, purpose, tool-agnostic notice
   - Conventions: kebab-case filenames, YAML frontmatter (all required fields), [[wikilink]] format, confidence levels
   - Ingest workflow: `scripts/ingest.py` parse → save to sources/ (no AI)
   - Batch-ingest workflow: scan folder → process all files → pause every 5 for progress
   - Compile workflow: AI reads uncompiled sources → auto route short/long content → create/update wiki pages
     - Long content (>1000 chars): full processing (summary + entities + concepts + cross-refs)
     - Short content (≤1000 chars): simplified (summary only, mark concepts as [pending])
   - Query workflow: search → synthesize → **mandatory feedback loop** (file insights back into wiki)
   - Digest workflow: deep cross-source synthesis → always creates comprehensive report in wiki/syntheses/
   - Lint workflow: check orphans, broken links, stale pages, missing frontmatter, contradictions
   - Graph workflow: `scripts/graph.py` scan wikilinks → generate Mermaid diagram → wiki/knowledge-graph.md
   - Page type definitions with inline templates (compact)
   - Scripts section: how to call each script, what it does
   - Directory structure reference

2. **Create index.md**:
   ```markdown
   ---
   title: Wiki Index
   updated: 2026-04-07
   ---
   # Wiki Index

   > Auto-maintained catalog. Rebuild: `python scripts/update-index.py`

   ## By Type
   <!-- Auto-generated sections below -->

   ## Recently Updated
   <!-- Auto-generated -->
   ```

3. **Create log.md**:
   ```markdown
   ---
   title: Activity Log
   ---
   # Activity Log

   > Append-only. Format: `| YYYY-MM-DD | action | details | author |`

   | Date | Action | Details | Author |
   |------|--------|---------|--------|
   ```

4. **Create page templates** (`_template.md` in each wiki subdir):
   - Each template has full frontmatter with placeholder values
   - Each template has section structure specific to its page type
   - Templates serve as reference for AI tools AND human editors

5. **Create glossary.md**:
   ```markdown
   ---
   title: Glossary
   type: glossary
   tags: [reference]
   created: 2026-04-07
   updated: 2026-04-07
   ---
   # Glossary

   > Domain-specific terminology. Format: `**Term** — Definition. See [[related-page]].`
   ```

## Todo List

- [x] Write AGENTS.md (< 200 lines, all sections)
- [x] Create index.md with auto-gen placeholders
- [x] Create log.md with table format
- [x] Create _template.md for: summary, entity, concept
- [x] Create _template.md for: comparison, synthesis, chronicle
- [x] Create _template.md for: adr (decision), runbook, postmortem
- [x] Create glossary.md
- [x] Validate: all page types referenced in AGENTS.md have templates
- [x] Validate: AGENTS.md sections parseable for Phase 4 generation

## Success Criteria
- AI tool (Claude/Cursor/etc.) reading AGENTS.md can correctly ingest a document without further instruction
- All 10 page types have templates with valid frontmatter
- index.md and log.md have clear format specifications
- AGENTS.md < 200 lines

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| AGENTS.md too long (>200 lines) | High | Medium | Use compact template syntax; link to _template.md files for details |
| AI tools interpret instructions differently | Medium | Medium | Use imperative language, numbered steps, explicit examples |
| Schema too rigid for diverse projects | Low | Medium | .llm-wiki.toml overrides for project-specific customization |

## Security Considerations
- AGENTS.md may contain project-specific conventions — review before making repo public
- No secrets in schema file; config file (.llm-wiki.toml) also secret-free by design

## Next Steps
- Phase 3 (scripts) reads frontmatter schema from this phase
- Phase 4 (tool config gen) parses AGENTS.md sections
- Phase 7 (docs) references AGENTS.md conventions
