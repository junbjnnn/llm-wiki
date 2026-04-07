# Phase 3: Python Utility Scripts

## Context Links
- [MarkItDown Research](../reports/researcher-01-markitdown-and-schema-compatibility.md)
- [Phase 2: AGENTS.md Schema](phase-02-agents-schema.md) (frontmatter spec)

## Overview
- **Priority:** P1 (scripts are the utility backbone)
- **Status:** Complete
- **Effort:** 4h
- **Description:** Implement 4 Python scripts: ingest.py, update-index.py, lint.py, stats.py. No LLM calls — pure file processing.

## Key Insights
- markitdown handles 15+ formats; our ingest.py wraps it with wiki-specific output formatting
- Scripts read .llm-wiki.toml for paths/config — single source of truth
- All scripts are CLI tools (argparse) — callable by AI tools or humans
- Scripts output to stdout by default (AI tools capture output); optional file write flags

## Requirements

### Functional
- **ingest.py**: Parse any file → markdown stdout. Support: PDF, DOCX, PPTX, XLSX, HTML, images, CSV, JSON, XML. Accept file path or URL.
- **update-index.py**: Scan wiki/, read frontmatter, rebuild index.md with categorized listings
- **lint.py**: Check orphans, broken [[wikilinks]], stale pages (>N days), missing frontmatter fields. Exit code 0/1.
- **stats.py**: Page count by type, source count, cross-ref density, recent activity from log.md

### Non-Functional
- Python 3.11+ (tomllib built-in)
- No LLM API calls in any script
- Each script < 200 lines
- Consistent CLI interface (argparse)
- Exit codes: 0 = success, 1 = issues found (lint)

## Architecture

### Shared Config Loading
```python
# scripts/config.py — shared config loader
import tomllib
from pathlib import Path

def load_config() -> dict:
    config_path = Path(__file__).parent.parent / ".llm-wiki.toml"
    with open(config_path, "rb") as f:
        return tomllib.load(f)
```

### Data Flow: ingest.py
```
Input file/URL → markitdown.convert() → markdown text →
add YAML frontmatter (type: summary, source ref) →
stdout OR save to sources/{category}/
```

### Data Flow: update-index.py
```
Scan wiki/**/*.md → parse YAML frontmatter →
group by type → sort by updated date →
write index.md (categorized listing with titles + tags)
```

### Data Flow: lint.py
```
Scan wiki/**/*.md → for each page:
  - Check required frontmatter fields (from config)
  - Extract [[wikilinks]] → verify targets exist
  - Check updated date vs stale threshold
Scan all pages → find orphans (0 inbound links)
Report issues → exit 1 if any found
```

## Related Code Files

### Files to Create
```
scripts/config.py          # Shared config loader + constants (~50 lines)
scripts/init-wiki.py       # Wiki initializer — creates .wiki/ + all structure (~150 lines)
scripts/ingest.py          # Doc parser (~120 lines)
scripts/update-index.py    # Index rebuilder (~100 lines)
scripts/lint.py            # Wiki health checker (~150 lines)
scripts/stats.py           # Wiki statistics (~80 lines)
scripts/graph.py           # Mermaid knowledge graph generator (~100 lines)
```

### Files to Modify
```
scripts/__init__.py        # Add package docstring
```

## Implementation Steps

### 0. scripts/init-wiki.py (wiki initializer)
- CLI: `python scripts/init-wiki.py [--name "Project Name"] [--language en] [--root .wiki]`
- Creates entire `.wiki/` structure programmatically:
  - 8 source dirs, 9 wiki dirs
  - AGENTS.md, CLAUDE.md (from embedded templates)
  - .llm-wiki.toml, index.md, log.md, glossary.md
  - Copies scripts/ into .wiki/scripts/
  - Runs `pip install markitdown[all] pyyaml` if needed
- Idempotent: skips existing files, warns if .wiki/ already exists

