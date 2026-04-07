# llm-wiki

Git-based markdown wiki for software teams. No server, no database. Pure git + markdown + Python scripts. Bring your own AI tool.

## Why

- **Tool-agnostic:** Works with Claude, Cursor, Copilot, Gemini, Codex — any tool that reads markdown
- **AGENTS.md standard:** Universal schema readable by any AI tool
- **Compounding knowledge:** Every query can feed insights back into the wiki
- **Zero infrastructure:** git repo = your wiki. No hosting, no server, no API keys

## Architecture

```
project-repo/
├── .wiki/                     # Wiki root (default: subfolder)
│   ├── AGENTS.md              # Universal schema (any AI tool)
│   ├── CLAUDE.md              # Claude-specific additions
│   ├── .llm-wiki.toml         # Config
│   ├── index.md               # Auto-maintained catalog
│   ├── log.md                 # Append-only activity log
│   ├── sources/               # Raw parsed documents (8 categories)
│   │   ├── product/ design/ architecture/ development/
│   │   └── operations/ meetings/ references/ data/
│   ├── wiki/                  # AI-generated pages (9 types)
│   │   ├── summaries/ entities/ concepts/ comparisons/
│   │   ├── syntheses/ chronicles/ decisions/ runbooks/
│   │   ├── postmortems/ glossary.md
│   │   └── _template.md       # In each subdir
│   └── scripts/               # Python utilities
└── src/, docs/, ...           # Your project code
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-org/llm-wiki.git
cd llm-wiki

# 2. Install dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Initialize wiki in your project
python scripts/init-wiki.py --target /path/to/your-project --name "My Project"

# 4. Ingest your first document
python .wiki/scripts/ingest.py meeting-notes.pdf --category meetings --output .wiki/sources/meetings/

# 5. Ask your AI tool to compile and query
# (Open your AI tool, it reads .wiki/AGENTS.md automatically)
```

## Scripts

| Script | Description |
|--------|-------------|
| `init-wiki.py` | Initialize wiki structure |
| `ingest.py` | Parse documents → markdown sources |
| `update-index.py` | Rebuild index.md catalog |
| `lint.py` | Check wiki health (orphans, broken links) |
| `stats.py` | Wiki statistics |
| `graph.py` | Generate Mermaid knowledge graph |
| `setup-qmd.sh` | Setup qmd semantic search (optional) |

## Workflows

1. **Ingest** — Parse docs into `sources/` (script, no AI)
2. **Compile** — AI reads sources → creates wiki pages
3. **Query** — AI searches wiki → answers → feeds insights back
4. **Digest** — AI deep-analyzes a topic across all sources
5. **Lint** — Check wiki consistency and health

## Claude Code Integration

```bash
bash skill/install.sh    # Install /wiki skill
# Then use: /wiki init, /wiki ingest, /wiki compile, /wiki query, etc.
```

## Requirements

- Python 3.11+
- git
- Optional: [qmd](https://github.com/tobi/qmd) for semantic search (recommended for 100+ pages)

## Docs

- [Getting Started](docs/getting-started.md)
- [For PM/PO](docs/for-pm-po.md)
- [For Developers](docs/for-developers.md)
- [Tool-Specific Setup](docs/tool-specific-setup.md)

## License

MIT
