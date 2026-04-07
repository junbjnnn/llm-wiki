# Phase 7: Documentation & Onboarding

## Context Links
- All previous phases
- [Brainstorm: success criteria](../reports/brainstorm-260407-1340-llm-wiki-knowledge-base.md)

## Overview
- **Priority:** P2 (essential for adoption)
- **Status:** Complete
- **Effort:** 2h
- **Description:** README, getting started guide, role-specific guides (PM/PO, developers), tool-specific setup

## Key Insights
- Target audiences: PM/PO (non-technical), developers, DevOps
- Each audience needs different onboarding path
- Tool-specific setup must cover: Claude Code, Cursor, Copilot, Gemini CLI
- README should get someone from 0 to working wiki in < 5 minutes

## Requirements

### Functional
- README.md: overview, quick start (< 5 min), feature list, architecture diagram (ASCII)
- docs/getting-started.md: detailed setup, first ingest walkthrough
- docs/for-pm-po.md: non-technical guide (how to add docs, ask questions, review wiki)
- docs/for-developers.md: technical guide (scripts, customization, contributing)
- docs/tool-specific-setup.md: setup instructions per AI tool

### Non-Functional
- Docs in markdown (Obsidian/GitHub compatible)
- No jargon in PM/PO guide
- Each doc < 150 lines

## Related Code Files

### Files to Create
```
docs/getting-started.md
docs/for-pm-po.md
docs/for-developers.md
docs/tool-specific-setup.md
```

### Files to Modify
```
README.md                   # Replace skeleton from Phase 1 with full content
```

## Implementation Steps

1. **README.md** — Project overview:
   - What: git-based markdown wiki for software teams
   - Why: tool-agnostic, no server, compounding knowledge
   - Quick Start (5 steps): clone → install → init → ingest first doc → query
   - ASCII architecture diagram
   - Links to detailed docs

2. **docs/getting-started.md** — Detailed setup:
   - Prerequisites (Python 3.11+, git)
   - Step-by-step: clone, venv, install, create first wiki page
   - First ingest walkthrough (with sample file)
   - How to query the wiki
   - How to lint/maintain

3. **docs/for-pm-po.md** — Non-technical guide:
   - What is this wiki? (plain language)
   - How to add documents (drag-and-drop metaphor)
   - How to ask questions (natural language examples)
   - How to review wiki pages (what frontmatter means)
   - Common workflows: "I have meeting notes" → ingest → query

4. **docs/for-developers.md** — Technical guide:
   - Directory structure explained
   - Script reference (CLI flags, examples)
   - Customizing .llm-wiki.toml
   - Adding new page types
   - Contributing guidelines

5. **docs/tool-specific-setup.md** — Per-tool instructions:
   - Claude Code: install skill, use /wiki commands
   - Cursor: .cursorrules generated, how to use
   - GitHub Copilot: copilot-instructions.md, chat usage
   - Gemini CLI: GEMINI.md, context loading
   - Generic: AGENTS.md works with any tool that reads it

## Todo List

- [x] Write README.md (overview + quick start)
- [x] Write docs/getting-started.md
- [x] Write docs/for-pm-po.md
- [x] Write docs/for-developers.md
- [x] Write docs/tool-specific-setup.md
- [x] Verify all internal links resolve
- [x] Verify quick start instructions work on clean machine

## Success Criteria
- New user follows README quick start → working wiki in < 5 minutes
- PM/PO reads for-pm-po.md → understands how to add docs and query
- Developer reads for-developers.md → understands customization options
- All docs render correctly on GitHub

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Docs drift from implementation | Medium | Medium | Write docs after implementation; reference actual commands |
| Too much jargon for PM/PO | Medium | Medium | Have non-technical reviewer read for-pm-po.md |
| Tool-specific instructions become stale | Medium | Low | Date-stamp tool versions; generate from AGENTS.md where possible |
