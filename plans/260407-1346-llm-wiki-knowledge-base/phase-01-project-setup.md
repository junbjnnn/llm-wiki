# Phase 1: Project Setup & Wiki Structure

## Context Links
- [Brainstorm Report](../reports/brainstorm-260407-1340-llm-wiki-knowledge-base.md)
- [Karpathy's llm-wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## Overview
- **Priority:** P1 (foundation — everything depends on this)
- **Status:** Complete
- **Effort:** 1.5h
- **Description:** Initialize git repo, create directory structure, config template, Python venv

## Key Insights
- Greenfield project — no migration concerns
- Directory structure must match AGENTS.md schema exactly (consistency = trust for AI tools)
- sources/ subdirs map to software project doc categories (from brainstorm: 31 doc types → 7 categories)

## Requirements

### Functional
- git-initialized repo with .gitignore
- Full directory tree with .gitkeep files for empty dirs
- .llm-wiki.toml config template with sensible defaults
- Python venv + requirements.txt (markitdown[all])
- README.md skeleton

### Non-Functional
- Setup must complete < 5 minutes on fresh machine
- Python 3.11+ required
- No system-wide pip installs

## Related Code Files

### Files to Create
```
.gitignore
.llm-wiki.toml
README.md
requirements.txt
sources/product/.gitkeep
sources/design/.gitkeep
sources/architecture/.gitkeep
sources/development/.gitkeep
sources/operations/.gitkeep
sources/meetings/.gitkeep
sources/references/.gitkeep
sources/data/.gitkeep
wiki/summaries/.gitkeep
wiki/entities/.gitkeep
wiki/concepts/.gitkeep
wiki/comparisons/.gitkeep
wiki/syntheses/.gitkeep
wiki/chronicles/.gitkeep
wiki/decisions/.gitkeep
wiki/runbooks/.gitkeep
wiki/postmortems/.gitkeep
scripts/__init__.py
```

## Implementation Steps

**Note:** No manual folder creation. `init-wiki.py` script (Phase 3) generates everything programmatically via `/wiki init` command.

1. **Define config template** (`.llm-wiki.toml` content embedded in init-wiki.py):
   ```toml
   [wiki]
   name = "My Project Wiki"
   version = "1.0.0"
   language = "en"  # Wiki page language: en, vi, ja, etc.
   root = ".wiki"   # Default: .wiki/ subfolder. Use "." for standalone repo

   [paths]
   sources = "sources"
   wiki = "wiki"
   scripts = "scripts"
   index = "index.md"
   log = "log.md"
   schema = "AGENTS.md"

   [frontmatter]
   required_fields = ["title", "type", "tags", "created", "updated"]
   page_types = ["summary", "entity", "concept", "comparison", "synthesis", "chronicle", "adr", "runbook", "postmortem"]
   confidence_levels = ["high", "medium", "low"]

   [lint]
   stale_days = 30
   require_backlinks = true
   require_sources = true

   [qmd]
   enabled = false
   collection_name = "wiki"
   ```
2. **Define directory structure** (created by init-wiki.py):
   - sources/: product, design, architecture, development, operations, meetings, references, data
   - wiki/: summaries, entities, concepts, comparisons, syntheses, chronicles, decisions, runbooks, postmortems
3. **Define templates** (AGENTS.md, CLAUDE.md, index.md, log.md, glossary.md — content in Phase 2)
4. **Requirements:** `markitdown[all]>=0.1.5`, `pyyaml>=6.0`

## Todo List

- [x] Define config template content
- [x] Define directory structure constants
- [x] Define template file contents (delegated to Phase 2)
- [x] Define requirements.txt content
- [x] All above embedded in init-wiki.py (Phase 3)

## Success Criteria
- `tree` command shows correct structure
- `.venv/bin/python3 -c "from markitdown import MarkItDown"` succeeds
- `.llm-wiki.toml` parseable by Python tomllib
- `git status` shows clean working tree after initial commit

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| markitdown install fails (native deps) | Low | High | Use `markitdown[pdf,docx,pptx]` subset if `[all]` fails |
| Python < 3.11 on user machine | Medium | Medium | Document requirement; tomli fallback for TOML parsing |

## Next Steps
- Phase 2 depends on this phase completing
- Directory structure here must match what AGENTS.md references
