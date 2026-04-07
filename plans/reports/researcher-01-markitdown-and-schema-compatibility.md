# Research Report: Microsoft MarkItDown & AI Tool Instruction File Schemas

**Date:** 2026-04-07
**Status:** Complete
**Focus:** Markitdown capabilities & cross-tool instruction file compatibility

---

## Part 1: Microsoft MarkItDown

### Overview
Microsoft MarkItDown is a lightweight Python utility (v0.1.5, Feb 2026) that converts document formats to Markdown for LLM pipelines. ~91k GitHub stars. MIT licensed. Production-ready but actively maintained.

### Supported Formats

| Category | Formats |
|----------|---------|
| **Office** | PDF, DOCX, PPTX, XLSX, XLS, MSG (Outlook) |
| **Images** | JPG, PNG (with EXIF, caption generation) |
| **Audio** | WAV, MP3 (with transcription) |
| **Web** | HTML, EPUB, YouTube URLs, ZIP archives |
| **Structured** | CSV, JSON, XML |

Optional dependencies allow selective installation: `[pdf]`, `[docx]`, `[pptx]`, `[xlsx]`, `[xls]`, `[outlook]`, `[audio-transcription]`, `[youtube-transcription]`, `[az-doc-intel]`.

### Python API Usage

**Installation:**
```bash
# Complete feature set
pip install 'markitdown[all]'

# Selective installation
pip install 'markitdown[pdf,docx,pptx]'
```

**Basic API:**
```python
from markitdown import MarkItDown

# Simple conversion
md = MarkItDown()
result = md.convert("file.xlsx")
print(result.text_content)

# With LLM image descriptions (OpenAI, Azure, etc.)
from openai import OpenAI
md = MarkItDown(llm_client=OpenAI(), llm_model="gpt-4o")
result = md.convert("image.jpg")
print(result.text_content)
```

**Key Methods:**
- `MarkItDown()` — instantiate with optional `llm_client` and `llm_model`
- `convert(file_path)` — convert local files, returns `DocumentConverterResult` object
- `result.text_content` — access converted Markdown output

### Limitations & Known Issues

