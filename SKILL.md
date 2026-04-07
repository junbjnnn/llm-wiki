---
name: llm-wiki
description: "Build and maintain a git-based markdown wiki for software teams. Use when user mentions wiki, knowledge base, llm-wiki, ingest documents, compile sources, or query project knowledge."
license: MIT
compatibility: Requires Python 3.11+ and git
metadata:
  author: junbjnnn
  version: "1.0"
---

# llm-wiki — Knowledge Base Manager

> Activate with `/wiki` prefix. Git-based markdown wiki for software teams.

## Commands

### `/wiki init [--name "Name"] [--language en] [--with-qmd]`
Initialize wiki in current project.
1. Run: `python scripts/init-wiki.py --name "Project Name" --language en --target .`
2. Verify: check `.wiki/` created with AGENTS.md, sources/, wiki/
3. Commit: `git add .wiki/ && git commit -m "docs: initialize llm-wiki"`

### `/wiki ingest <file_or_url> [--category <cat>]`
Parse document into wiki source (no AI needed).
1. Run: `python scripts/ingest.py <file> --category <category> --output .wiki/sources/<category>/`
2. Categories: product, design, architecture, development, operations, meetings, references, data
3. Report: "Ingested <file> → .wiki/sources/<category>/<name>.md"

### `/wiki batch-ingest <folder> [--category <cat>]`
Ingest all files in a folder.
1. Run: `python scripts/ingest.py <folder> --category <category>`
2. Script pauses every 5 files for progress. Report total when done.

### `/wiki compile`
AI reads uncompiled sources → creates wiki pages.
1. Scan `.wiki/sources/` for files not yet in `.wiki/wiki/summaries/`
2. For each uncompiled source:
   - Read source content
   - **Long (>1000 chars):** Create summary + entities + concepts + wikilinks
   - **Short (≤1000 chars):** Create summary only, concepts as [pending]
   - **Check duplicates:** Search existing summaries by `sources` frontmatter field → update don't duplicate
3. Save pages to `.wiki/wiki/<type>/` with full frontmatter
4. **Conflict detection:** If new source contradicts existing content:
   - Add `> ⚠️ Conflict: [[source-a]] states X, but [[source-b]] states Y.` blockquote
   - Keep both viewpoints, never silently overwrite
5. **Cascade updates:** Scan existing wiki pages for content affected by new source:
   - Update affected pages (add new info, cross-refs)
   - Refresh `updated` date on every touched page
6. Run: `python scripts/update-index.py`
7. Append to `.wiki/log.md`: `| <date> | compile | compiled N sources, cascade-updated M | claude |`
8. Commit: `git commit -am "docs: compile N sources, cascade-updated M pages"`

### `/wiki ingest+compile <file> [--category <cat>]`
Shortcut: ingest then compile in one step.
1. Run `/wiki ingest <file> --category <cat>`
2. Run `/wiki compile` (processes the just-ingested source)

### `/wiki query <question>`
Search wiki → answer → mandatory feedback loop.
1. Read `.wiki/index.md` for page catalog
2. Search: `grep -ri "<keywords>" .wiki/wiki/` (or `qmd query` if available)
3. Read relevant pages → synthesize answer
4. **MANDATORY FEEDBACK:** Evaluate "Does this answer have NEW insights?"
   - **YES:** Create new page in `.wiki/wiki/syntheses/` or `.wiki/wiki/concepts/`
     - Add wikilinks, update index, append to log.md, commit
   - **NO:** Answer only, no wiki changes, no log entry

### `/wiki digest <topic>`
Deep cross-source synthesis on a topic.
1. Read ALL sources and wiki pages mentioning `<topic>`
2. Cross-reference, find patterns, contradictions, gaps
3. Create: `.wiki/wiki/syntheses/digest-<topic>.md`
4. Update index, log, commit. Always creates a page.

### `/wiki lint`
Check wiki health.
1. Run: `python scripts/lint.py` — deterministic checks (orphans, broken links, stale, frontmatter)
2. **AI heuristic checks** (report only):
   - Factual contradictions missing `⚠️ Conflict` annotations
   - Outdated claims superseded by newer sources
   - Frequently mentioned concepts lacking dedicated pages
   - Missing cross-references between related pages
3. Fix deterministic issues. Report heuristic findings to user.

### `/wiki status`
Wiki statistics.
1. Run: `python scripts/stats.py`
2. Show: page counts, source counts, cross-ref density, recent activity

### `/wiki graph`
Generate knowledge graph.
1. Run: `python scripts/graph.py`
2. Creates `.wiki/wiki/knowledge-graph.md` with Mermaid diagram
3. Show summary: "Generated graph with N nodes, M edges"

## Key Rules
- Read `.wiki/AGENTS.md` for full conventions before operating
- Every wiki page needs YAML frontmatter: title, type, tags, created, updated
- Use `[[wikilinks]]` for cross-references
- Log mutations to log.md — never log read-only queries
- Run `python scripts/update-index.py` after any wiki changes