### 1. scripts/config.py (shared utilities + constants)
```python
# Constants:
# SOURCE_CATEGORIES = ["product", "design", "architecture", ...]
# WIKI_SUBDIRS = ["summaries", "entities", "concepts", ...]
# PAGE_TYPES = ["summary", "entity", "concept", ...]
#
# Functions:
# load_config() -> dict          # Parse .llm-wiki.toml
# get_wiki_root() -> Path        # Resolve wiki root (.wiki/ or .)
# get_wiki_path() -> Path        # Resolve wiki directory
# get_sources_path() -> Path     # Resolve sources directory
# parse_frontmatter(text) -> dict  # Extract YAML frontmatter from markdown
# extract_wikilinks(text) -> list[str]  # Find all [[...]] references
```

### 2. scripts/ingest.py
- CLI: `python scripts/ingest.py <file_or_url> [--output sources/category/] [--category product]`
- Use `MarkItDown().convert(path)` for local files
- Add minimal frontmatter to output: title (from filename), source path, ingested date
- Print to stdout by default; `--output` saves to file
- Handle errors gracefully: unsupported format → clear error message

### 3. scripts/update-index.py
- CLI: `python scripts/update-index.py [--dry-run]`
- Walk `wiki/` recursively, skip `_template.md` files
- Parse frontmatter from each page
- Group pages by `type` field
- Within each type: sort by `updated` date (newest first)
- Generate index.md with format:
  ```
  ## Entities
  - [[entity-name]] — *Brief title* (tags: tag1, tag2) [updated: 2026-04-07]
  ```
- `--dry-run` prints to stdout instead of writing

### 4. scripts/lint.py
- CLI: `python scripts/lint.py [--fix] [--strict]`
- Checks (each returns list of issues):
  1. Missing frontmatter fields (per config `required_fields`)
  2. Invalid `type` value (not in config `page_types`)
  3. Broken [[wikilinks]] (target file doesn't exist)
  4. Orphan pages (no inbound [[wikilinks]] from other pages)
  5. Stale pages (updated > `stale_days` ago)
  6. Empty pages (no content beyond frontmatter)
- Output: grouped by check type, with file paths
- `--fix`: auto-fix what's possible (add missing `updated` date)
- `--strict`: treat warnings as errors
- Exit 0 if clean, 1 if issues

### 5. scripts/stats.py
- CLI: `python scripts/stats.py [--json]`
- Metrics:
  - Total pages, pages by type
  - Total sources (count files in sources/)
  - Cross-reference density (avg wikilinks per page)
  - Orphan count
  - Most connected pages (top 5 by inbound links)
  - Recent log entries (last 10 from log.md)
- `--json` for machine-readable output

## Todo List

- [x] Create scripts/config.py (shared utils + constants)
- [x] Create scripts/init-wiki.py (wiki initializer)
- [x] Create scripts/ingest.py (markitdown wrapper)
- [x] Create scripts/update-index.py (index rebuilder)
- [x] Create scripts/lint.py (wiki health checker)
- [x] Create scripts/stats.py (wiki statistics)
- [x] Test ingest.py with: PDF, DOCX, plain text, URL
- [x] Test update-index.py on empty wiki + wiki with templates
- [x] Test lint.py catches: missing frontmatter, broken links, orphans
- [x] Test stats.py on empty wiki + populated wiki
- [x] Create scripts/graph.py (Mermaid knowledge graph)
- [x] Test graph.py generates valid Mermaid syntax
- [x] Verify all scripts < 200 lines each

## Success Criteria
- `python scripts/ingest.py README.md` outputs valid markdown with frontmatter
- `python scripts/update-index.py` generates correct index.md from wiki pages
- `python scripts/lint.py` returns exit 1 on wiki with broken links
- `python scripts/stats.py` shows correct page counts
- All scripts handle empty wiki gracefully (no crashes)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| markitdown fails on specific format | Medium | Low | Catch exceptions per file; report unsupported format; continue |
| Large PDF causes OOM | Low | Medium | Document size limits; markitdown handles chunking internally |
| YAML frontmatter parsing edge cases | Medium | Low | Use PyYAML with safe_load; handle malformed gracefully |
| scripts exceed 200-line limit | Medium | Low | Extract helpers to config.py; keep scripts focused |

## Security Considerations
- ingest.py processes user-provided files — no eval/exec on content
- URL ingestion: markitdown handles HTTP; no shell injection risk
- No secrets read or written by any script
