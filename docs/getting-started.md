# Getting Started

## Prerequisites

- Python 3.11+
- git
- An AI tool (Claude Code, Cursor, Copilot, Gemini CLI, etc.)

## Setup

### 1. Get llm-wiki

```bash
git clone https://github.com/your-org/llm-wiki.git
cd llm-wiki
```

### 2. Create Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Initialize wiki in your project

```bash
# Default: creates .wiki/ subfolder in your project
python scripts/init-wiki.py --target /path/to/project --name "My Project Wiki"

# Options:
#   --language vi       Wiki page language (default: en)
#   --root .            Standalone repo mode (no .wiki/ subfolder)
#   --with-qmd          Setup qmd search if installed
```

### 4. Verify setup

```bash
cd /path/to/project
ls .wiki/           # Should show AGENTS.md, sources/, wiki/, etc.
python .wiki/scripts/stats.py   # Should show empty wiki stats
```

## First Ingest

```bash
# Parse a document into wiki source
python .wiki/scripts/ingest.py meeting-notes.pdf --category meetings \
    --output .wiki/sources/meetings/

# Or a URL
python .wiki/scripts/ingest.py https://example.com/api-docs.html --category references \
    --output .wiki/sources/references/
```

## First Compile

Open your AI tool in the project directory. It reads `.wiki/AGENTS.md` automatically.

Ask: *"Compile the wiki — process any uncompiled sources in .wiki/sources/"*

The AI will:
1. Read sources → create wiki pages (summaries, entities, concepts)
2. Add [[wikilinks]] cross-references
3. Update index.md
4. Append to log.md
5. Commit changes

## First Query

Ask your AI tool: *"Search the wiki: how does our authentication work?"*

The AI will:
1. Search index.md and wiki pages
2. Synthesize an answer
3. If the answer has new insights → create a wiki page automatically

## Maintenance

```bash
# Check wiki health
python .wiki/scripts/lint.py

# Rebuild index
python .wiki/scripts/update-index.py

# View stats
python .wiki/scripts/stats.py

# Generate knowledge graph
python .wiki/scripts/graph.py
```
