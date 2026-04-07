# Phase 4: Tool Config Generation

## Context Links
- [Schema Compatibility Research](../reports/researcher-01-markitdown-and-schema-compatibility.md)
- [Phase 2: AGENTS.md](phase-02-agents-schema.md)

## Overview
- **Priority:** P2 (convenience, not critical)
- **Status:** Pending
- **Effort:** 2h
- **Description:** Script to generate tool-specific instruction files (CLAUDE.md, .cursorrules, etc.) from AGENTS.md

## Key Insights
- AGENTS.md = single source of truth; tool-specific files are derivatives
- Each tool has different format expectations (see research report)
- Not all tools read AGENTS.md yet — generation bridges the gap
- Generated files should have a header comment: "Auto-generated from AGENTS.md. Do not edit directly."

## Requirements

### Functional
- Parse AGENTS.md sections into structured data
- Generate: CLAUDE.md, .cursorrules, .github/copilot-instructions.md, GEMINI.md
- Each generated file follows tool's expected format
- Idempotent: running twice produces same output
- `--tool` flag to generate for specific tool only

### Non-Functional
- Script < 200 lines
- No external dependencies beyond stdlib + tomllib

## Architecture

### Data Flow
```
AGENTS.md → parse sections (regex on ## headers) →
extract content blocks → format per tool →
write tool-specific files
```

### Generation Matrix

| Target | Output File | Format | Key Sections |
|--------|-----------|--------|-------------|
| Claude | CLAUDE.md | Markdown | All sections + Claude-specific tips |
| Cursor | .cursorrules | Plain text | Conventions + architecture |
| Copilot | .github/copilot-instructions.md | Markdown | Conventions + workflows |
| Gemini | GEMINI.md | Markdown | All sections |

## Related Code Files

### Files to Create
```
scripts/generate-tool-configs.py    # Generator script (~150 lines)
```

### Files Generated (output, not committed to plan)
```
CLAUDE.md
.cursorrules
.github/copilot-instructions.md
GEMINI.md
```

## Implementation Steps

1. Parse AGENTS.md into sections dict: `{"About": "...", "Conventions": "...", ...}`
2. For each tool, define a template function:
   - `generate_claude_md(sections)` — full content + "Generated from AGENTS.md" header
   - `generate_cursorrules(sections)` — strip markdown formatting, plain text rules
   - `generate_copilot_instructions(sections)` — markdown, focused on conventions
   - `generate_gemini_md(sections)` — full content, similar to Claude
3. CLI: `python scripts/generate-tool-configs.py [--tool claude|cursor|copilot|gemini|all]`
4. Default: `--tool all` generates all files
5. Add auto-gen header to each output: `<!-- Auto-generated from AGENTS.md. Run: python scripts/generate-tool-configs.py -->`

## Todo List

- [ ] Implement AGENTS.md section parser
- [ ] Implement CLAUDE.md generator
- [ ] Implement .cursorrules generator
- [ ] Implement .github/copilot-instructions.md generator
- [ ] Implement GEMINI.md generator
- [ ] Test: generated files match expected format
- [ ] Test: idempotent (run twice, diff = 0)

## Success Criteria
- `python scripts/generate-tool-configs.py` generates all 4 files without error
- Generated CLAUDE.md contains wiki conventions and workflows
- Generated files have auto-gen header comment
- Re-running produces identical output

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| AGENTS.md format changes break parser | Medium | Medium | Use resilient regex; fallback to full-file copy |
| Tool format specs change | Low | Low | Templates are simple; easy to update |