| Issue | Impact |
|-------|--------|
| **PDF formatting loss** | Strips headings, lists, styling; no distinction between text types |
| **OCR dependency** | Cannot process non-OCR'd PDFs; image quality affects accuracy |
| **Complex layouts** | Limited support for intricate table structures |
| **Large documents** | Response can exceed LLM token limits (issue #1333) |
| **Image extraction** | Requires external LLM for descriptions; loses formatting |
| **Wrapper architecture** | Built on existing libraries (mammoth, pandas); not novel conversion |
| **Optional dependency management** | Potential conflicts if dependencies not carefully installed |

### Requirements
- Python 3.10+
- Virtual environment recommended to avoid dependency conflicts

---

## Part 2: AI Tool Instruction File Schemas

### Quick Reference Table

| Tool | Filename | Location | Auto-Load | Format | Scope |
|------|----------|----------|-----------|--------|-------|
| **Claude Code** | `CLAUDE.md` | Project root, `~/.claude/` | Yes, auto-read | Markdown | Claude-specific |
| **Cursor IDE** | `.cursorrules` or `.cursor/*.mdc` | Project root | Yes, auto-load | Plain text/Markdown | Cursor-specific |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.github/` directory | Yes, auto-include | Markdown | Tool-agnostic (VS Code, GH) |
| **OpenAI Codex** | `AGENTS.md` | Project root, walk hierarchy | Yes, at startup | Markdown (natural language) | Open standard (universal) |
| **Google Gemini CLI** | `GEMINI.md` | Project root, `~/.gemini/` | Yes, context auto-load | Markdown | Gemini-specific |
| **Windsurf** | `.windsurfrules` | Project root | Yes | Plain text/Markdown | Windsurf-specific |

### Detailed Specifications

#### CLAUDE.md (Claude Code)
**Structure:**
```markdown
## Project
One-line description

## Stack
- Technology: Version

## Commands
- `command` — description

## Conventions
- Convention items

## Architecture
Directory structure notes

## Rules
- Hard rules (imperative statements)
```

**Key Features:**
- Supports file imports: `@path/to/other.md` to reference external files
- Loading hierarchy: global admin → personal global → project-level → current directory (later = higher priority)
- Size recommendation: <200 lines (adherence drops with larger files)
- No special syntax; plain Markdown with natural language instructions

**Best For:** Single-tool, deep project context; Claude-specific features like sub-agent delegation, permission levels.

#### .cursorrules (Cursor IDE)
**Format:** Plain text or JSON. Legacy `.cursorrules` still works but deprecated.

**Modern Approach:** `.cursor/index.mdc` with Rule Type "Always" for project-wide standards; focused `.cursor/*.mdc` files for specialized tasks.

**Structure (Legacy):**
```json
{
  "general_rules": [...],
  "ai_reasoning": [...],
  "testing": [...],
  "code_style": [...]
}
```

**Key Features:**
- No formal schema; natural language rules
- Can section into `general_rules`, `ai_reasoning`, `testing`, `code_style`, etc.
- Whitespace ignored; can be single paragraph or line-by-line

**Limitation:** Cursor-only; ignored by other tools.

#### .github/copilot-instructions.md (GitHub Copilot)
**Structure:** Plain Markdown, natural language instructions.

**Example:**
```markdown
We use Bazel for Java dependency management, not Maven.
All JavaScript uses double quotes and tabs.
```

**Key Features:**
- Short, self-contained statements
- Auto-included in Copilot Chat (VS Code, GitHub)
- Verify inclusion by checking References in response
- Whitespace ignored; can be single paragraph or separated lines

**Scope:** GitHub Copilot Chat (VS Code, GH web), tool-agnostic format.

#### AGENTS.md (OpenAI Codex)
**Structure:** Markdown with natural language sections.

**Discovery Hierarchy:**
1. Codex home directory (`~/.codex/`): reads `AGENTS.override.md`, then `AGENTS.md`
2. Project root down to current working directory: checks for `AGENTS.override.md`, then `AGENTS.md` at each level
3. Fallback: `project_doc_fallback_filenames` config

**Typical Sections:**
- Dev environment setup
- Testing procedures
- PR conventions
- Build commands

**Key Features:**
- **Open standard** — stewarded by Agentic AI Foundation (Linux Foundation)
- Backed by Sourcegraph, OpenAI, Google, Cursor, Factory
- Designed for universal tool support
- Complements README (extra context agents need, not for humans)

**Advantage:** Single source of truth across multiple tools (if they adopt AGENTS.md).

#### GEMINI.md (Google Gemini CLI)
**Location:** Project root, `~/.gemini/GEMINI.md` (global)

**Features:**
- Configurable via `context.fileName` in settings
- Hierarchical: global → project-level
- Advanced override: `GEMINI_SYSTEM_MD` environment variable replaces default system prompt entirely

**Config Location:** `~/.gemini/settings.json` (global settings), `GEMINI.md` (project context)

---

### Schema Compatibility Analysis

#### Cross-Tool Support Matrix

| File | Claude | Cursor | Copilot | Codex | Gemini | Windsurf |
|------|--------|--------|---------|-------|--------|----------|
| CLAUDE.md | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| .cursorrules | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| .github/copilot-instructions.md | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| AGENTS.md | ✓ (partial) | ✓ (planned) | ✗ (not yet) | ✓ | ✗ (not yet) | ✗ (not yet) |
| GEMINI.md | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| .windsurfrules | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

**Key Finding:** AGENTS.md has broadest potential adoption (open standard, Linux Foundation backing) but adoption by Copilot/Gemini/Windsurf is incomplete as of April 2026.

#### Recommended Pattern: Layered Approach

**Current Best Practice** (per community consensus):
1. **AGENTS.md** — Universal baseline (shared across tools)
2. **CLAUDE.md** — Claude-specific additions (if using Claude Code)
3. **Minimal overlap** — Tool-specific features only in tool-specific files

**Rationale:**
- AGENTS.md becomes the portable standard (like README.md)
- Tool-specific files add precision where needed
- Reduces duplication and maintenance burden

**Ecosystem Trajectory:** AGENTS.md adoption likely to increase throughout 2026 as more tools implement support. By end of 2026, expect most major AI coding tools to read AGENTS.md.

---

## Part 3: Single-Source Schema Generation (Concept)

### Why One File for All Tools Is Unrealistic (Today)

1. **No formal AGENTS.md schema** — Exists as convention, not spec. Each tool interprets "sections" differently.
2. **Tool-specific features diverge** — CLAUDE.md supports import syntax; `.cursorrules` supports JSON structure; others don't.
3. **Adoption gaps** — Copilot, Gemini, Windsurf do not yet read AGENTS.md (as of Feb 2026).
4. **Permission/delegation models differ** — Claude's sub-agent instructions don't map to Cursor's rule hierarchy.

### Practical Workaround: Template System

**Option A: Dual-File Maintenance (Recommended for 2026)**
- Keep `AGENTS.md` as single source of truth for universal context
- Generate tool-specific files via script:
  - Extract sections from AGENTS.md
  - Format for CLAUDE.md, .cursorrules, etc.
  - Reduce manual sync burden

**Option B: Wait-and-See (2027+)**
- Monitor AGENTS.md adoption rate
- Plan migration to single-file when majority of tools support it
- Expected timeline: 12–18 months for broad adoption

---

## Unresolved Questions

1. **AGENTS.md adoption rate in 2026** — Does Copilot actually read AGENTS.md by end of 2026, or is it still aspirational?
2. **Formal AGENTS.md schema** — Will the Agentic AI Foundation publish a strict schema, or remain convention-based?
3. **Windsurf/other emerging tools** — Which instruction file format will new AI coding tools adopt in 2026? AGENTS.md or tool-specific?
4. **MarkItDown MCP integration** — Any official integration with Claude's Model Context Protocol (MCP) for direct file ingestion?
5. **Large document handling** — Does MarkItDown v0.2+ address token-limit issues from v0.1.x?

---

## Sources

### MarkItDown
- [Microsoft MarkItDown GitHub Repository](https://github.com/microsoft/markitdown)
- [MarkItDown PyPI Package](https://pypi.org/project/markitdown/)
- [Real Python: Python MarkItDown Guide](https://realpython.com/python-markitdown/)
- [Trigger.dev: Convert Documents with MarkItDown](https://trigger.dev/docs/guides/python/python-doc-to-markdown/)

### Claude Code (CLAUDE.md)
- [Claude Code: Using CLAUDE.md Files](https://claude.com/blog/using-claude-md-files)
- [Builder.io: How to Write a Good CLAUDE.md File](https://www.builder.io/blog/claude-md-guide)
- [HumanLayer: Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

### Cursor IDE (.cursorrules)
- [GitHub: awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
- [dotcursorrules.com: .cursorrules Guide](https://dotcursorrules.com/)
- [Cursor Community Forum: .cursorrules Discussion](https://forum.cursor.com/t/good-examples-of-cursorrules-file/4346)
- [Medium: What are Cursor Rules](https://medium.com/towards-agi/what-are-cursor-rules-and-how-to-use-them-ec558468d139)

### GitHub Copilot (.github/copilot-instructions.md)
- [GitHub Docs: Adding Custom Instructions for Copilot](https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [GitHub Docs: Repository Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [Medium: Mastering GitHub Copilot Custom Instructions](https://medium.com/@anil.goyal0057/mastering-github-copilot-custom-instructions-with-github-copilot-instructions-md-f353e5abf2b1)

### OpenAI Codex (AGENTS.md)
- [AGENTS.md GitHub Repository](https://github.com/agentsmd/agents.md)
- [AGENTS.md Official Site](https://agents.md/)
- [OpenAI Codex Developers: AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md)

### Google Gemini CLI (GEMINI.md)
- [Google Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Gemini CLI Documentation](https://geminicli.com/docs/)
- [Gemini CLI Configuration](https://geminicli.com/docs/reference/configuration/)
- [Google Cloud Blog: Mastering Gemini CLI](https://cloud.google.com/blog/topics/developers-practitioners/mastering-gemini-cli-your-complete-guide-from-installation-to-advanced-use-cases)

### Cross-Tool Comparisons
- [The Prompt Shelf: .cursorrules vs CLAUDE.md vs AGENTS.md](https://thepromptshelf.dev/blog/cursorrules-vs-claude-md/)
- [DeployHQ: CLAUDE.md, AGENTS.md, and Every AI Config File Explained](https://www.deployhq.com/blog/ai-coding-config-files-guide)
- [TokenCentric: AI Coding Assistant Config Files Compared](https://www.tokencentric.app/blog/ai-coding-config-files-compared)
- [Medium: The Complete Guide to AI Agent Memory Files](https://medium.com/data-science-collective/the-complete-guide-to-ai-agent-memory-files-claude-md-agents-md-and-beyond-49ea0df5c5a9)
