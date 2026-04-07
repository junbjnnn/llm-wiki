#!/usr/bin/env python3
"""Parse documents into markdown for llm-wiki sources.

Usage:
    python scripts/ingest.py <file_or_url> [--category product] [--output sources/product/]
    python scripts/ingest.py <folder> --category meetings
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from config import SOURCE_CATEGORIES, find_wiki_root, load_config


def parse_file(file_path: str) -> str:
    """Convert file to markdown using markitdown."""
    try:
        from markitdown import MarkItDown
    except ImportError:
        print("Error: markitdown not installed. Run: pip install markitdown[all]", file=sys.stderr)
        sys.exit(1)

    md = MarkItDown()
    try:
        result = md.convert(file_path)
        return result.text_content
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def add_frontmatter(content: str, title: str, source_path: str) -> str:
    """Add minimal YAML frontmatter to parsed content."""
    today = date.today().isoformat()
    fm = (
        f"---\n"
        f"title: \"{title}\"\n"
        f"source: \"{source_path}\"\n"
        f"ingested: {today}\n"
        f"---\n\n"
    )
    return fm + content


def ingest_single(file_path: str, category: str, output_dir: Path | None) -> str:
    """Ingest a single file. Returns output path or prints to stdout."""
    path = Path(file_path)
    title = path.stem.replace("-", " ").replace("_", " ").title()
    content = parse_file(file_path)
    result = add_frontmatter(content, title, str(path))

    if output_dir:
        out_file = output_dir / f"{path.stem}.md"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(result)
        return str(out_file)
    else:
        print(result)
        return ""


def ingest_folder(folder: Path, category: str, output_dir: Path) -> list[str]:
    """Ingest all supported files in a folder. Pause every 5."""
    supported = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm",
                 ".csv", ".json", ".xml", ".md", ".txt", ".rst"}
    files = [f for f in sorted(folder.iterdir()) if f.suffix.lower() in supported and f.is_file()]

    if not files:
        print(f"No supported files found in {folder}", file=sys.stderr)
        return []

    results = []
    for i, f in enumerate(files, 1):
        try:
            out = ingest_single(str(f), category, output_dir)
            results.append(out)
            print(f"  [{i}/{len(files)}] Ingested: {f.name}", file=sys.stderr)
        except Exception as e:
            print(f"  [{i}/{len(files)}] FAILED: {f.name} — {e}", file=sys.stderr)

        if i % 5 == 0 and i < len(files):
            print(f"\n  Progress: {i}/{len(files)} files processed.\n", file=sys.stderr)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into llm-wiki sources")
    parser.add_argument("path", help="File, URL, or folder to ingest")
    parser.add_argument("--category", default="references",
                        choices=SOURCE_CATEGORIES, help="Source category")
    parser.add_argument("--output", help="Output directory (default: stdout for single file)")
    args = parser.parse_args()

    input_path = Path(args.path)

    # Determine output dir
    output_dir = None
    if args.output:
        output_dir = Path(args.output)
    elif input_path.is_dir():
        try:
            wiki_root = find_wiki_root()
            config = load_config(wiki_root)
            sources = wiki_root / config.get("paths", {}).get("sources", "sources")
            output_dir = sources / args.category
        except FileNotFoundError:
            output_dir = Path("sources") / args.category

    if input_path.is_dir():
        if output_dir is None:
            print("Error: --output required for folder ingest", file=sys.stderr)
            sys.exit(1)
        results = ingest_folder(input_path, args.category, output_dir)
        print(f"\nIngested {len(results)} files to {output_dir}", file=sys.stderr)
    else:
        ingest_single(args.path, args.category, output_dir)


if __name__ == "__main__":
    main()
