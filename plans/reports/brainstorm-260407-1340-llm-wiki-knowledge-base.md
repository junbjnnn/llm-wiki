# Brainstorm Report: LLM Wiki Knowledge Base

**Date:** 2026-04-07
**Based on:** [Karpathy's llm-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

## Problem Statement

PM/Tech Lead quản lý nhiều dự án phần mềm cần knowledge base cho team. Team members dùng nhiều AI tools khác nhau (Claude Code, Cursor, Copilot, Gemini CLI, Antigravity). Cần giải pháp đơn giản, git-native, tool-agnostic.

## Requirements

- Git-based markdown wiki — mọi thay đổi tracked, diff-able, reviewable
- Tool-agnostic — hoạt động với bất kỳ AI coding tool nào
- Team-friendly — PM/PO không cần biết code cũng dùng được
- Multi-project — mỗi project 1 wiki riêng
- Auto-ingest — parse PDF, DOCX, code, meeting notes → wiki pages
- Software project focus — hỗ trợ 31+ loại tài liệu dự án phần mềm

## Final Design: KISS Architecture

### Core Concept

Wiki = git repo chứa markdown. Schema file hướng dẫn AI tool cách vận hành. Python scripts làm utilities (parse docs, update index). LLM layer = AI tool mà user đang dùng.

### Architecture

```
User's AI Tool (Claude/Cursor/Copilot/Gemini/...)
         │ reads schema, follows rules
         ▼
Git Repo (wiki)
├── AGENTS.md          ← Schema/instructions cho mọi AI tool
├── index.md           ← Auto-maintained catalog
├── log.md             ← Chronological activity log
├── sources/           ← Raw source files (immutable)
├── wiki/              ← LLM-generated pages
│   ├── summaries/
│   ├── entities/
│   ├── concepts/
│   ├── comparisons/
│   ├── syntheses/
│   ├── chronicles/    ← Feature evolution logs
│   ├── decisions/     ← ADRs
│   ├── runbooks/
│   ├── postmortems/
│   └── glossary.md
└── scripts/           ← Python utility tools
    ├── ingest.py      ← Parse any format → markdown
    ├── update-index.py
    ├── lint.py
    └── stats.py
```

### Schema Compatibility

- `AGENTS.md` — universal (Karpathy's approach)
- Optionally symlink/copy to `.cursorrules`, `CLAUDE.md`, etc.

### 3 Operations (từ Karpathy)

1. **Ingest** — Script parse file → AI tool đọc output → tạo summary + update related pages → commit
2. **Query** — AI tool search wiki pages → synthesize answer → optionally tạo page mới
3. **Lint** — Script check orphans/broken links + AI tool check contradictions/staleness

### Page Types (Software Project)

| Type | Mô tả |
|------|--------|
| summary | 1:1 tóm tắt source document |
| entity | Service, API, database, team member |
| concept | Architecture pattern, convention |
| comparison | Side-by-side analysis |
| synthesis | Cross-source insights |
| chronicle | Feature evolution history |
| adr | Architecture Decision Record |
| runbook | Operational how-to |
| postmortem | Incident analysis |
| glossary | Domain terminology |

### 31 Document Types Supported

Product (PRD, backlog, release notes, user research), Design (wireframes, style guide, user flows), Architecture (system arch, ADR, API specs, DB schema, infra), Development (README, code standards, tech debt, dependencies), Testing (test plans, bug reports, QA checklists), Operations (runbooks, incidents, monitoring), Communication (meeting notes, Slack, emails), Project Management (sprint reports, risk register, stakeholder map), Knowledge (onboarding, glossary, external references).

### Tech Stack

| Component | Choice |
|-----------|--------|
| Storage | Git + Markdown |
| Doc parsing | Python + markitdown |
| Scripts | Python (utilities only, no LLM calls) |
| LLM | User's own AI tool |
| Search | grep/ripgrep (basic), qmd CLI (optional advanced) |
| Config | TOML (.llm-wiki.toml) |

## Rejected Approaches

| Approach | Why rejected |
|----------|-------------|
| MCP Server | Unnecessary complexity — user already has LLM tool |
| litellm | Each user uses their own LLM, no need to abstract |
| Vector DB | Overkill for markdown wiki — text search sufficient initially |
| Web UI | CLI/AI tool sufficient, YAGNI |

## Risks

- **Schema drift** — different AI tools may interpret AGENTS.md differently → mitigate with clear, explicit instructions
- **Merge conflicts** — multiple users editing wiki simultaneously → mitigate with git workflow conventions
- **LLM quality variance** — different models produce different quality pages → mitigate with strict page templates

## Success Criteria

- PM/PO can ingest docs and query wiki using any AI tool
- Wiki stays consistent after multiple team members contribute
- Setup < 5 minutes (clone + install markitdown)
- No server, no API keys beyond user's own AI tool

## Next Steps

Create implementation plan with phases:
1. Wiki repo structure + schema
2. Python utility scripts
3. Claude Code skill wrapper
4. Documentation + onboarding guide
