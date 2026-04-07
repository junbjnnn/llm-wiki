#!/usr/bin/env python3
"""Wiki statistics: page counts, cross-ref density, recent activity.

Usage:
    python scripts/stats.py [--json]
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from config import extract_wikilinks, find_wiki_root, get_paths, load_config, parse_frontmatter


def count_sources(sources_dir: Path) -> dict[str, int]:
    """Count files per source category."""
    counts: dict[str, int] = {}
    if not sources_dir.exists():
        return counts
    for subdir in sorted(sources_dir.iterdir()):
        if subdir.is_dir():
            files = [f for f in subdir.iterdir() if f.is_file() and f.name != ".gitkeep"]
            if files:
                counts[subdir.name] = len(files)
    return counts


def analyze_wiki(wiki_dir: Path) -> dict:
    """Analyze wiki pages for statistics."""
    pages_by_type: dict[str, int] = Counter()
    total_links = 0
    page_count = 0
    inbound: dict[str, int] = Counter()

    for md_file in wiki_dir.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        text = md_file.read_text(errors="replace")
        fm = parse_frontmatter(text)
        if fm:
            pages_by_type[fm.get("type", "unknown")] += 1

        links = extract_wikilinks(text)
        total_links += len(links)
        page_count += 1
        for link in links:
            inbound[link] += 1

    # Top connected pages
    top_connected = inbound.most_common(5)

    # Orphans (0 inbound)
    all_names = {f.stem for f in wiki_dir.rglob("*.md") if not f.name.startswith("_")}
    orphan_count = len(all_names - set(inbound.keys()))

    return {
        "total_pages": page_count,
        "pages_by_type": dict(pages_by_type),
        "total_wikilinks": total_links,
        "avg_links_per_page": round(total_links / page_count, 1) if page_count else 0,
        "orphan_count": orphan_count,
        "top_connected": [{"page": p, "inbound": c} for p, c in top_connected],
    }


def recent_log(log_path: Path, count: int = 10) -> list[str]:
    """Get last N entries from log.md."""
    if not log_path.exists():
        return []
    lines = log_path.read_text(errors="replace").strip().split("\n")
    # Filter table rows (start with |, skip header/separator)
    rows = [l for l in lines if l.startswith("|") and "---" not in l and "Date" not in l]
    return rows[-count:]


def main() -> None:
    parser = argparse.ArgumentParser(description="Wiki statistics")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    try:
        wiki_root = find_wiki_root()
        config = load_config(wiki_root)
        paths = get_paths(config, wiki_root)
    except FileNotFoundError:
        print("Error: No .llm-wiki.toml found. Run init-wiki.py first.")
        sys.exit(1)

    wiki_name = config.get("wiki", {}).get("name", "Wiki")
    source_counts = count_sources(paths["sources"])
    wiki_stats = analyze_wiki(paths["wiki"])
    log_entries = recent_log(paths["log"])

    stats = {
        "wiki_name": wiki_name,
        "sources": {"total": sum(source_counts.values()), "by_category": source_counts},
        **wiki_stats,
        "recent_log": log_entries,
    }

    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        print(f"=== {wiki_name} Stats ===\n")
        print(f"Sources: {stats['sources']['total']} files")
        for cat, cnt in source_counts.items():
            print(f"  {cat}: {cnt}")
        print(f"\nWiki Pages: {wiki_stats['total_pages']}")
        for pt, cnt in sorted(wiki_stats["pages_by_type"].items()):
            print(f"  {pt}: {cnt}")
        print(f"\nCross-refs: {wiki_stats['total_wikilinks']} total, "
              f"{wiki_stats['avg_links_per_page']} avg/page")
        print(f"Orphans: {wiki_stats['orphan_count']}")
        if wiki_stats["top_connected"]:
            print("\nMost Connected:")
            for item in wiki_stats["top_connected"]:
                print(f"  {item['page']}: {item['inbound']} inbound links")
        if log_entries:
            print(f"\nRecent Activity (last {len(log_entries)}):")
            for entry in log_entries:
                print(f"  {entry}")


if __name__ == "__main__":
    main()
