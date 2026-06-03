# The Cultural Brief (SA) — GitHub Repository Structure

## Overview

The repository follows a **content-first, build-on-push** architecture.  
Editorial content lives in `content/` as lean Markdown files.  
GitHub Actions automatically converts them to HTML on every push.  
The live site is served from the `gh-pages` branch via GitHub Pages.

---

## Directory Tree

```
cultural-brief-sa/
│
├── .github/
│   └── workflows/
│       └── build-edition.yml     ← CI/CD pipeline (auto-build + deploy)
│
├── content/                      ← SOURCE OF TRUTH (commit here, never edit HTML directly)
│   ├── 05-march-2026.md
│   ├── 12-march-2026.md
│   ├── 19-march-2026.md
│   ├── 26-march-2026.md
│   ├── 02-april-2026.md
│   ├── 08-april-2026.md
│   ├── 16-april-2026.md
│   ├── 23-april-2026.md
│   ├── 30-april-2026.md
│   ├── 06-may-2026.md
│   ├── 14-may-2026.md
│   ├── 20-may-2026.md
│   ├── 28-may-2026.md
│   └── [DD-month-YYYY].md        ← Add new editions here every Thursday
│
├── templates/                    ← Jinja2 templates (one-time setup, rarely edited)
│   ├── edition.html.j2           ← Template for individual edition pages
│   └── index.html.j2             ← Template for the archive homepage
│
├── editions/                     ← GENERATED (do not edit manually)
│   ├── 05-march-2026.html
│   ├── 12-march-2026.html
│   ├── 19-march-2026.html
│   ├── 26-march-2026.html
│   ├── 02-april-2026.html
│   ├── 08-april-2026.html
│   ├── 16-april-2026.html
│   ├── 23-april-2026.html
│   ├── 30-april-2026.html
│   ├── 06-may-2026.html
│   ├── 14-may-2026.html
│   ├── 20-may-2026.html
│   ├── 28-may-2026.html
│   └── [auto-generated on push]
│
├── og-images/                    ← Open Graph share card SVGs (one per edition)
│   ├── og-05-march-2026.svg
│   └── [slug-named SVGs]
│
├── index.html                    ← GENERATED archive homepage (rebuilt on every push)
├── about.html                    ← Static page (edit directly)
├── subscribe.html                ← Static page (edit directly)
├── privacy.html                  ← Static page (edit directly)
├── cookie-consent.js             ← Shared JS (edit directly)
├── og-image.svg                  ← Site-level OG image
│
├── build_edition.py              ← Build one edition: .md → HTML + patches index
├── build_all.py                  ← Full rebuild: all .md → HTML + regenerates index
├── requirements.txt              ← Python deps: jinja2, pyyaml
└── REPO-STRUCTURE.md             ← This file
```

---

## The Weekly Publishing Workflow

```
Thursday morning
      │
      ▼
1. Write edition content
   └─ Create: content/DD-month-YYYY.md
      (YAML frontmatter + structured Markdown)
      │
      ▼
2. git add content/DD-month-YYYY.md
   git commit -m "content: DD Month YYYY edition"
   git push
      │
      ▼
3. GitHub Actions triggers automatically
   └─ build-edition.yml detects new .md file
      │
      ├─ Runs: build_edition.py (incremental)
      │        → editions/DD-month-YYYY.html
      │        → index.html (patched with new entry)
      │
      ├─ git commit generated HTML back to main
      │
      └─ Deploys main → gh-pages (live site)
      │
      ▼
4. Live at:
   https://1906reblabs.github.io/cultural-brief-sa/editions/DD-month-YYYY.html
```

---

## Content File Format

Every edition is a single `.md` file with two parts:

### Part 1 — YAML Frontmatter (metadata for index + OG tags)
```yaml
---
date: "5 March 2026"
slug: "05-march-2026"
title: "The Empty Room: On the Goliath Affair..."
standfirst: "South Africa will not hold a pavilion..."
opening_quote:
  text: "The truth isn't always beauty..."
  author: "Nadine Gordimer"
  source: ""
tags: ["arts", "policy"]
og_description: "Short description for social sharing (max 160 chars)"
---
```

### Part 2 — Structured Markdown (rendered into HTML sections)
```
## LEAD EDITORIAL
[300–500 words]

---

## CULTURAL SIGNAL
[40–80 words, present tense]

---

## DISPATCHES

### dispatch_1
**title:** Event Name — Location
**meta:** City · Dates
**body:** |
  Paragraph one.

  Paragraph two.
**footer:** Venue, dates, URL.

---

## LONG ESSAY
**title:** Essay Title
**type:** Institutional argument

[900–1,500 words]

---

## CLOSING REFLECTION
[80–150 words]
```

---

## Build Triggers (GitHub Actions)

| What you push          | What runs              | What updates                        |
|------------------------|------------------------|-------------------------------------|
| `content/*.md`         | Incremental build      | New `editions/*.html` + `index.html`|
| `templates/*.j2`       | Full rebuild (all)     | All `editions/*.html` + `index.html`|
| `build_edition.py`     | Full rebuild (all)     | All `editions/*.html` + `index.html`|
| `build_all.py`         | Full rebuild (all)     | All `editions/*.html` + `index.html`|
| Manual dispatch        | Full rebuild (all)     | All `editions/*.html` + `index.html`|

---

## Token Efficiency

| Approach              | Tokens per edition |
|-----------------------|--------------------|
| Old (inline HTML)     | ~10,000–12,000     |
| New (Markdown only)   | ~2,000–2,500       |
| **Saving**            | **~80% per week**  |

The CSS, structure, and JavaScript are written once in the Jinja2 templates  
and never regenerated. Only the editorial content changes each Thursday.

---

## One-Time Setup (New Machine or Fresh Clone)

```bash
git clone https://github.com/1906reblabs/cultural-brief-sa.git
cd cultural-brief-sa
pip install -r requirements.txt

# Rebuild everything from scratch
python3 build_all.py
```

---

## Adding a New Edition (Local Preview)

```bash
# 1. Create content file
vim content/05-june-2026.md

# 2. Build single edition + update index
python3 build_edition.py content/05-june-2026.md editions templates index.html

# 3. Preview in browser
open editions/05-june-2026.html

# 4. Push — GitHub Actions handles the rest
git add content/05-june-2026.md
git commit -m "content: 5 June 2026 edition"
git push
```
