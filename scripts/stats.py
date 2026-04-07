#!/usr/bin/env python3
"""Wiki statistics: page counts, cross-ref density, quality metrics.

Usage:
    python scripts/stats.py [--json] [--benchmark]
"""

import argparse
import json
import shutil
import sys
from collections import Counter
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


def analyze_wiki(wiki_dir: Path, sources_dir: Path = None, benchmark: bool = False) -> dict:
    """Analyze wiki pages for statistics and optional quality metrics."""
    from datetime import date, timedelta

    pages_by_type: dict[str, int] = Counter()
    total_links = 0
    page_count = 0
    inbound: dict[str, int] = Counter()
    fresh_count = 0
    cited_count = 0
    threshold = date.today() - timedelta(days=30) if benchmark else None

    for md_file in wiki_dir.rglob("*.md"):
        if md_file.name.startswith("_"):
            continue
        text = md_file.read_text(errors="replace")
        fm = parse_frontmatter(text)
        if fm:
            pages_by_type[fm.get("type", "unknown")] += 1
            if benchmark:
                try:
                    updated = date.fromisoformat(str(fm.get("updated", "")))
                    if updated >= threshold:
                        fresh_count += 1
                except (ValueError, TypeError):
                    pass
                if fm.get("citations"):
                    cited_count += 1

        links = extract_wikilinks(text)
        total_links += len(links)
        page_count += 1
        for link in links:
            inbound[link] += 1

    top_connected = inbound.most_common(5)
    all_names = {f.stem for f in wiki_dir.rglob("*.md") if not f.name.startswith("_")}
    orphan_count = len(all_names - set(inbound.keys()))

    result = {
        "total_pages": page_count,
        "pages_by_type": dict(pages_by_type),
        "total_wikilinks": total_links,
        "avg_links_per_page": round(total_links / page_count, 1) if page_count else 0,
        "orphan_count": orphan_count,
        "top_connected": [{"page": p, "inbound": c} for p, c in top_connected],
    }

    if benchmark and page_count > 0:
        source_count = sum(1 for f in sources_dir.rglob("*.md") if f.is_file()) if sources_dir and sources_dir.exists() else 0
        summary_count = pages_by_type.get("summary", 0)
        coverage = min(round((summary_count / source_count * 100) if source_count > 0 else 100), 100)
        avg_inbound = sum(inbound.values()) / page_count
        connectivity = min(round(avg_inbound * 20), 100)
        freshness = round(fresh_count / page_count * 100)
        citation_rate = round(cited_count / page_count * 100)
        health_score = round(coverage * 0.30 + connectivity * 0.25 + freshness * 0.25 + citation_rate * 0.20)
        result["quality"] = {
            "coverage": coverage, "connectivity": connectivity,
            "freshness": freshness, "citation_rate": citation_rate,
            "health_score": health_score,
        }

    return result


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
    parser.add_argument("--benchmark", action="store_true", help="Show quality metrics")
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
    wiki_stats = analyze_wiki(paths["wiki"], paths["sources"], args.benchmark)
    log_entries = recent_log(paths["log"])

    qmd_available = shutil.which("qmd") is not None
    stats = {
        "wiki_name": wiki_name,
        "sources": {"total": sum(source_counts.values()), "by_category": source_counts},
        "search_backend": "qmd" if qmd_available else "grep",
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
        search_status = "qmd (hybrid search)" if qmd_available else "grep only (consider installing qmd)"
        print(f"Search: {search_status}")
        if wiki_stats["top_connected"]:
            print("\nMost Connected:")
            for item in wiki_stats["top_connected"]:
                print(f"  {item['page']}: {item['inbound']} inbound links")
        quality = wiki_stats.get("quality")
        if quality:
            print(f"\nQuality Metrics:")
            print(f"  Coverage:     {quality['coverage']}%")
            print(f"  Connectivity: {quality['connectivity']}%")
            print(f"  Freshness:    {quality['freshness']}%")
            print(f"  Citation:     {quality['citation_rate']}%")
            print(f"  Health Score: {quality['health_score']}/100")
        if log_entries:
            print(f"\nRecent Activity (last {len(log_entries)}):")
            for entry in log_entries:
                print(f"  {entry}")


if __name__ == "__main__":
    main()
