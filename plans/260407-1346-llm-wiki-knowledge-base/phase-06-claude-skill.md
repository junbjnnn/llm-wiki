# Phase 6: Claude Code Skill Wrapper

## Context Links
- [Phase 3: Python Scripts](phase-03-python-scripts.md) (scripts this skill wraps)
- [Claude Code Skills docs](https://docs.anthropic.com/en/docs/claude-code/skills)

## Overview
- **Priority:** P3 (optional convenience for Claude Code users)
- **Status:** Complete
- **Effort:** 2h
- **Description:** Claude Code skill providing /wiki commands that wrap Python scripts + add AI-powered workflows

## Key Insights
- Skill = SKILL.md file that Claude Code reads when activated
- Skill instructs Claude how to use the wiki — it's a convenience layer, not required
- Commands map to: init, ingest, query, lint, status
- The skill tells Claude to run scripts AND interpret results — combining utility scripts with LLM reasoning

## Requirements

### Functional
- SKILL.md with /wiki command documentation
- Commands: `/wiki init`, `/wiki ingest <file>`, `/wiki query <question>`, `/wiki lint`, `/wiki status`
- Each command: describes what to do, which script to run, how to interpret output
- Ingest command: run ingest.py → read output → create wiki pages → update index → commit

### Non-Functional
- Skill works with Claude Code only (other tools use AGENTS.md directly)
- SKILL.md < 150 lines
- No custom code needed — skill is pure instruction

## Architecture

### Command Flow
```
User: /wiki ingest meeting-notes.pdf
  → Run: python scripts/ingest.py meeting-notes.pdf --category meetings
  → Script saves parsed markdown to .wiki/sources/meetings/meeting-notes.md
  → Done (no AI yet)

User: /wiki compile
  → Claude reads SKILL.md
  → Scans sources/ for files not yet summarized in wiki/
  → For each: create wiki/summaries/*, update entities/concepts
  → Run: python scripts/update-index.py
  → Append to log.md
  → git commit -m "docs: compile 3 new sources"

User: /wiki query "how does auth work?"
  → Claude searches wiki → synthesizes answer
  → Evaluates: "New insight?" → YES
  → Creates wiki/syntheses/auth-flow-overview.md
  → Updates cross-refs, index, log
  → git commit -m "docs: query insight - auth flow overview"
```

## Related Code Files

### Skill Directory Structure
```
~/.claude/skills/llm-wiki/
├── SKILL.md                    # Skill definition (/wiki commands)
├── templates/
│   ├── agents-md.md            # AGENTS.md template
│   ├── claude-md.md            # CLAUDE.md template
│   ├── llm-wiki.toml           # Config template
│   └── page-templates.yaml     # All 10 page type templates in 1 file
└── scripts/
    ├── config.py               # Shared utils + constants
    ├── init-wiki.py            # Creates .wiki/ + everything
    ├── ingest.py               # Parse docs → markdown
    ├── update-index.py         # Rebuild index.md
    ├── lint.py                 # Wiki health check
    └── stats.py                # Statistics
```

### Files to Create (in repo, for distribution)
```
skill/SKILL.md              # Reference copy
skill/install.sh            # Copy skill to ~/.claude/skills/llm-wiki/
```

### install.sh copies entire skill/ → ~/.claude/skills/llm-wiki/

## Implementation Steps

1. **Create skill/SKILL.md** with sections:
   - Activation: `/wiki` prefix
   - Commands:
     - `/wiki init` — Initialize new wiki in `.wiki/` subfolder
     - `/wiki ingest <file>` — Parse file → save to sources/ (script only)
     - `/wiki batch-ingest <folder>` — Scan folder, process all files, pause every 5
     - `/wiki compile` — AI reads uncompiled sources → create/update wiki pages (auto short/long routing)
     - `/wiki ingest+compile <file>` — Shortcut: ingest then compile in one step
     - `/wiki query <question>` — Search + answer + mandatory feedback loop
     - `/wiki digest <topic>` — Deep cross-source synthesis → save report to wiki/syntheses/
     - `/wiki lint` — Health check: orphans, broken links, contradictions
     - `/wiki status` — Wiki statistics + recent activity
     - `/wiki graph` — Generate Mermaid knowledge graph from wikilinks
   - Each command includes: what to run, how to interpret output, what to do next

2. **Create skill/install.sh:**
   ```bash
   #!/usr/bin/env bash
   mkdir -p ~/.claude/skills/llm-wiki
   cp skill/SKILL.md ~/.claude/skills/llm-wiki/SKILL.md
   echo "Skill installed. Activate with /wiki in Claude Code."
   ```

## Todo List

- [x] Write SKILL.md with all 5 commands
- [x] Create install.sh
- [x] Test: Claude Code recognizes /wiki commands
- [x] Test: /wiki ingest runs ingest.py and creates wiki page
- [x] Test: /wiki lint runs lint.py and reports issues
- [x] Verify SKILL.md < 150 lines

## Success Criteria
- Claude Code user can type `/wiki ingest file.pdf` and get a wiki page created
- `/wiki status` shows accurate wiki statistics
- `/wiki lint` identifies and reports issues
- Skill is optional — wiki works without it

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Claude Code skill API changes | Low | Medium | SKILL.md is simple markdown; easy to update |
| Skill path differs across OS | Low | Low | install.sh handles path; document manual install |
| Users expect skill to work in other tools | Medium | Low | Document clearly: Claude Code only; others use AGENTS.md |
