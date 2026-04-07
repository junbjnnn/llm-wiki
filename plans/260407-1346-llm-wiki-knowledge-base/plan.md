---
title: "LLM Wiki Knowledge Base"
description: "Git-based markdown wiki for software teams, tool-agnostic, Karpathy pattern"
status: completed
priority: P1
effort: 16h
branch: main
tags: [wiki, knowledge-base, markdown, agents-md, greenfield]
created: 2026-04-07
---

# LLM Wiki Knowledge Base — Implementation Plan

## Overview

Build a git-based markdown wiki for software project teams. No server, no MCP, no litellm. Pure git + markdown + Python utility scripts. Users bring their own AI tool. AGENTS.md serves as universal schema.

## Architecture

Default: `.wiki/` subfolder in code repo. Also supports standalone repo via config.

```
project-repo/
├── .wiki/                     # Wiki root (default: subfolder)
│   ├── AGENTS.md              # Universal schema (open standard)
│   ├── CLAUDE.md              # Claude-specific additions
│   ├── .llm-wiki.toml         # Config (wiki_root, language, etc.)
│   ├── index.md / log.md      # Auto-maintained catalog + activity log
│   ├── sources/               # Raw source files (immutable, 8 subdirs)
│   ├── wiki/                  # LLM-generated pages (10 subdirs + glossary.md)
│   └── scripts/               # Python utilities
└── src/, docs/, ...           # Project code
```

## Phases

| # | Phase | Effort | Status | File |
|---|-------|--------|--------|------|
| 1 | Project Setup & Wiki Structure | 1h | Complete | [phase-01](phase-01-project-setup.md) |
| 2 | AGENTS.md Schema & Page Templates | 3.5h | Complete | [phase-02](phase-02-agents-schema.md) |
| 3 | Python Utility Scripts | 5h | Complete | [phase-03](phase-03-python-scripts.md) |
| 5 | qmd Integration | 1.5h | Complete | [phase-05](phase-05-qmd-integration.md) |
| 6 | Claude Code Skill Wrapper | 3h | Complete | [phase-06](phase-06-claude-skill.md) |
| 7 | Documentation & Onboarding | 2h | Complete | [phase-07](phase-07-documentation.md) |

> Phase 4 removed (YAGNI: AGENTS.md + CLAUDE.md maintained manually)

## Dependency Graph

```
Phase 1 → Phase 2 → Phase 3 → Phase 5
                  ↘ Phase 7 (parallel, starts after 2)
           Phase 3 → Phase 6
```

## Key Decisions

- Default: `.wiki/` subfolder in code repo; configurable for standalone
- AGENTS.md + CLAUDE.md maintained manually (no auto-generation, YAGNI)
- [[wikilink]] style cross-refs (Obsidian compatible)
- YAML frontmatter on every wiki page (10 page types)
- markitdown for doc parsing; no LLM calls in scripts
- Wiki language configurable per project (default: English)
- qmd optional (npm); Claude skill optional
- Each project manages its own wiki (no shared cross-project wiki)

## Rollback

Each phase is a standalone git commit. Revert any phase without cascading damage. No external state (no DB, no server).

## Success Criteria

- [x] PM/PO can ingest docs and query wiki using any AI tool
- [x] Setup < 5 minutes (clone + pip install)
- [x] Wiki stays consistent after multiple contributors
- [x] All scripts run without errors on empty + populated wiki
- [x] AGENTS.md readable by Claude, Cursor, Copilot, Gemini, Codex

## Validation Log

### Session 1 — 2026-04-07
**Trigger:** Post-plan validation interview
**Questions asked:** 6

#### Questions & Answers

1. **[Architecture]** Wiki standalone repo hay subfolder?
   - Options: Standalone repo | .wiki/ subfolder | Both
   - **Answer:** Both — default `.wiki/` subfolder, config cho standalone
   - **Rationale:** PM/PO access wiki trong code repo, không cần repo riêng

2. **[Scope]** 10 page types cần tất cả ngay?
   - Options: All 10 | Core 5 | Core 3
   - **Answer:** All 10
   - **Rationale:** EXPANSION scope, tạo hết templates từ đầu

3. **[YAGNI]** Phase 4 tool config generation cần thiết?
   - Options: Keep | Remove | Defer
   - **Answer:** Remove — chỉ giữ AGENTS.md + CLAUDE.md, viết thủ công
   - **Rationale:** YAGNI — auto-generation phức tạp không cần thiết

4. **[Scope]** Multi-project shared wiki?
   - Options: Per-project | Shared + per-project | Defer
   - **Answer:** Per-project only
   - **Rationale:** Đơn giản, mỗi project tự quản lý

5. **[Language]** AGENTS.md ngôn ngữ?
   - **Answer:** Tiếng Anh
   - **Rationale:** AI tools hiểu EN tốt nhất

6. **[Language]** Wiki pages ngôn ngữ?
   - **Answer:** Configurable per project (default EN)
   - **Rationale:** Flexibility cho teams khác nhau

#### Confirmed Decisions
- `.wiki/` subfolder default: confirmed
- Phase 4 removed: confirmed (YAGNI)
- AGENTS.md + CLAUDE.md only: confirmed
- Wiki language in .llm-wiki.toml: confirmed

#### Impact on Phases
- Phase 1: Update directory structure (`.wiki/` root), add `language` to config
- Phase 2: Write CLAUDE.md alongside AGENTS.md (no auto-gen)
- Phase 4: REMOVED
- Phase 6: Skill references `.wiki/` path by default

### Session 2 — 2026-04-07
**Trigger:** Post-brainstorm reviews (DAIR article + sdyckjq-lab repo) + user Q&A
**Changes applied:** 16

#### Key Decisions (post-Session 1)

1. **[Architecture]** Tách Ingest vs Compile — ingest = script only, compile = AI
2. **[Architecture]** Mandatory query feedback loop (not optional)
3. **[Architecture]** log.md = mutations only, no read queries
4. **[Architecture]** Compile update detection via frontmatter `sources` field
5. **[Feature]** batch-ingest, digest, graph commands added (10 total)
6. **[Feature]** Content short/long routing in compile (≤1000 / >1000 chars)
7. **[Feature]** graph.py — Mermaid knowledge graph generator
8. **[Scale]** qmd P3 → P2, index.md auto-split >200 pages
9. **[Scope]** 10 commands confirmed, no reduction
10. **[Process]** Implement theo thứ tự plan: Phase 1→2→3→5→6→7

#### Effort Update
- Phase 1: 1.5h → 1h (init-wiki.py handles setup)
- Phase 2: 3h → 3.5h (more workflows: compile, digest, update detection, log rules)
- Phase 3: 4h → 5h (added graph.py, init-wiki.py)
- Phase 6: 2h → 3h (10 commands, batch-ingest progress, digest deep report)
- **Total: 16h**
