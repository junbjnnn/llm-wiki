# Phase 5: qmd Integration

## Context Links
- [qmd Research](../reports/researcher-260407-qmd-and-wiki-patterns.md)
- [qmd GitHub](https://github.com/tobi/qmd)

## Overview
- **Priority:** P2 (recommended — essential for wikis > 100 pages)
- **Status:** Complete
- **Effort:** 1.5h
- **Description:** Setup script for qmd, collection config, usage docs in AGENTS.md

## Key Insights
- qmd = on-device hybrid search (BM25 + vector + LLM reranking) by Tobi Lutke
- Install: `npm install -g @tobilu/qmd`
- Collection = indexed directory; wiki/ is our collection
- qmd is OPTIONAL — wiki works fine with grep/ripgrep alone
- MCP server mode available for Claude Desktop integration

## Requirements

### Functional
- Shell script to check qmd installation + initialize collection
- .llm-wiki.toml `[qmd]` section: `enabled`, `auto_embed`, `collection_name`
- AGENTS.md tiered search strategy (grep < 100 pages, qmd > 100 pages)
- `/wiki init --with-qmd` flag in init-wiki.py
- Auto `qmd embed` after ingest (when `auto_embed = true`)
- `update-index.py` splits index.md when > 200 pages (sub-indexes per type)

### Non-Functional
- qmd is recommended but degrades gracefully to grep
- No Node.js dependency if qmd not used
- Wiki works without qmd at any scale (just slower search)

## Related Code Files

### Files to Create
```
scripts/setup-qmd.sh       # qmd setup helper (~40 lines)
```

### Files to Modify
```
AGENTS.md                   # Add qmd search section
.llm-wiki.toml             # qmd config section (already templated in Phase 1)
.gitignore                  # Add .qmd/ directory
```

## Implementation Steps

1. **Create scripts/setup-qmd.sh:**
   ```bash
   #!/usr/bin/env bash
   # Check qmd installed
   # Read collection name from .llm-wiki.toml
   # qmd collection add ./wiki --name $COLLECTION
   # qmd collection add ./sources --name "${COLLECTION}-sources"
   # qmd embed
   ```

2. **Update AGENTS.md** — tiered search strategy:
   ```markdown
   ## Search Strategy

   ### Tiered approach (auto-select by wiki size)
   - **< 100 pages:** Read index.md + `grep -r "keyword" .wiki/wiki/`
   - **100+ pages:** Use `qmd query "question"` if available, fallback grep
   - **500+ pages:** qmd strongly recommended (grep insufficient for semantic search)

   ### qmd commands (if installed)
   - `qmd query "your question" --collection wiki` — hybrid search + LLM reranking
   - `qmd search "keyword" --collection wiki` — fast BM25 keyword search
   - Check availability: `qmd status`

   ### Fallback (no qmd)
   - `grep -ri "keyword" .wiki/wiki/`
   - Read .wiki/index.md for page catalog
   ```

3. **Update init-wiki.py** — add `--with-qmd` flag:
   - Check `which qmd`, if found → auto setup collection
   - Set `[qmd] enabled = true` in .llm-wiki.toml
   - Run initial `qmd embed`

4. **Update ingest.py** — auto embed hook:
   - After saving source, check config `[qmd] auto_embed`
   - If true and qmd available → run `qmd embed`

5. **Update update-index.py** — auto-split:
   - Count wiki pages; if > 200 → generate per-type `_index.md` files
   - Main index.md becomes overview linking to sub-indexes

3. **Ensure .gitignore includes `.qmd/`** (index cache directory)

## Todo List

- [x] Create scripts/setup-qmd.sh
- [x] Add qmd search section to AGENTS.md
- [x] Verify .gitignore covers .qmd/
- [x] Test setup-qmd.sh with qmd installed
- [x] Test setup-qmd.sh graceful failure when qmd not installed

## Success Criteria
- `bash scripts/setup-qmd.sh` succeeds when qmd installed, fails gracefully when not
- `qmd query "test" --collection wiki` returns results after setup
- Wiki fully functional without qmd (grep fallback)

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| qmd npm package unavailable | Low | None | qmd is optional; grep works fine |
| qmd API changes | Low | Low | Pin version in docs; setup script is thin wrapper |
| Large wiki slow to embed | Low | Low | qmd handles incremental indexing |
