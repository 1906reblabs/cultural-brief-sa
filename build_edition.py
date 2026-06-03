#!/usr/bin/env python3
"""
The Cultural Brief (SA) — Edition Build Script
Usage: python3 build_edition.py <content_file.md> [output_dir]

Parses structured Markdown content with YAML frontmatter,
renders via Jinja2 template → final publication-ready HTML.

Token efficiency: editorial content is generated as lean Markdown (~2k tokens).
This script + template handle all HTML/CSS (~0 tokens per edition).
"""

import sys
import re
import os
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml


def parse_frontmatter(text):
    """Extract YAML frontmatter and body from markdown file."""
    match = re.match(r'^---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if not match:
        raise ValueError("No YAML frontmatter found")
    meta = yaml.safe_load(match.group(1))
    body = match.group(2).strip()
    return meta, body


def parse_paragraphs(text):
    """Split text block into individual paragraphs, preserving inline HTML."""
    text = text.strip()
    paras = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]
    return paras


def parse_body(body):
    """
    Parse the structured markdown body into sections:
      - lead_paragraphs
      - cultural_signal
      - dispatches (list)
      - essay (title + paragraphs)
      - closing_paragraphs
    """
    result = {}

    # ── LEAD EDITORIAL ──────────────────────────────────────────
    lead_match = re.search(
        r'## LEAD EDITORIAL\n(.*?)(?=\n---\n## CULTURAL SIGNAL|\Z)',
        body, re.DOTALL
    )
    result['lead_paragraphs'] = parse_paragraphs(lead_match.group(1)) if lead_match else []

    # ── CULTURAL SIGNAL ─────────────────────────────────────────
    signal_match = re.search(
        r'## CULTURAL SIGNAL\n(.*?)(?=\n---\n## DISPATCHES|\Z)',
        body, re.DOTALL
    )
    result['cultural_signal'] = signal_match.group(1).strip() if signal_match else ''

    # ── DISPATCHES ──────────────────────────────────────────────
    dispatches_match = re.search(
        r'## DISPATCHES\n(.*?)(?=\n---\n## LONG ESSAY|\Z)',
        body, re.DOTALL
    )
    dispatches = []
    if dispatches_match:
        dispatch_blocks = re.split(r'\n---\n\n### dispatch_\d+\n\n', dispatches_match.group(1))
        # Also handle first block
        all_blocks = re.findall(
            r'### dispatch_\d+\n\n(.*?)(?=\n---\n\n### dispatch_|\Z)',
            dispatches_match.group(1), re.DOTALL
        )
        for block in all_blocks:
            d = parse_dispatch(block.strip())
            if d:
                dispatches.append(d)
    result['dispatches'] = dispatches

    # ── LONG ESSAY ──────────────────────────────────────────────
    essay_match = re.search(
        r'## LONG ESSAY\n\n\*\*title:\*\* (.*?)\n\*\*type:\*\* (.*?)\n\n(.*?)(?=\n---\n## CLOSING REFLECTION|\Z)',
        body, re.DOTALL
    )
    if essay_match:
        result['essay'] = {
            'title': essay_match.group(1).strip(),
            'type': essay_match.group(2).strip(),
            'paragraphs': parse_paragraphs(essay_match.group(3))
        }
    else:
        result['essay'] = {'title': '', 'type': '', 'paragraphs': []}

    # ── CLOSING REFLECTION ──────────────────────────────────────
    closing_match = re.search(
        r'## CLOSING REFLECTION\n\n(.*?)$',
        body, re.DOTALL
    )
    result['closing_paragraphs'] = parse_paragraphs(closing_match.group(1)) if closing_match else []

    return result


def parse_dispatch(block):
    """Parse a single dispatch block into structured dict."""
    title_m = re.search(r'\*\*title:\*\* (.*)', block)
    meta_m = re.search(r'\*\*meta:\*\* (.*)', block)
    footer_m = re.search(r'\*\*footer:\*\* (.*)', block)
    body_m = re.search(r'\*\*body:\*\* \|\n(.*?)(?=\*\*footer:|\Z)', block, re.DOTALL)

    if not title_m:
        return None

    body_text = body_m.group(1) if body_m else ''
    # Strip leading 2-space indent from YAML literal block
    body_text = re.sub(r'^ {2}', '', body_text, flags=re.MULTILINE)

    return {
        'title': title_m.group(1).strip(),
        'meta': meta_m.group(1).strip() if meta_m else '',
        'body_paragraphs': parse_paragraphs(body_text),
        'footer': footer_m.group(1).strip() if footer_m else ''
    }


