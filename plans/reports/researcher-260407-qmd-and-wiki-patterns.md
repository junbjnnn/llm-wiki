# Research Report: qmd Integration & LLM Wiki Best Practices
**Date:** 2026-04-07 | **Report ID:** researcher-260407-1345-qmd-and-wiki-patterns

---

## Executive Summary

**qmd** is a production-ready on-device search engine for markdown + code that combines BM25, semantic search, and LLM re-ranking. **LLM Wiki** (Karpathy pattern) is a markdown-first knowledge base architecture where LLMs incrementally build and maintain structured wikis. These two systems complement each other: qmd handles retrieval/discovery, LLM Wiki handles knowledge organization and compilation.

---

## Topic 1: QMD Integration

### What is QMD?

| Aspect | Details |
|--------|---------|
| **Author** | Tobi Lutke (Shopify founder) |
| **Type** | On-device search engine for markdown, code, transcripts, docs |
| **License** | Open source ([GitHub](https://github.com/tobi/qmd)) |
| **Installation** | `npm install -g @tobilu/qmd` or `bun install -g @tobilu/qmd` |
| **Execution Model** | Local-only via node-llama-cpp with GGUF models |

### Core Search Architecture

qmd implements **hybrid search** with three complementary strategies:

1. **BM25 Full-Text** — keyword matching (fast, inverted index)
2. **Vector Semantic Search** — embedding-based similarity (slow, comprehensive)
3. **LLM Re-ranking** — contextual relevance scoring (slow, highest quality)

Query expansion: simple input → lexical + vector + HyDE-style sub-queries → Reciprocal Rank Fusion → LLM reranking.

**Context System:** Metadata (frontmatter/context) attached to collections or file paths is returned with results, enabling better LLM reasoning.

### CLI Usage

```bash
# Setup
qmd collection add ~/notes --name notes
qmd context add qmd://notes "Personal notes and ideas"
qmd embed

# Search modes
qmd search "project timeline"          # BM25 only (fast)
qmd vsearch "how to deploy"            # Vector search (semantic)
qmd query "quarterly planning"         # Hybrid + LLM reranking (best)

# Retrieval
qmd get "meetings/2024-01-15.md"
qmd multi-get "journals/2025-05*.md"
qmd get "#abc123"  # by docid
```

### Collection Management

- **Add:** `qmd collection add <path> --name <name>`
- **Remove:** `qmd collection remove <name>`
- **List:** Query multiple collections in single search
- **Patterns:** File inclusion/exclusion rules per collection
- **Batch Operations:** `--collection <name>` flag on embed, search, query

### Code File Support

| Language | Extensions | Chunking Strategy |
|----------|------------|------------------|
| TypeScript | `.ts`, `.tsx` | AST-aware (tree-sitter) |
| JavaScript | `.js`, `.jsx` | AST-aware |
| Python | `.py` | AST-aware |
| Go | `.go` | AST-aware |
| Rust | `.rs` | AST-aware |
| Others | — | Regex fallback |

**Chunking:** `--chunk-strategy auto` uses AST boundaries (functions, classes, imports); `regex` (default) splits on text; tree-sitter grammars are optional deps with automatic fallback.

### MCP Server Mode

| Aspect | Details |
|--------|---------|
| **Protocol** | Model Context Protocol (MCP) |
| **Tools Exposed** | `query`, `get`, `multi_get`, (others TBD) |
| **Configuration** | Claude Desktop via `mcpServers.qmd` config |
| **Transport** | Unix socket (default) or HTTP (shared daemon) |
| **Model Persistence** | Models stay in VRAM across requests (5min idle timeout) |
| **Startup Penalty** | ~1s on cold start; models remain loaded after |

**HTTP Daemon Mode:**
```bash
qmd mcp --http --daemon
qmd mcp stop
```

### SDK/Library Usage

- **Package:** `@tobilu/qmd` (Node.js, Bun)
- **Exports:** Full TypeScript support for search, retrieval, collection mgmt, indexing
- **Use Case:** Embed qmd into CLI tools, agents, IDE plugins

### Performance Characteristics

| Metric | Baseline |
|--------|----------|
| **Cold Start (MCP)** | ~1s (models load once) |
| **Warm Query (MCP)** | <100ms (models in VRAM) |
| **Idle Timeout** | 5 min before model unload |
| **Re-warm Penalty** | ~1s |
| **Full-Text Search** | Sub-100ms (BM25) |
| **Vector Search** | 500ms–2s (embedding + similarity) |
| **LLM Re-ranking** | 1–5s (depends on result set size) |
| **Max Collection Size** | ~500K words well-tested; scale beyond TBD |

### Integration with AI Coding Tools

| Tool | Integration Method | Status |
|------|-------------------|--------|
| **Claude Code / Claude Desktop** | MCP server | Native support (add to mcpServers config) |
| **Cursor IDE** | MCP or SDK integration | Custom implementation via SDK |
| **GitHub Copilot** | Not supported | Would require Copilot extension API (not available) |
| **VSCode** | Via extension using SDK | Third-party implementations exist |

**Recommended Flow for LLMs:**
- Query qmd → Get chunk + context → Synthesize answer → Option to file new wiki page back

### Tree-Sitter Support Details

qmd uses [web-tree-sitter](https://www.npmjs.com/package/web-tree-sitter) for AST parsing. Grammar support:
- Built-in: TypeScript, JavaScript, Python, Go, Rust
- Optional: Additional grammars available via npm
- **Fallback:** Regex chunking if grammar missing
- **No markdown tree-sitter used** (qmd treats markdown as text with optional YAML frontmatter parsing)

---

## Topic 2: LLM Wiki Best Practices

### Karpathy Pattern: Core Architecture

**Problem Solved:** Traditional RAG re-derives answers from raw documents every time. **Solution:** LLM increments and maintains a structured wiki that compounds with every source and query.

**Three-Layer Architecture:**

1. **Raw Sources** — Immutable corpus (papers, articles, images, datasets, etc.)
2. **Wiki** — LLM-compiled markdown files with summaries, entities, concepts, cross-refs
3. **Schema** — Configuration (like CLAUDE.md) defining conventions and workflows

### File Organization & Structure

```
wiki/
├── raw/                    # Immutable source documents
│   ├── papers/
│   ├── articles/
│   └── datasets/
├── index.md               # Content catalog (all pages with summaries)
├── log.md                 # Append-only ingestion/query log
├── entities/              # Named people, organizations, projects
├── concepts/              # Ideas, techniques, frameworks
├── [topic-pages]/         # Topic-specific organized content
└── schema.md              # Wiki conventions & workflows
```

### Page Templates & Metadata Convention

**Frontmatter (YAML):**
```yaml
---
title: Page Title
tags: [topic1, topic2]
created: 2025-04-07
updated: 2025-04-07
sources: 3
confidence: high
backlinks: [page-a, page-b]
---
```

**Frontmatter Metadata (Required):**
- `tags` — searchable topics
- `created`, `updated` — versioning
- `sources` — count of raw sources informing this page (attribution)
- `confidence` — [high|medium|low] (claim strength)
- `backlinks` — pages that reference this page (bidirectional)

**Content Structure:**
1. **Summary** (1–2 sentences)
2. **Key Points** (bullet list)
3. **Details** (prose with examples)
4. **Cross-references** (Obsidian-style `[[page-name]]` wikilinks)
5. **Sources** (external links, raw docs)

### Cross-Referencing Convention

- **Internal Links:** `[[entity-name]]`, `[[concept-name]]` (Obsidian wikilink format)
- **External Links:** Standard markdown `[title](url)`
- **Bidirectional Requirement:** If A→B, then B→A (maintain symmetry)
- **Tool Support:** Obsidian + Dataview plugin for automatic backlink generation

### Core Workflows

#### 1. Ingest Process
1. User provides raw source (PDF, article, GitHub repo, web link)
2. LLM reads source, extracts key takeaways
3. LLM writes summary page (source-specific, dated, tagged)
4. LLM updates index.md with new page entry
5. LLM updates/creates relevant entity pages (people, orgs, projects)
6. LLM updates/creates relevant concept pages (ideas, techniques)
7. LLM adds wikilinks ([[...]]) for cross-references
8. LLM appends entry to log.md (timestamp, source, changes made)

#### 2. Query Workflow
1. User asks question
2. LLM searches wiki for relevant pages (qmd, grep, or index.md)
3. LLM synthesizes answer from wiki pages + cites sources
4. LLM optionally files valuable insights as new wiki page

#### 3. Maintenance (Lint) Workflow
1. LLM periodically reviews wiki for:
   - Contradictions between pages
   - Outdated claims superseded by newer sources
   - Orphaned pages (no inbound backlinks)
   - Important concepts missing their own page
   - Missing cross-references
2. LLM proposes fixes (edits, deletions, new pages)
3. User reviews and approves changes

### Git Workflow for Team Collaboration

| Aspect | Recommendation |
|--------|-----------------|
| **Branch Strategy** | Feature branches per wiki section/feature |
| **Merge Conflicts** | Rare if: sections are isolated + metadata clear |
| **Concurrent Edits** | If 2+ people edit same file, use git worktrees (avoid conflicts) |
| **Commit Frequency** | After each ingest/maintenance pass (1–3 commits/day) |
| **Commit Message** | `docs: ingest {source-name}` or `docs: lint {section}` |
| **PR Size** | Keep to single ingest or single maintenance pass |
| **Merge Conflicts Resolution** | Manual review required; metadata may differ |

**Best Practice:** Use git worktrees for parallel team work.
```bash
git worktree add ~/karpathy-wiki-team-a
git worktree add ~/karpathy-wiki-team-b
# Each team member works in isolation, commits to their worktree
# Pull main regularly, merge feature branches explicitly
```

### Implementation Frameworks & Tools

| Tool/Framework | Type | Status | Notes |
|---|---|---|---|
| **Obsidian** | Frontend | Recommended | Local-first, plugin ecosystem (Dataview, Web Clipper) |
| **Obsidian Web Clipper** | Ingestion | Recommended | Converts web → markdown with local image storage |
| **Dataview** | Query/Index | Recommended | Dynamic tables/lists from frontmatter metadata |
| **LLM Wiki Compiler** (ussumant) | Automation | Active | Claude Code plugin implementing Karpathy pattern |
| **obsidian-wiki** (Ar9av) | Framework | Active | Full LLM wiki + Obsidian integration |
| **karpathy-wiki** (toolboxmd) | Framework | Active | Claude Code skills for wiki building |
| **knowledge-engine** (tashisleepy) | System | Active | LLM Wiki + Memvid (video memory) |

### Scaling Characteristics

| Metric | Baseline | Notes |
|--------|----------|-------|
| **Optimal Wiki Size** | ~100 pages, ~400K words | ~5–10KB per page avg |
| **Token Efficiency** | Up to 95% reduction vs naive RAG | At medium scale (~100 pages) |
| **Index Performance** | Sub-second index.md scan | Markdown-based catalog is fast |
| **LLM Overhead** | 2–5 tokens for search + synthesis | Much lower than full document loading |
| **Max Tested Scale** | ~500–1000 pages | Performance TBD beyond |
| **Git Repo Growth** | Linear with content | History accumulates; consider git filter/archive |

### Template Structure for Obsidian Integration

**Entity Page Template (e.g., person, org, project):**
```markdown
---
title: {Name}
type: entity
tags: [category, topic]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: {count}
confidence: high
---

## Overview
{1–2 sentence summary}

## Key Details
- Detail 1
- Detail 2

## Related Concepts
[[concept-name]]
[[another-concept]]

## Related Entities
[[entity-name]]

## Sources
- [Source 1](url)
```

**Concept Page Template:**
```markdown
---
title: {Concept Name}
type: concept
tags: [category, topic]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: {count}
confidence: high
---

## Definition
{Clear, LLM-ready definition}

## Key Principles
1. Principle 1
2. Principle 2

## Examples
{Concrete examples}

## Related Concepts
[[related-concept-1]]

## Sources
- [Source 1](url)
```

### Community Implementations & Adoption

- **Claude Code Plugins:** llm-wiki-compiler, wiki-skills (3+ plugins implementing pattern)
- **Obsidian Frameworks:** obsidian-wiki, knowledge-engine (active communities)
- **Academic Interest:** Published in medium.com, multiple blog posts covering architecture
- **Enterprise:** Limited adoption (most evidence from indie/researcher communities)

---

## Comparison: QMD vs LLM Wiki Roles

| Aspect | QMD | LLM Wiki |
|--------|-----|----------|
| **Primary Purpose** | Search/retrieval engine | Knowledge organization & compilation |
| **Input** | Raw markdown + code (any source) | Structured, curated markdown (LLM-compiled) |
| **Output** | Ranked search results | Refined knowledge, new insights, updated wiki |
| **Execution Model** | Local inference (search) | Agentic workflows (ingest, lint, query) |
| **Use Case** | "Find what I know" | "Build what I know" + "Refine what I know" |
| **Learning Curve** | Low (CLI) | Medium–High (requires schema + workflows) |
| **Scalability** | 500K+ words tested | ~100–1000 pages optimal; unknown beyond |

**Architectural Integration:**
```
Raw Sources → [LLM Wiki Ingest] → Structured Wiki → [QMD Index] → Search + Retrieval → [LLM Query] → New Insights
```

---

## Adoption Recommendations

### For llm-wiki Project

1. **LLM Wiki as Core:** Use Karpathy pattern for primary wiki structure (entity + concept pages, index.md, log.md, schema.md).

2. **qmd as Search Backend:** Index wiki with qmd for fast retrieval during LLM query workflows.

3. **Integration Points:**
   - Post-ingest: Run `qmd embed` to update search index
   - Query: LLM uses `qmd query` via MCP to find relevant pages
   - Maintenance: `qmd vsearch` to identify orphaned/contradictory content

4. **Git Workflow:** Feature branches per section; worktrees for parallel team contribution.

5. **Frontmatter Standard:** Adopt metadata template above; enforce via schema.md.

6. **Obsidian Frontend:** Recommended for human editing; Dataview for dynamic navigation.

### Why This Pairing Works

- **LLM Wiki** provides _structure_ and _intent_ (what to know, why it matters)
- **qmd** provides _speed_ and _scale_ (find relevant knowledge fast)
- **qmd's context system** + **LLM Wiki's frontmatter** = optimal LLM reasoning
- **Markdown** is the common format (no conversion overhead)
- **Git** is the version control (free history + collaboration)

---

## Unresolved Questions

1. **qmd Code Search Performance:** What is latency for searching 1000+ code files? Are there benchmarks?

2. **LLM Wiki at Scale:** What happens beyond 1000 pages? Does index.md become unwieldy? When to split into multiple wikis?

3. **Concurrent Edit Conflict Resolution:** In git worktree + team model, how to handle merge conflicts on shared frontmatter (e.g., `sources` count)?

4. **QMD Custom Embedding Models:** Can qmd use custom embedding models (e.g., fine-tuned for domain)? Current docs mention GGUF only.

5. **Tree-sitter + Markdown:** Why doesn't qmd use tree-sitter for markdown AST-aware chunking? Would this improve semantic clarity of markdown headings?

6. **Obsidian Scaling:** Does Obsidian's graph view become slow with 1000+ pages? Any reported limits?

---

## Sources

- [QMD GitHub Repository](https://github.com/tobi/qmd)
- [Introducing lazyqmd: a TUI for QMD](https://alexanderzeitler.com/articles/introducing-lazyqmd-a-tui-for-qmd/)
- [Karpathy's LLM Wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [LLM Wiki Compiler Plugin](https://github.com/ussumant/llm-wiki-compiler)
- [Karpathy's LLM Wiki: The Complete Guide](https://antigravity.codes/blog/karpathy-llm-wiki-idea-file)
- [LLM Wiki vs RAG: When to Use Markdown Knowledge Bases](https://www.mindstudio.ai/blog/llm-wiki-vs-rag-markdown-knowledge-base-comparison)
- [Semantic Code Indexing with Tree-sitter](https://medium.com/@email2dineshkuppan/semantic-code-indexing-with-ast-and-tree-sitter-for-ai-agents-part-1-of-3-eb5237ba687a)
- [Git Workflow Best Practices](https://www.atlassian.com/git/tutorials/comparing-workflows)
- [obsidian-wiki Framework](https://github.com/Ar9av/obsidian-wiki)
- [karpathy-wiki Framework](https://github.com/toolboxmd/karpathy-wiki)
- [DAIR.AI Academy: LLM Knowledge Bases](https://academy.dair.ai/blog/llm-knowledge-bases-karpathy)
