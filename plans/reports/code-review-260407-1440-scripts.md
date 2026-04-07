# Code Review: llm-wiki Python Scripts

**Date:** 2026-04-07
**Reviewer:** code-reviewer
**Scope:** scripts/*.py, scripts/setup-qmd.sh, skill/SKILL.md, skill/install.sh, skill/templates/agents-md.md
**LOC:** ~1024 (Python) + ~42 (bash) + ~113 (markdown)

## Overall Assessment

Codebase is clean, well-structured, and follows KISS/YAGNI principles. Scripts are focused, modular, and share config properly. No eval/exec, no injection vectors, safe file handling throughout. A few issues worth fixing — one critical, a few high, rest minor.

---

## Critical Issues

### 1. [CRITICAL] `lint.py` auto-fix corrupts frontmatter (line 195)

```python
text = text.replace("---\n", f"---\nupdated: {today}\n", 1)
```

This replaces the FIRST occurrence of `---\n`, inserting `updated:` immediately after the opening delimiter. Result:

```yaml
---
updated: 2026-04-07
title: My Page
---
```

**But worse:** if `---` appears in body content (e.g., horizontal rules), the `count=1` only saves it from multi-replace — it still targets the opening `---` of frontmatter, placing `updated` BEFORE other fields. While not broken YAML, it's fragile. The real bug: if the file does NOT start with `---` (no frontmatter), this still replaces the first `---\n` found anywhere in body text, corrupting content.

**Fix:** Use `parse_frontmatter()` result + reconstruct, or at minimum guard with `if text.startswith("---")`.

### 2. [CRITICAL] `lint.py` exceeds 200-line limit (221 lines)

Per project rules, code files must stay under 200 lines. `lint.py` is at 221. Needs modularization — extract check functions to a separate module (e.g., `lint-checks.py`).

---

## High Priority

### 3. [HIGH] DRY violation: `SOURCE_CATEGORIES` and `WIKI_SUBDIRS` duplicated

`init-wiki.py` (lines 21-28) duplicates `SOURCE_CATEGORIES` and `WIKI_SUBDIRS` from `config.py` (lines 17-25). `init-wiki.py` does not import from `config.py`.

**Why it matters:** If categories/subdirs change, `init-wiki.py` gets out of sync silently.

**Fix:** `from config import SOURCE_CATEGORIES, WIKI_SUBDIRS` in `init-wiki.py`.

### 4. [HIGH] `subprocess.run` without `check=True` (init-wiki.py:138)

```python
subprocess.run(["bash", str(setup_script)], cwd=str(wiki_root))
```

Silent failure — if qmd setup fails, user gets no feedback. Return code ignored.

**Fix:** Either `check=True` with try/except, or capture and check `result.returncode`.

### 5. [HIGH] Mermaid node IDs not sanitized (graph.py:78, 89, 91)

```python
lines.append(f"    {name}[\"{label}\"]{style}")
```

If a page filename contains spaces, dots, or special chars (e.g., `my page.md`, `v2.0-release.md`), the Mermaid node ID will be invalid. Mermaid IDs must be alphanumeric + hyphens + underscores.

**Fix:** Sanitize node IDs:
```python
def sanitize_id(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)
```

### 6. [HIGH] `graph.py` label quotes not escaped (line 78)

If a page title contains `"`, the Mermaid syntax breaks:
```
node["My "Special" Page"]  # Invalid Mermaid
```

**Fix:** `label = label.replace('"', "'")` or escape with `#quot;`.

### 7. [HIGH] `ingest.py` claims URL support but doesn't handle URLs

Docstring says `<file_or_url>` and SKILL.md says `python scripts/ingest.py <file_or_url>`, but the code only handles file paths — `Path(args.path)` will fail or produce wrong results for URLs.

**Fix:** Either remove URL from docs, or add URL detection + handling (e.g., markitdown may support URLs directly).

---

## Medium Priority

### 8. [MED] `update-index.py` display name logic is wrong (line 70)

```python
display = page_type.replace("adr", "Decisions (ADR)").title()
```

This applies `.title()` AFTER replace, so `"Decisions (ADR)"` becomes `"Decisions (Adr)"`. The `.title()` lowercases non-initial characters.

**Fix:** Handle ADR as special case before `.title()`, or use a mapping dict.

### 9. [MED] `parse_frontmatter` in `config.py` uses lazy import of yaml (line 77)

`import yaml` inside function body. While functional, it means import errors only surface at runtime when the function is first called. All other scripts import at module level.

**Consideration:** This may be intentional to avoid requiring pyyaml for scripts that don't parse frontmatter. Acceptable if documented.

### 10. [MED] `config.py` `resolve_wikilink` returns first `rglob` match non-deterministically

```python
for md in wiki_dir.rglob(f"{name}.md"):
    return md  # Returns first match
```

If multiple subdirs contain a file with the same name, behavior is OS-dependent (filesystem ordering). Could lead to inconsistent link resolution across machines.

**Mitigation:** Log a warning when multiple matches found, or prefer specific subdirs.

### 11. [MED] `install.sh` uses bare glob without quoting (line 18)

```bash
cp "$SCRIPT_DIR/templates/"* "$SKILL_DIR/templates/"
```

If templates dir is empty, glob expands to literal `*` and `cp` fails. Not critical since templates always exist, but fragile.

### 12. [MED] `setup-qmd.sh` WIKI_ROOT detection assumes script is in `scripts/` directly under wiki root (line 16)

```bash
WIKI_ROOT="$(dirname "$SCRIPT_DIR")"
```

This breaks if the script is run from a different location or if wiki root is `.` (not `.wiki/`). The Python scripts use `find_wiki_root()` which walks up — more robust.

---

## Low Priority

### 13. [LOW] `stats.py` iterates wiki dir twice

`analyze_wiki()` calls `wiki_dir.rglob("*.md")` twice — once for analysis (line 37), once for orphan detection (line 55). Could combine into single pass.

### 14. [LOW] `ingest.py` `parse_file` calls `sys.exit(1)` on error

Functions should raise exceptions, not exit. `main()` should handle exits. Currently prevents reuse of `parse_file` as a library function.

### 15. [LOW] `update-index.py` `generate_index` has `.title()` applied to "adr" display name

Same issue as #8 — `"Decisions (ADR)".title()` produces `"Decisions (Adr)"`. Listed separately as it appears in display logic.

### 16. [LOW] No `encoding="utf-8"` on `write_text()` / `read_text()` calls

Most calls use default encoding. On some Windows systems this could default to cp1252. Not an issue on macOS/Linux but reduces portability.

---

## Positive Observations

- **Clean separation of concerns:** config.py as shared module, each script focused
- **No security issues:** No eval/exec, no shell injection, safe YAML loading (`safe_load`), binary mode for TOML
- **Good CLI patterns:** argparse with help text, --dry-run support, stderr for progress
- **Error handling:** `errors="replace"` on file reads prevents crashes on bad encoding
- **Consistent structure:** All scripts follow same pattern: imports → functions → main → `__name__` guard
- **Template-based init:** No hardcoded content, extensible via YAML templates

---

## Recommended Actions (priority order)

1. **Fix lint.py auto-fix** — guard against missing frontmatter, reconstruct properly
2. **Modularize lint.py** — extract check functions to stay under 200 lines
3. **Import constants in init-wiki.py** from config.py instead of duplicating
4. **Add `check=True`** or return code handling to subprocess.run
5. **Sanitize Mermaid node IDs** and escape label quotes in graph.py
6. **Fix `.title()` on ADR** display name in update-index.py
7. **Clarify URL support** in ingest.py docs vs implementation

---

## Metrics

| Metric | Value |
|--------|-------|
| Files reviewed | 11 |
| Total Python LOC | 1024 |
| Critical issues | 2 |
| High issues | 5 |
| Medium issues | 5 |
| Low issues | 4 |
| Files over 200 lines | 1 (lint.py: 221) |
| Security issues | 0 |
| eval/exec usage | 0 |

---

## Unresolved Questions

- Is URL support in `ingest.py` planned or should docs be corrected?
- Is the lazy `import yaml` in `config.py` intentional to avoid hard dependency?
- Should `resolve_wikilink` warn on ambiguous matches or is first-match acceptable?
