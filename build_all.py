#!/usr/bin/env python3
"""
The Cultural Brief (SA) — Full Rebuild Script
Usage: python3 build_all.py [--content-dir DIR] [--output-dir DIR]
                             [--template-dir DIR] [--index FILE]

Rebuilds every edition HTML from every .md file in content/,
then regenerates index.html from scratch.

Run this when:
  - The Jinja2 template changes
  - The build script changes
  - You need to onboard a new environment
  - GitHub Actions runs a full rebuild
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
import yaml

# ── Import single-edition builder ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from build_edition import parse_frontmatter, parse_body, build_edition


# ── Month ordering helper ───────────────────────────────────────────────────
MONTH_ORDER = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}


def slug_to_date(slug):
    """Convert DD-month-YYYY slug to a sortable datetime. Returns datetime or epoch on failure."""
    try:
        return datetime.strptime(slug, '%d-%B-%Y'.lower()) if False else \
               _parse_slug_date(slug)
    except Exception:
        return datetime(1970, 1, 1)


def _parse_slug_date(slug):
    """Parse slugs like '20-may-2026' → datetime(2026, 5, 20)."""
    parts = slug.split('-')
    if len(parts) < 3:
        return datetime(1970, 1, 1)
    try:
        day = int(parts[0])
        month = MONTH_ORDER.get(parts[1].lower(), 1)
        year = int(parts[2])
        return datetime(year, month, day)
    except (ValueError, IndexError):
        return datetime(1970, 1, 1)


def load_all_meta(content_dir):
    """
    Load frontmatter from every .md file in content_dir.
    Returns list of meta dicts sorted newest-first.
    """
    content_dir = Path(content_dir)
    editions = []

    for md_file in sorted(content_dir.glob('*.md')):
        try:
            raw = md_file.read_text(encoding='utf-8')
            meta, _ = parse_frontmatter(raw)
            meta['_file'] = md_file
            meta['_sort_date'] = _parse_slug_date(meta.get('slug', ''))
            editions.append(meta)
        except Exception as e:
            print(f"⚠ Skipping {md_file.name}: {e}")

    # Newest first
    editions.sort(key=lambda m: m['_sort_date'], reverse=True)
    return editions


def build_index(editions, index_template_path, output_path):
    """
    Regenerate index.html from scratch using the index Jinja2 template
    and all edition metadata sorted newest-first.
    """
    index_template_path = Path(index_template_path)
    output_path = Path(output_path)

    if not index_template_path.exists():
        print(f"⚠ Index template not found at {index_template_path} — skipping index regeneration")
        return

    template_dir = str(index_template_path.parent)
    template_name = index_template_path.name

    env = Environment(loader=FileSystemLoader(template_dir), autoescape=False)
    template = env.get_template(template_name)

    latest = editions[0] if editions else {}

    html = template.render(
        latest=latest,
        editions=editions,
        build_date=datetime.now().strftime('%d %B %Y'),
    )

    output_path.write_text(html, encoding='utf-8')
    print(f"✓ Index rebuilt: {output_path} ({len(editions)} editions)")


def main():
    parser = argparse.ArgumentParser(description='Full rebuild of all Cultural Brief editions')
    parser.add_argument('--content-dir',  default='content',   help='Directory with .md source files')
    parser.add_argument('--output-dir',   default='editions',  help='Directory for generated HTML editions')
    parser.add_argument('--template-dir', default='templates', help='Directory with Jinja2 templates')
    parser.add_argument('--index',        default='index.html', help='Output path for index.html')
    args = parser.parse_args()

    content_dir  = Path(args.content_dir)
    output_dir   = Path(args.output_dir)
    template_dir = Path(args.template_dir)
    index_path   = Path(args.index)

    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Build all editions ───────────────────────────────────
    md_files = sorted(content_dir.glob('*.md'))
    if not md_files:
        print(f"⚠ No .md files found in {content_dir}")
        sys.exit(1)

    print(f"\nBuilding {len(md_files)} editions...\n")
    built = 0
    for md_file in md_files:
        try:
            build_edition(md_file, output_dir, template_dir)
            built += 1
        except Exception as e:
            print(f"✗ Failed {md_file.name}: {e}")

    print(f"\n✓ Built {built}/{len(md_files)} editions")

    # ── 2. Regenerate index ─────────────────────────────────────
    editions = load_all_meta(content_dir)

    index_template = template_dir / 'index.html.j2'
    if index_template.exists():
        build_index(editions, index_template, index_path)
    else:
        print(f"⚠ No index template found at {index_template}")
        print("  Run build_edition.py individually to patch the existing index.html")

    print(f"\n✓ Full rebuild complete — {built} editions, index updated\n")


if __name__ == '__main__':
    main()
