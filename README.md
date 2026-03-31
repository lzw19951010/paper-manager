# deepaper

> One arxiv link &rarr; one expert-level deep analysis note

[![PyPI](https://img.shields.io/pypi/v/deepaper)](https://pypi.org/project/deepaper/)
[![Python](https://img.shields.io/pypi/pyversions/deepaper)](https://pypi.org/project/deepaper/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)

**English** | **[中文](README_CN.md)**

![deepaper demo](demo.gif)

deepaper turns arxiv paper links into structured deep analysis notes. Not summaries -- **actionable research notes**: 7-layer deep analysis, evidence-based mechanism family trees, real citation-based descendant tracking (zero config, no API key), complete pseudocode walkthroughs, and engineering pitfall warnings for reproducers.

Notes are stored as Obsidian-compatible Markdown + YAML, with semantic search, multi-device Git sync, auto-classification (12 subcategories), powered by Claude Code CLI (Max subscription, no API billing).

## deepaper vs Alternatives

| Feature | Zotero | Semantic Scholar | Manual Notes | **deepaper** |
|---------|--------|------------------|-------------|------------|
| **Deep Analysis** | Bookmarks + highlights | Abstract | Hand-written | 7-layer expert analysis |
| **Mechanism Mapping** | None | None | Yes (time-consuming) | Auto mechanism family tree (ancestors/siblings/descendants) |
| **Citation Analysis** | Count only | Citation list | Manual search | Evidence-based descendants (OpenAlex, no API key) |
| **Obsidian Native** | None | None | Native | Native (YAML + Markdown + Dataview) |
| **Semantic Search** | None | Yes (closed-source) | None | Local RAG (ChromaDB) |
| **Multi-device Sync** | Cloud sync (paid) | None | Git sync (DIY) | Git sync (built-in) |
| **API Cost** | None | None | None | None (Max subscription, no per-token billing) |

## Quick Start

```bash
# Install
pip install deepaper

# Initialize
deepaper init

# Add a paper
deepaper add https://arxiv.org/abs/1706.03762
```

A markdown note appears in `papers/` -- open it directly in Obsidian.

## Claude Code Integration

deepaper is designed to work with [Claude Code](https://claude.ai/code). Claude Code CLI handles AI analysis, deepaper handles paper management.

### Installation

Install directly in a Claude Code session:

```bash
# Recommended: isolated install
pipx install deepaper

# Or direct install
pip install deepaper

# Zero-install run (requires uv)
uvx deepaper add https://arxiv.org/abs/1706.03762
```

### Usage in Claude Code

After installation, call directly in Claude Code:

```bash
# Add a paper with deep analysis
! deepaper add https://arxiv.org/abs/2301.00001

# Search existing notes
! deepaper search "attention mechanism"

# Look up citation graph
! deepaper cite 1706.03762
```

> **Prerequisite:** [Claude Code CLI](https://claude.ai/code) installed and authenticated (Max subscription).

## Core Features

### Add Papers

```bash
# Single paper
deepaper add https://arxiv.org/abs/2301.00001

# Multiple papers (ID or URL)
deepaper add 2301.00001 2301.00002 2301.00003

# HuggingFace papers page also works
deepaper add https://huggingface.co/papers/2301.00001

# Re-analyze an existing paper
deepaper add --force https://arxiv.org/abs/2301.00001
```

Pipeline: fetch metadata &rarr; download PDF &rarr; extract key figures &rarr; Claude Code deep analysis &rarr; auto-classify &amp; tag &rarr; generate Markdown note &rarr; ChromaDB index &rarr; cleanup.

### Semantic Search

Can't find a paper from 16 months ago among 50 notes, but remember "attention mechanism for long sequences"?

```bash
deepaper search "attention mechanism for long sequences"
deepaper search "contrastive learning vision" --n 10
```

Returns similarity scores, paper titles, matched note snippets, and arxiv IDs.

### Git Sync

Sync notes across machines:

```bash
# Push updates
deepaper sync

# Custom commit message
deepaper sync --message "Add three NLP papers"
```

Auto-runs `git pull --rebase`, then commits and pushes. Newly pulled files are automatically indexed.

### Tags and Classification

```bash
# Re-tag all papers
deepaper tag

# Only recent papers
deepaper tag --since 2024-01-01

# Limit count
deepaper tag --limit 10
```

Auto-classifies into 12 subcategories:
- **LLM**: pretraining, alignment, reasoning, efficiency, agent
- **RecSys**: matching, ranking, llm-as-rec, generative-rec, system
- **Multimodal & CV**: vlm, generation, understanding
- **Other**: misc

### Citation Lookup

```bash
# Look up citing papers
deepaper cite 1706.03762

# Update an existing note's descendants section
deepaper cite --update 1706.03762
```

Fetches real citing papers from OpenAlex (free, no API key needed), sorted by citation count.

### Rebuild Search Index

```bash
deepaper reindex
```

Re-scans the `papers/` directory and updates the ChromaDB index. Run after bulk imports or note edits.

### Show Configuration

```bash
deepaper config
```

Displays all settings and validates Claude Code CLI availability.

## Analysis Output

Each note contains Zotero-compatible YAML metadata + 7-layer deep analysis:

| Section | Content |
|---------|---------|
| **Executive Summary** | TL;DR (<=100 chars) + mental model analogy + core mechanism in one line |
| **Motivation & First Principles** | Pain points of prior work + key insight (causal chain) + intuitive explanation |
| **Methodology** | Intuitive walkthrough (with figures) + formal spec (flowchart/formulas/numerical example/pseudocode) + design decisions + common confusions |
| **Experiments & Attribution** | Quantitative gains + ablation ranking + credibility check |
| **Critical Review** | Hidden costs + engineering pitfalls + connections to existing techniques |
| **Mechanism Transfer Analysis** | Mechanism decomposition + cross-domain transfer prescriptions + **mechanism family tree** (ancestors/siblings/descendants) |
| **Background Context** | Referenced techniques and common practices (optional) |

### Mechanism Family Tree Example

Using "Scaling Laws for Neural Language Models" as an example:

```
Ancestors:
  - Hestness et al. (2017): Early systematic study of deep learning scaling behavior
  - McCandlish et al. (2018): Critical batch size concept and gradient noise scale theory

Siblings:
  - Rosenfeld et al. (2019): Independent parallel research on model/data scaling
  - EfficientNet (Tan & Le, 2019): Power-law for model size vs performance in vision

Descendants (based on OpenAlex citation data):
  - GPT-3 (Brown et al., 2020): Directly applied scaling laws to train 175B model
  - Chinchilla (Hoffmann et al., 2022): Revised optimal N:D allocation ratio
  - Henighan et al. (2020): Extended methodology to images, video, math, code
```

## Figure Extraction

The analyzer automatically:

1. Scans PDF for pages containing figures/tables (bitmaps, vector graphics, captions)
2. Prioritizes main body pages over appendix
3. Renders up to 20 key pages as JPEG images
4. Passes them to Claude Code for visual analysis
5. Cleans up temporary files after analysis

## Note Format

Notes are stored as `papers/{category}/{paper-title}.md` with YAML metadata:

```yaml
---
title: "Attention Is All You Need"
authors: [Ashish Vaswani, ...]
date: "2017-06-12"
arxiv_id: "1706.03762"
url: "https://arxiv.org/abs/1706.03762"
venue: "NeurIPS 2017"
keywords: [transformer, attention, NLP, sequence-to-sequence]
tags: [NLP, deep-learning, transformer]
citation_count: 6510
status: complete
---
```

## Obsidian Integration

Open the project root as an Obsidian vault. Use [Dataview](https://github.com/blacksmithgu/obsidian-dataview) to query notes:

```dataview
TABLE date, venue, tags
FROM "papers"
WHERE contains(tags, "NLP")
SORT date DESC
```

More queries:

```dataview
-- Recent papers
TABLE date, venue, arxiv_id
FROM "papers"
WHERE status = "complete"
SORT date DESC
LIMIT 20

-- All papers in a specific area
TABLE authors, venue
FROM "papers/llm/pretraining"
SORT date DESC
```

## Multi-device Sync

Seamlessly sync notes across machines:

```bash
# Machine A: add papers and push
deepaper add 2301.00001
deepaper sync

# Machine B: pull and auto-index
deepaper sync
```

`deepaper sync` automatically:
1. Pulls latest changes from remote
2. Commits local new notes
3. Pushes to remote
4. Indexes new files in ChromaDB

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `git_remote` | -- | GitHub/GitLab remote URL (for `deepaper sync`) |
| `model` | `claude-opus-4-6` | Model name for analysis (display/logging only) |
| `tag_model` | `claude-opus-4-6` | Model name for tagging (display/logging only) |
| `papers_dir` | `papers` | Note storage directory |
| `template` | `default` | Analysis prompt template (filename without `.md` in `templates/`) |
| `chromadb_dir` | `.chromadb` | Vector database directory |

Citation analysis (`deepaper cite` and descendant tracking in `deepaper add`) uses the [OpenAlex](https://openalex.org/) open API -- **no API key required**, works out of the box.

For richer influence scoring, optionally configure a [Semantic Scholar API key](https://www.semanticscholar.org/product/api#api-key-form) (free):

```yaml
# config.yaml
semantic_scholar_api_key: "your_key_here"
```

Or via environment variable: `export SEMANTIC_SCHOLAR_API_KEY=your_key`

`config.yaml` is gitignored -- your settings are never committed.

## Custom Analysis Prompts

Edit `templates/default.md` to customize the analysis structure. You can also create new templates (e.g. `templates/my-style.md`) and set `template: "my-style"` in `config.yaml`.

## Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/code) CLI (installed and authenticated)
- Max subscription (no API billing)
- Git (optional, for `deepaper sync`)
- Obsidian (optional, for viewing the vault)

## Install

```bash
pip install deepaper
```

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE).