def build_edition(content_path, output_dir, template_dir):
    """Main build function."""
    content_path = Path(content_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse content
    raw = content_path.read_text(encoding='utf-8')
    meta, body = parse_frontmatter(raw)
    sections = parse_body(body)

    # Derive ISO date from slug (DD-month-YYYY → YYYY-MM-DD)
    slug = meta.get('slug', '')
    try:
        dt = datetime.strptime(meta['date'], '%d %B %Y')
        iso_date = dt.strftime('%Y-%m-%d')
    except Exception:
        iso_date = slug

    # Build template context
    context = {
        **meta,
        'iso_date': iso_date,
        **sections,
    }

    # Render
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False  # content is trusted editorial text
    )
    template = env.get_template('edition.html.j2')
    html = template.render(**context)

    # Write output
    out_path = output_dir / f"{slug}.html"
    out_path.write_text(html, encoding='utf-8')
    print(f"✓ Built: {out_path}")
    return out_path, meta


def update_index(index_path, meta, editions_archive_entry):
    """
    Update index.html: swap the feature edition block and
    prepend the new entry to the archive list.
    """
    index_path = Path(index_path)
    html = index_path.read_text(encoding='utf-8')

    # ── Update feature edition block ────────────────────────────
    new_feature = f"""      <!-- LATEST EDITION FEATURE — updated {meta['date']} -->
      <div class="feature-edition">
        <p class="edition-label">Latest Edition &nbsp;·&nbsp; {meta['date']}</p>
        <h2>{meta['title']}</h2>
        <p class="standfirst">{meta['standfirst']}</p>
        <div class="edition-links">
          <a href="editions/{meta['slug']}.html" class="read-link">Read this edition &rarr;</a>
          <a href="theculturalbriefsa{meta['slug'].replace('-','')}.pdf" class="pdf-link" target="_blank">Download PDF &rarr;</a>
        </div>
      </div>"""

    html = re.sub(
        r'      <!-- LATEST EDITION FEATURE.*?</div>\s*</div>',
        new_feature + '\n',
        html,
        flags=re.DOTALL,
        count=1
    )

    # ── Prepend to archive list ─────────────────────────────────
    new_li = f"""
        <!-- NEW: {meta['date']} -->
        <li data-tags="{' '.join(meta.get('tags', ['arts']))}">
          <span class="archive-date">{meta['date']}</span>
          <div>
            <a href="editions/{meta['slug']}.html" class="archive-title">{meta['title']}</a>
            <div class="archive-tags" aria-hidden="true">
              {''.join(f'<span class="archive-tag">{t.title()}</span>' for t in meta.get('tags', ['arts']))}
            </div>
          </div>
          <a href="theculturalbriefsa{meta['slug'].replace('-','')}.pdf" class="archive-pdf" target="_blank" aria-label="Download PDF, {meta['date']}">PDF</a>
        </li>
"""

    html = html.replace(
        '        <!-- ADD NEW EDITIONS ABOVE THIS LINE -->',
        new_li + '\n        <!-- ADD NEW EDITIONS ABOVE THIS LINE -->'
    )

    index_path.write_text(html, encoding='utf-8')
    print(f"✓ Index updated: {index_path}")


if __name__ == '__main__':
    content_file = sys.argv[1] if len(sys.argv) > 1 else 'content/20-may-2026.md'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'editions'
    template_dir = sys.argv[3] if len(sys.argv) > 3 else 'templates'
    index_file = sys.argv[4] if len(sys.argv) > 4 else 'index.html'

    out_path, meta = build_edition(content_file, output_dir, template_dir)

    if Path(index_file).exists():
        update_index(index_file, meta, None)
        print(f"✓ Pipeline complete. Edition → {out_path}")
    else:
        print(f"✓ Edition built. No index.html found at '{index_file}' — skipping index update.")
