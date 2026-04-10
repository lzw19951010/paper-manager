# Per-Paper Analysis v2.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add depth signals, figure image embedding, compact confusion-point format, and coverage gates to the deepaper pipeline while preserving v2 4-section structure.

**Architecture:** Single-file enrichment of existing v2 pipeline. New `extract_core_figure_images()` in extractor renders PDF pages as PNG. New gates H11 (figure embed) and H12 (section-bucket coverage) replace broken H2. Writer prompts gain depth requirements (D1/D2/D3). Save command outputs P2 directory layout.

**Tech Stack:** Python 3.11+, pytest, pdftoppm (poppler-utils), Pillow, typer, PyYAML, fitz (PyMuPDF)

**Spec:** `docs/superpowers/specs/2026-04-08-per-paper-analysis-v2.1-depth-design.md`

---

## File Structure

| File | Responsibility | Change Type |
|------|---------------|-------------|
| `tests/golden/olmo-3.md` | Frozen v2 output for regression comparison | Create (copy) |
| `tests/update_golden.py` | CLI helper to refresh golden files | Create |
| `tests/test_golden_regression.py` | Structural metric regression test | Create |
| `tests/test_h11_figure_embed.py` | H11 gate unit tests | Create |
| `tests/test_h12_section_bucket.py` | H12 gate unit tests | Create |
| `tests/test_frontmatter.py` | arxiv_id preservation assertion | Create |
| `src/deepaper/registry.py` | Add `top_level_sections` to `compute_paper_profile()` | Modify |
| `src/deepaper/extractor.py` | Add `extract_core_figure_images()` | Modify |
| `src/deepaper/gates.py` | Add H11, H12; skip H2; update `run_hard_gates()` | Modify |
| `src/deepaper/output_schema.py` | Add H12 config constants | Modify |
| `src/deepaper/prompt_builder.py` | Add depth + figure embed + confusion format constraints | Modify |
| `src/deepaper/defaults.py` | Update DEFAULT_TEMPLATE confusion-point example | Modify |
| `src/deepaper/cli.py` | Update `save` for P2 layout; update `gates` to pass profile | Modify |
| `src/deepaper/writer.py` | Update `write_paper_note` for P2 directory output | Modify |

---

### Task 0: Freeze baseline (golden reference)

**Files:**
- Create: `tests/golden/olmo-3.md`
- Create: `tests/update_golden.py`

This must happen BEFORE any code changes. It freezes the current v2 output for regression comparison.

- [ ] **Step 1: Copy current output to golden**

```bash
mkdir -p tests/golden
cp papers/llm/pretraining/olmo-3.md tests/golden/olmo-3.md
```

- [ ] **Step 2: Create update_golden.py helper**

```python
# tests/update_golden.py
"""Helper to refresh golden files from current pipeline output.

Usage: python -m tests.update_golden olmo-3
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent / "golden"
# Map slug to current output path (v2.1 P2 layout)
PAPER_PATHS = {
    "olmo-3": "papers/llm/pretraining/olmo-3/olmo-3.md",
}
# Fallback: v2 flat layout
PAPER_PATHS_V2 = {
    "olmo-3": "papers/llm/pretraining/olmo-3.md",
}


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: python -m tests.update_golden <slug>")
        print(f"Available: {', '.join(PAPER_PATHS)}")
        sys.exit(1)

    slug = sys.argv[1]
    source = Path(PAPER_PATHS.get(slug, ""))
    if not source.exists():
        source = Path(PAPER_PATHS_V2.get(slug, ""))
    if not source.exists():
        print(f"Error: no output found for {slug}")
        sys.exit(1)

    dest = GOLDEN_DIR / f"{slug}.md"
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    print(f"Updated golden: {dest}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verify golden file exists and matches source**

```bash
diff papers/llm/pretraining/olmo-3.md tests/golden/olmo-3.md
```

Expected: no diff (files are identical).

- [ ] **Step 4: Commit**

```bash
git add tests/golden/olmo-3.md tests/update_golden.py
git commit -m "test: freeze OLMo 3 v2 output as golden reference for regression testing"
```

---

### Task 1: Add `top_level_sections` to `compute_paper_profile()`

**Files:**
- Modify: `src/deepaper/registry.py` (function `compute_paper_profile` at line 377)
- Create: `tests/test_h12_section_bucket.py` (partial — only the profile test for now)
- Modify: `tests/test_registry.py` (add assertion for new field)

- [ ] **Step 1: Write failing test**

Add to `tests/test_registry.py`:

```python
def test_compute_paper_profile_top_level_sections():
    """compute_paper_profile must return top_level_sections with page ranges."""
    from deepaper.registry import compute_paper_profile

    # Minimal 3-page paper: Abstract on p1, Method on p2, Experiments on p3
    text_by_page = {
        1: "Abstract\nThis paper presents...",
        2: "3 Method\nWe propose a novel approach...",
        3: "4 Experiments\nWe evaluate on three benchmarks...",
    }
    profile = compute_paper_profile(text_by_page, {})
    sections = profile.get("top_level_sections", [])

    assert len(sections) >= 2, f"Expected ≥2 sections, got {sections}"
    names = [s["title"] for s in sections]
    assert "Abstract" in names
    assert "Method" in names or "Experiments" in names

    # Each section must have page_start and page_end
    for s in sections:
        assert "page_start" in s, f"Missing page_start in {s}"
        assert "page_end" in s, f"Missing page_end in {s}"
        assert s["page_start"] <= s["page_end"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_registry.py::test_compute_paper_profile_top_level_sections -v
```

Expected: FAIL — `top_level_sections` key missing from profile dict.

- [ ] **Step 3: Implement `top_level_sections` extraction**

In `src/deepaper/registry.py`, add a helper function before `compute_paper_profile`:

```python
def _compute_top_level_sections(
    text_by_page: dict[int, str],
) -> list[dict]:
    """Extract top-level section boundaries with page ranges.

    Returns list of {title, page_start, page_end} dicts sorted by page_start.
    """
    # Find the first section heading on each page
    page_section: list[tuple[int, str]] = []
    for page in sorted(text_by_page.keys()):
        text = text_by_page[page]
        for m in _SECTION_RE.finditer(text):
            canonical = _canonical_section(m.group(1).strip())
            page_section.append((page, canonical))
            break  # only first heading per page

    if not page_section:
        return []

    # Deduplicate: keep first occurrence of each canonical name
    seen: set[str] = set()
    unique: list[tuple[int, str]] = []
    for page, name in page_section:
        if name not in seen:
            seen.add(name)
            unique.append((page, name))

    # Build page ranges
    max_page = max(text_by_page.keys())
    sections: list[dict] = []
    for i, (page_start, name) in enumerate(unique):
        if i + 1 < len(unique):
            page_end = unique[i + 1][0] - 1
        else:
            page_end = max_page
        sections.append({
            "title": name,
            "page_start": page_start,
            "page_end": page_end,
        })

    return sections
```

Then in `compute_paper_profile`, add to the returned dict:

```python
    return {
        "total_pages": len(text_by_page),
        "total_chars": total_chars,
        "section_chars": section_chars,
        "subsection_headings": subsection_headings,
        "top_level_sections": _compute_top_level_sections(text_by_page),  # NEW
        "num_tables": num_tables,
        "num_figures": num_figures,
        "num_equations": num_equations,
    }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_registry.py::test_compute_paper_profile_top_level_sections -v
```

Expected: PASS.

- [ ] **Step 5: Verify against real data**

```bash
python -c "
import json
from deepaper.registry import compute_paper_profile
pp = json.load(open('.deepaper/runs/2512.13961/paper_profile.json'))
tbp_raw = json.load(open('.deepaper/runs/2512.13961/text_by_page.json'))
tbp = {int(k): v for k, v in tbp_raw.items()}
reg = json.load(open('.deepaper/runs/2512.13961/visual_registry.json'))
profile = compute_paper_profile(tbp, reg)
for s in profile['top_level_sections']:
    print(f\"{s['title']:20s} pages {s['page_start']:3d}-{s['page_end']:3d}\")
"
```

Expected: 5-7 sections with non-overlapping page ranges covering pages 1-117.

- [ ] **Step 6: Run full test suite**

```bash
pytest tests/test_registry.py -v
```

Expected: all tests pass (no regressions from adding new field).

- [ ] **Step 7: Commit**

```bash
git add src/deepaper/registry.py tests/test_registry.py
git commit -m "feat(registry): add top_level_sections with page ranges to paper_profile"
```

---

### Task 2: Add `extract_core_figure_images()` to extractor

**Files:**
- Modify: `src/deepaper/extractor.py` (add function at module level)
- Modify: `src/deepaper/cli.py` (wire into `extract` command)

No bbox exists in `core_figures.json`, so we render whole pages via `pdftoppm`.

- [ ] **Step 1: Write failing test**

Create `tests/test_figure_extraction.py`:

```python
"""Tests for core figure image extraction."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest


def _pdftoppm_available() -> bool:
    try:
        subprocess.run(["pdftoppm", "-v"], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False


@pytest.mark.skipif(not _pdftoppm_available(), reason="pdftoppm not installed")
def test_extract_core_figure_images_creates_pngs(tmp_path):
    """extract_core_figure_images should create one PNG per core figure."""
    from deepaper.extractor import extract_core_figure_images

    # Use real OLMo 3 fixtures if available
    fixture_pdf = Path("tmp/2512.13961.pdf")
    if not fixture_pdf.exists():
        pytest.skip("OLMo 3 PDF not available")

    core_figures = [
        {"key": "Figure_1", "id": 1, "page": 3},
        {"key": "Figure_2", "id": 2, "page": 4},
    ]

    output_dir = tmp_path / "figures"
    result = extract_core_figure_images(
        pdf_path=str(fixture_pdf),
        core_figures=core_figures,
        output_dir=str(output_dir),
    )

    assert result["extracted"] == 2
    assert (output_dir / "figure-1.png").exists()
    assert (output_dir / "figure-2.png").exists()
    # Each file should be non-empty and under 500KB
    for fig in core_figures:
        fpath = output_dir / f"figure-{fig['id']}.png"
        size = fpath.stat().st_size
        assert size > 1000, f"{fpath.name} too small: {size} bytes"
        assert size < 512_000, f"{fpath.name} too large: {size} bytes"


def test_extract_core_figure_images_no_pdftoppm(tmp_path):
    """Should return gracefully when pdftoppm is missing."""
    from deepaper.extractor import extract_core_figure_images

    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = extract_core_figure_images(
            pdf_path="dummy.pdf",
            core_figures=[{"key": "Figure_1", "id": 1, "page": 1}],
            output_dir=str(tmp_path / "figures"),
        )
    assert result["extracted"] == 0
    assert "warning" in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_figure_extraction.py -v
```

Expected: FAIL — `extract_core_figure_images` not found in `deepaper.extractor`.

- [ ] **Step 3: Implement `extract_core_figure_images()`**

Add to `src/deepaper/extractor.py` (at the end of the file):

```python
# ===========================================================================
# Core figure image extraction (v2.1)
# ===========================================================================

def extract_core_figure_images(
    pdf_path: str,
    core_figures: list[dict],
    output_dir: str,
) -> dict:
    """Render PDF pages containing core figures as PNG images.

    Uses pdftoppm to rasterize whole pages at 150 DPI. Falls back
    gracefully if pdftoppm is unavailable.

    Returns {extracted: int, files: list[str], warning: str | None}.
    """
    import subprocess
    from pathlib import Path

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    extracted = 0
    files: list[str] = []

    for fig in core_figures:
        fig_id = fig.get("id", "")
        page = fig.get("page")
        if not page:
            continue

        output_prefix = str(out / f"_tmp_fig{fig_id}")
        output_file = out / f"figure-{fig_id}.png"

        try:
            subprocess.run(
                [
                    "pdftoppm",
                    "-f", str(page),
                    "-l", str(page),
                    "-r", "150",
                    "-png",
                    "-singlefile",
                    pdf_path,
                    output_prefix,
                ],
                capture_output=True,
                check=True,
                timeout=30,
            )
        except FileNotFoundError:
            return {
                "extracted": extracted,
                "files": files,
                "warning": "pdftoppm not found; install poppler-utils",
            }
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            # Log and continue with remaining figures
            continue

        # pdftoppm with -singlefile outputs <prefix>.png
        rendered = Path(f"{output_prefix}.png")
        if rendered.exists():
            rendered.rename(output_file)
            files.append(str(output_file))
            extracted += 1

    return {"extracted": extracted, "files": files, "warning": None}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_figure_extraction.py -v
```

Expected: both tests PASS (one may skip if no PDF available).

- [ ] **Step 5: Wire into CLI extract command**

In `src/deepaper/cli.py`, in the `extract` function after `safe_write_json(str(run_dir / "core_tables.json"), core_tables)` (around line 437), add:

```python
    # v2.1: extract core figure images
    from deepaper.extractor import extract_core_figure_images
    figures_dir = run_dir / "figures"
    fig_result = extract_core_figure_images(
        pdf_path=str(pdf_path),
        core_figures=core_figs,
        output_dir=str(figures_dir),
    )
    if fig_result.get("warning"):
        typer.echo(f"Warning: {fig_result['warning']}", err=True)
```

Add `"figures_extracted": fig_result["extracted"]` to the JSON output dict at the end of the function.

- [ ] **Step 6: Run full test suite**

```bash
pytest tests/ -v --timeout=30
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/deepaper/extractor.py src/deepaper/cli.py tests/test_figure_extraction.py
git commit -m "feat(extractor): extract core figure pages as PNG images via pdftoppm"
```

---

### Task 3: Add H11 `check_core_figures_embedded` gate

**Files:**
- Modify: `src/deepaper/gates.py`
- Create: `tests/test_h11_figure_embed.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_h11_figure_embed.py`:

```python
"""Tests for H11: core figure image embedding gate."""
from __future__ import annotations

from deepaper.gates import check_core_figures_embedded


def _core_figs():
    return [
        {"key": "Figure_1", "id": 1, "page": 3},
        {"key": "Figure_2", "id": 2, "page": 4},
    ]


def test_h11_all_embedded():
    md = """\
---
title: test
---
#### 技术精要
![Figure 1 — pipeline](./assets/figure-1.png)
Some text about the pipeline.
![Figure 2 — model flow](./assets/figure-2.png)
"""
    result = check_core_figures_embedded(md, _core_figs())
    assert result["passed"] is True
    assert result["missing"] == []


def test_h11_one_missing():
    md = """\
---
title: test
---
#### 技术精要
![Figure 1 — pipeline](./assets/figure-1.png)
Text mentions Figure 2 but only as text, not image syntax.
"""
    result = check_core_figures_embedded(md, _core_figs())
    assert result["passed"] is False
    assert "Figure_2" in result["missing"]


def test_h11_text_ref_not_enough():
    """Bare text 'Figure 2' should NOT satisfy H11 (that's H7's job)."""
    md = "Figure 2 shows the model flow."
    result = check_core_figures_embedded(md, _core_figs())
    assert result["passed"] is False
    assert len(result["missing"]) == 2


def test_h11_empty_core_figures():
    result = check_core_figures_embedded("some text", [])
    assert result["passed"] is True


def test_h11_subpanel_id():
    """Figure IDs like '13a' should work."""
    md = "![Figure 13a — RULER](./assets/figure-13a.png)"
    figs = [{"key": "Figure_13a", "id": "13a", "page": 34}]
    result = check_core_figures_embedded(md, figs)
    assert result["passed"] is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_h11_figure_embed.py -v
```

Expected: FAIL — `check_core_figures_embedded` not importable.

- [ ] **Step 3: Implement H11**

Add to `src/deepaper/gates.py` before the orchestrator section:

```python
# ===========================================================================
# H11: Core Figures Embedded (image syntax)
# ===========================================================================

def check_core_figures_embedded(md: str, core_figures: list[dict]) -> dict:
    """Check every core figure is embedded with image syntax.

    Requires ``![...](./assets/figure-<id>.png)`` — bare text references
    like ``Figure N`` do NOT satisfy this gate (that's H7's job).

    Returns ``{passed, missing}``.
    """
    if not core_figures:
        return {"passed": True, "missing": []}

    body = _extract_body(md)
    missing: list[str] = []

    for fig in core_figures:
        fig_id = fig.get("id", "")
        key = fig.get("key", f"Figure_{fig_id}")
        # Match ![any alt text](./assets/figure-<id>.png)
        pattern = re.compile(
            rf"!\[.*?\]\(\./assets/figure-{re.escape(str(fig_id))}\.png\)"
        )
        if not pattern.search(body):
            missing.append(key)

    return {"passed": len(missing) == 0, "missing": missing}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_h11_figure_embed.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Wire H11 into `run_hard_gates()`**

In `src/deepaper/gates.py`, in `run_hard_gates()`, after the H10 block add:

```python
    # H11: Core Figures Embedded (image syntax) — v2.1
    if core_figures:
        results["H11"] = check_core_figures_embedded(merged_md, core_figures)
    else:
        results["H11"] = dict(_SKIPPED)
```

- [ ] **Step 6: Run full gates tests**

```bash
pytest tests/test_gates.py tests/test_gates_integration.py tests/test_h11_figure_embed.py -v
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add src/deepaper/gates.py tests/test_h11_figure_embed.py
git commit -m "feat(gates): add H11 core figure image embed gate"
```

---

### Task 4: Add H12 section-bucket coverage + skip H2

**Files:**
- Modify: `src/deepaper/gates.py`
- Modify: `src/deepaper/output_schema.py`
- Modify: `src/deepaper/cli.py` (pass `paper_profile` to `run_hard_gates`)
- Create: `tests/test_h12_section_bucket.py`

- [ ] **Step 1: Add H12 constants to output_schema.py**

In `src/deepaper/output_schema.py`, add:

```python
# H12: Section-bucket coverage — minimum fraction of top-level sections
# that must have at least one page/figure/table reference in the output.
H12_MIN_BUCKET_COVERAGE = 0.8
```

- [ ] **Step 2: Write failing test for H12**

Create `tests/test_h12_section_bucket.py`:

```python
"""Tests for H12: section-bucket coverage gate."""
from __future__ import annotations

from deepaper.gates import check_section_bucket_coverage


def _profile_5_sections():
    """Paper with 5 top-level sections spanning pages 1-50."""
    return {
        "top_level_sections": [
            {"title": "Abstract", "page_start": 1, "page_end": 2},
            {"title": "Introduction", "page_start": 3, "page_end": 10},
            {"title": "Method", "page_start": 11, "page_end": 25},
            {"title": "Experiments", "page_start": 26, "page_end": 40},
            {"title": "Conclusion", "page_start": 41, "page_end": 50},
        ],
    }


def test_h12_full_coverage():
    """All 5 sections referenced → pass."""
    md = "Section 3.2, p.5 ... Table 3, p.15 ... p.30 ... p.45 ... Abstract p.1"
    result = check_section_bucket_coverage(md, _profile_5_sections())
    assert result["passed"] is True


def test_h12_80_percent_coverage():
    """4/5 sections referenced (80%) → pass at threshold."""
    md = "p.1 ... p.5 ... p.15 ... p.30"
    result = check_section_bucket_coverage(md, _profile_5_sections())
    assert result["passed"] is True
    assert result["coverage"] >= 0.8


def test_h12_below_threshold():
    """Only 2/5 sections → fail."""
    md = "p.1 ... p.5"
    result = check_section_bucket_coverage(md, _profile_5_sections())
    assert result["passed"] is False
    assert len(result["uncovered"]) >= 3


def test_h12_no_sections_in_profile():
    """Missing top_level_sections → skip (pass)."""
    result = check_section_bucket_coverage("any text", {})
    assert result["passed"] is True
    assert result.get("skipped") is True


def test_h12_figure_table_refs_count():
    """Figure/Table refs on known pages should satisfy coverage."""
    md = "Figure 5 (p.30)"  # page 30 is in Experiments (26-40)
    profile = _profile_5_sections()
    # Only Experiments bucket should be covered
    result = check_section_bucket_coverage(md, profile)
    covered = [s for s in profile["top_level_sections"]
               if s["title"] not in result.get("uncovered", [])]
    exp_titles = [s["title"] for s in covered]
    assert "Experiments" in exp_titles
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tests/test_h12_section_bucket.py -v
```

Expected: FAIL — `check_section_bucket_coverage` not importable.

- [ ] **Step 4: Implement H12**

Add to `src/deepaper/gates.py`:

```python
from deepaper.output_schema import H12_MIN_BUCKET_COVERAGE

# ===========================================================================
# H12: Section-Bucket Coverage (v2.1, replaces H2)
# ===========================================================================

# Regex to find page references: p.5, p.47, page 5, Page 47
_PAGE_REF_RE = re.compile(r"(?:p\.|page\s+)(\d+)", re.IGNORECASE)


def check_section_bucket_coverage(
    merged: str,
    paper_profile: dict,
) -> dict:
    """Check output references pages from >= 80% of top-level sections.

    For each top-level section (identified by page range), check if the
    output contains any page reference (p.NN) where NN falls in that
    section's page range.

    Returns {passed, coverage, uncovered, total_sections}.
    """
    sections = paper_profile.get("top_level_sections", [])
    if not sections:
        return {"passed": True, "skipped": True, "reason": "no top_level_sections"}

    body = _extract_body(merged)

    # Extract all page numbers referenced in the output
    referenced_pages: set[int] = set()
    for m in _PAGE_REF_RE.finditer(body):
        referenced_pages.add(int(m.group(1)))

    # Check each section bucket
    uncovered: list[str] = []
    for sec in sections:
        page_start = sec["page_start"]
        page_end = sec["page_end"]
        # Does any referenced page fall in this section's range?
        covered = any(page_start <= p <= page_end for p in referenced_pages)
        if not covered:
            uncovered.append(sec["title"])

    total = len(sections)
    covered_count = total - len(uncovered)
    coverage = covered_count / total if total > 0 else 1.0

    return {
        "passed": coverage >= H12_MIN_BUCKET_COVERAGE,
        "coverage": round(coverage, 4),
        "uncovered": uncovered,
        "total_sections": total,
    }
```

- [ ] **Step 5: Run H12 tests**

```bash
pytest tests/test_h12_section_bucket.py -v
```

Expected: all pass.

- [ ] **Step 6: Skip H2 + wire H12 into `run_hard_gates()`**

In `run_hard_gates()` signature, add `paper_profile: dict | None = None`:

```python
def run_hard_gates(
    merged_md: str,
    coverage_checklist: dict,
    core_figures: list[dict],
    text_by_page: dict[int, str] | None,
    registry: dict | None,
    paper_profile: dict | None = None,  # NEW — v2.1
) -> dict:
```

Replace H2 logic:

```python
    # H2: SKIPPED (v2.1 — replaced by H12 section-bucket coverage)
    results["H2"] = dict(_SKIPPED)
```

Add H12 after H11:

```python
    # H12: Section-bucket coverage (v2.1, replaces H2)
    if paper_profile:
        results["H12"] = check_section_bucket_coverage(merged_md, paper_profile)
    else:
        results["H12"] = dict(_SKIPPED)
```

- [ ] **Step 7: Update `cli.py` gates command to pass paper_profile**

In `src/deepaper/cli.py`, in the `gates` function (around line 372), load profile and pass it:

```python
    profile = safe_read_json(str(run_dir / "paper_profile.json"), {})
    # ... existing code ...
    result = run_hard_gates(merged_md, checklist, core_figures, text_by_page, registry_data,
                            paper_profile=profile)
```

- [ ] **Step 8: Update existing H2 tests**

In `tests/test_gates.py`, find any test that asserts `results["H2"]["passed"]` is `True` or `False`. Update to expect `{"passed": True, "skipped": True}`.

If test calls `check_structural_coverage` directly, those tests can remain — the function still exists, it's just un-wired.

- [ ] **Step 9: Run full gates tests**

```bash
pytest tests/test_gates.py tests/test_gates_integration.py tests/test_h11_figure_embed.py tests/test_h12_section_bucket.py -v
```

Expected: all pass.

- [ ] **Step 10: Commit**

```bash
git add src/deepaper/gates.py src/deepaper/output_schema.py src/deepaper/cli.py tests/test_h12_section_bucket.py tests/test_gates.py
git commit -m "feat(gates): add H12 section-bucket coverage, skip H2"
```

---

### Task 5: Update writer prompts (depth + figure embed + compact confusion)

**Files:**
- Modify: `src/deepaper/prompt_builder.py`
- Modify: `src/deepaper/defaults.py` (lines 148-154: confusion point example)
- Modify: `tests/test_prompt_builder.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_prompt_builder.py`:

```python
def test_depth_requirement_in_principle_writer():
    """writer-principle prompt must contain D1/D2/D3 depth requirement."""
    from deepaper.prompt_builder import auto_split, generate_writer_prompt, \
        parse_template_sections, extract_system_role, gates_to_constraints
    from deepaper.defaults import DEFAULT_TEMPLATE

    tasks = auto_split({})
    principle_task = [t for t in tasks if t.name == "writer-principle"][0]

    sections = parse_template_sections(DEFAULT_TEMPLATE)
    constraints = gates_to_constraints(principle_task.sections, {}, {}, [])

    prompt = generate_writer_prompt(
        task=principle_task, run_dir="/tmp/test", template_sections=sections,
        system_role="", figure_contexts={}, constraints=constraints,
        pdf_path="", table_def_pages=[],
    )
    assert "D1. 反事实推理" in prompt or "D1." in prompt
    assert "D2. 怀疑性批判" in prompt or "D2." in prompt


def test_figure_embed_constraint_in_technical_writer():
    """writer-technical prompt must require image syntax for core figures."""
    from deepaper.prompt_builder import auto_split, generate_writer_prompt, \
        parse_template_sections, extract_system_role, gates_to_constraints
    from deepaper.defaults import DEFAULT_TEMPLATE

    tasks = auto_split({})
    tech_task = [t for t in tasks if t.name == "writer-technical"][0]
    core_figs = [{"key": "Figure_1", "id": 1, "page": 3}]

    sections = parse_template_sections(DEFAULT_TEMPLATE)
    constraints = gates_to_constraints(tech_task.sections, {}, {}, core_figs)

    prompt = generate_writer_prompt(
        task=tech_task, run_dir="/tmp/test", template_sections=sections,
        system_role="", figure_contexts={}, constraints=constraints,
        pdf_path="", table_def_pages=[],
    )
    assert "./assets/figure-" in prompt
    assert "H11" in prompt or "图片嵌入" in prompt


def test_figure_embed_not_forced_on_overview_writer():
    """writer-overview should NOT have hard figure embed requirement."""
    from deepaper.prompt_builder import auto_split, gates_to_constraints
    from deepaper.defaults import DEFAULT_TEMPLATE

    tasks = auto_split({})
    overview_task = [t for t in tasks if t.name == "writer-overview"][0]
    core_figs = [{"key": "Figure_1", "id": 1, "page": 3}]

    constraints = gates_to_constraints(overview_task.sections, {}, {}, core_figs)
    # Overview should have soft suggestion, not hard requirement
    assert "所有 core_figures" not in constraints


def test_compact_confusion_format_in_template():
    """DEFAULT_TEMPLATE must use v2.1 compact confusion format (❌/✅/🚨)."""
    from deepaper.defaults import DEFAULT_TEMPLATE
    assert "🚨" in DEFAULT_TEMPLATE
    assert "如果搞错" in DEFAULT_TEMPLATE or "搞错" in DEFAULT_TEMPLATE
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_prompt_builder.py::test_depth_requirement_in_principle_writer tests/test_prompt_builder.py::test_figure_embed_constraint_in_technical_writer tests/test_prompt_builder.py::test_figure_embed_not_forced_on_overview_writer tests/test_prompt_builder.py::test_compact_confusion_format_in_template -v
```

Expected: all FAIL.

- [ ] **Step 3: Add depth requirement block to `gates_to_constraints()`**

In `src/deepaper/prompt_builder.py`, in `gates_to_constraints()`, after the causal chain format block (line ~165), add:

```python
    # --- Depth requirements (v2.1) — only for 第一性原理分析 and 技术精要 ---
    depth_sections = {"第一性原理分析", "技术精要"}
    if depth_sections & set(sections):
        lines.append("\n**深度要求（v2.1，硬性约束）：**")
        lines.append("本章节必须包含以下 3 种深度信号中的至少 2 种：")
        lines.append("- **D1. 反事实推理** — 对至少 1 个核心设计决策，说明"如果不这么做会怎样"")
        lines.append("- **D2. 怀疑性批判** — 对至少 1 个数字/结论，指出 fine print 或度量偏差")
        lines.append("- **D3. 实现层细节** — 对至少 1 个核心机制，写出论文正文外的具体实现参数")
        lines.append("- 禁止教科书式背景知识（不解释 DPO / GRPO 等基本概念）")
```

- [ ] **Step 4: Add figure embed constraints**

In `gates_to_constraints()`, after depth requirements, add:

```python
    # --- Figure embed constraints (v2.1) ---
    if core_figures:
        fig_ids_str = ", ".join(f"figure-{cf['id']}" for cf in core_figures)
        if "技术精要" in sections:
            # Hard requirement for writer-technical
            lines.append("\n**图片嵌入约束（v2.1，H11 gate 验证）：**")
            lines.append(f"你负责嵌入所有 core figure: {fig_ids_str}")
            lines.append("每个 figure 用图片语法 `![Figure N — 简短caption](./assets/figure-N.png)` 至少嵌入 1 次")
            lines.append("裸文本引用 `Figure N 展示了...` 不算嵌入")
        else:
            # Soft suggestion for other writers
            lines.append("\n**图片嵌入建议（可选）：**")
            lines.append("如需引用 core figure 作证据，可用 `![Figure N — ...](./assets/figure-N.png)` 嵌入")
```

- [ ] **Step 5: Update confusion-point example in `defaults.py`**

In `src/deepaper/defaults.py`, replace lines 148-154:

Old:
```
##### 易混淆点

≤ 3 对，每对 2 行：

- ❌ 错误理解：...
- ✅ 正确理解：...
```

New:
```
##### 易混淆点

≤ 3 条，每条紧凑 3 行（≤100 个汉字/条，不含标题和嵌图）：

**混淆点 N：一句话 label**

- ❌ 常见错误理解
- ✅ 正确理解（必须解释差异的动因）
- 🚨 如果搞错：落地后果
  可选嵌入 figure 作证据：`![Figure N — caption](./assets/figure-N.png)`
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_prompt_builder.py -v
```

Expected: all pass (including the 4 new ones).

- [ ] **Step 7: Sync templates/default.md**

```bash
cp src/deepaper/defaults.py /dev/null  # the sync target depends on project convention
```

Check if `templates/default.md` needs to match `DEFAULT_TEMPLATE`. If so, read `src/deepaper/templates.py` to find the sync mechanism, and run it. (Previous commit `04d7dea` synced these; follow the same approach.)

- [ ] **Step 8: Commit**

```bash
git add src/deepaper/prompt_builder.py src/deepaper/defaults.py tests/test_prompt_builder.py
git commit -m "feat(prompts): add v2.1 depth requirements, figure embed constraints, compact confusion format"
```

---

### Task 6: Update save command for P2 directory layout

**Files:**
- Modify: `src/deepaper/writer.py` (`write_paper_note` function)
- Modify: `src/deepaper/cli.py` (`save` command)
- Modify: `tests/test_writer.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_writer.py`:

```python
def test_write_paper_note_p2_layout(tmp_path):
    """save should create P2 directory: <slug>/<slug>.md + assets/."""
    from deepaper.writer import write_paper_note

    analysis_fm = {
        "title": "Test Paper",
        "arxiv_id": "2512.99999",
        "tldr": "Test TL;DR with 3.5 and 99.2 numbers.",
        "tags": ["test"],
    }
    analysis_body = "#### 核心速览\nTest content."
    metadata = {"title": "Test Paper", "arxiv_id": "2512.99999"}
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()

    note_path = write_paper_note(
        analysis_fm, analysis_body, metadata, ["test"],
        papers_dir, force=True, category="test",
    )

    # v2.1: output should be inside a slug directory
    assert note_path.parent.name == "test-paper" or note_path.parent != papers_dir / "test"
    assert note_path.exists()
    assert note_path.suffix == ".md"
```

- [ ] **Step 2: Understand current `write_paper_note`**

Read `src/deepaper/writer.py` to find the `write_paper_note` function. Understand how it constructs the output path. The change is:

Old: `papers_dir / category / f"{slug}.md"`
New: `papers_dir / category / slug / f"{slug}.md"`

- [ ] **Step 3: Implement P2 layout in `write_paper_note`**

Modify the path construction in `write_paper_note`:

```python
    # v2.1: P2 layout — each paper gets its own directory
    paper_dir = category_dir / slug
    paper_dir.mkdir(parents=True, exist_ok=True)
    note_path = paper_dir / f"{slug}.md"
```

- [ ] **Step 4: Add figure copy logic to CLI `save` command**

In `src/deepaper/cli.py`, in the `save` function, after `note_path = write_paper_note(...)`, add:

```python
    # v2.1: copy extracted figure images to paper assets directory
    from deepaper.pipeline_io import safe_read_json, ensure_run_dir
    run_dir = ensure_run_dir(root, real_id)
    figures_src = run_dir / "figures"
    if figures_src.exists():
        assets_dir = note_path.parent / "assets"
        assets_dir.mkdir(exist_ok=True)
        import shutil
        for png in figures_src.glob("*.png"):
            shutil.copy2(png, assets_dir / png.name)
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_writer.py tests/test_cli.py -v
```

Expected: all pass. Some existing tests may need path adjustments if they assert flat layout — update them.

- [ ] **Step 6: Commit**

```bash
git add src/deepaper/writer.py src/deepaper/cli.py tests/test_writer.py
git commit -m "feat(save): P2 directory layout with figure asset copy"
```

---

### Task 7: Golden regression test + arxiv_id test

**Files:**
- Create: `tests/test_golden_regression.py`
- Create: `tests/test_frontmatter.py`

- [ ] **Step 1: Write golden regression test**

Create `tests/test_golden_regression.py`:

```python
"""Golden reference regression test.

Compares structural metrics between golden (frozen v2 output) and current
papers/ output. Does NOT check exact wording — only structural indicators.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

GOLDEN = Path("tests/golden/olmo-3.md")
# v2.1 P2 layout; fall back to v2 flat layout
CURRENT_P2 = Path("papers/llm/pretraining/olmo-3/olmo-3.md")
CURRENT_FLAT = Path("papers/llm/pretraining/olmo-3.md")


def _current_path() -> Path:
    if CURRENT_P2.exists():
        return CURRENT_P2
    return CURRENT_FLAT


def _parse(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    fm = yaml.safe_load(text[3:end]) or {}
    body = text[end + 3:]
    return fm, body


def _count_table_rows(body: str) -> int:
    return sum(1 for line in body.split("\n")
               if line.strip().startswith("|") and line.strip().endswith("|")
               and "---" not in line)


def _count_causal_chains(body: str) -> int:
    return len(re.findall(r"\[C\d+\]", body))


def _count_confusion_points(body: str) -> int:
    return len(re.findall(r"[❌]", body))


def _count_page_refs(body: str) -> int:
    return len(re.findall(r"(?:p\.|page\s+)\d+", body, re.IGNORECASE))


@pytest.mark.skipif(not GOLDEN.exists(), reason="golden not frozen yet")
class TestGoldenRegression:
    def setup_method(self):
        self.golden_fm, self.golden_body = _parse(GOLDEN)
        current = _current_path()
        if not current.exists():
            pytest.skip("current output not yet generated")
        self.current_fm, self.current_body = _parse(current)

    def test_causal_chains_not_fewer(self):
        golden_count = _count_causal_chains(self.golden_body)
        current_count = _count_causal_chains(self.current_body)
        assert current_count >= golden_count, \
            f"Causal chains regressed: {current_count} < {golden_count}"

    def test_confusion_points_not_fewer(self):
        golden_count = _count_confusion_points(self.golden_body)
        current_count = _count_confusion_points(self.current_body)
        assert current_count >= golden_count, \
            f"Confusion points regressed: {current_count} < {golden_count}"

    def test_table_rows_not_fewer(self):
        golden_count = _count_table_rows(self.golden_body)
        current_count = _count_table_rows(self.current_body)
        assert current_count >= golden_count, \
            f"Table rows regressed: {current_count} < {golden_count}"

    def test_page_refs_not_fewer(self):
        golden_count = _count_page_refs(self.golden_body)
        current_count = _count_page_refs(self.current_body)
        assert current_count >= golden_count, \
            f"Page refs regressed: {current_count} < {golden_count}"

    def test_arxiv_id_preserved(self):
        assert self.current_fm.get("arxiv_id"), "arxiv_id missing from current output"
```

- [ ] **Step 2: Write frontmatter test**

Create `tests/test_frontmatter.py`:

```python
"""Tests for frontmatter field preservation."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

PAPERS_DIR = Path("papers")


def _find_paper_mds():
    """Find all paper .md files in the papers directory."""
    if not PAPERS_DIR.exists():
        return []
    # v2.1 P2 layout: papers/cat/slug/slug.md
    # v2 flat layout: papers/cat/slug.md
    results = []
    for md in PAPERS_DIR.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        if text.startswith("---"):
            results.append(md)
    return results


@pytest.mark.skipif(not PAPERS_DIR.exists(), reason="no papers dir")
def test_all_papers_have_arxiv_id():
    """Every paper markdown must have arxiv_id in frontmatter."""
    papers = _find_paper_mds()
    if not papers:
        pytest.skip("no papers found")
    missing = []
    for p in papers:
        text = p.read_text(encoding="utf-8")
        end = text.find("---", 3)
        if end < 0:
            continue
        fm = yaml.safe_load(text[3:end]) or {}
        if not fm.get("arxiv_id"):
            missing.append(str(p))
    assert not missing, f"Papers missing arxiv_id: {missing}"
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_golden_regression.py tests/test_frontmatter.py -v
```

Expected: golden regression tests pass (comparing golden to itself). Frontmatter test passes if current papers have arxiv_id.

- [ ] **Step 4: Commit**

```bash
git add tests/test_golden_regression.py tests/test_frontmatter.py
git commit -m "test: add golden regression and frontmatter preservation tests"
```

---

### Task 8: Run full test suite + fix regressions

**Files:**
- Any files that need fixes from test failures

- [ ] **Step 1: Run full pytest**

```bash
pytest tests/ -v --tb=short 2>&1 | tail -40
```

Expected: all tests pass. If any fail, fix them.

- [ ] **Step 2: Common failure patterns to watch for**

1. **Existing tests that check `results["H2"]["passed"]`** — update to expect `skipped: True`
2. **Existing tests that assert flat save path** (`papers/cat/slug.md`) — update for P2 path
3. **Tests that count gates** (e.g., `len(result["failed"])`) — H11/H12 are new, may change counts
4. **Import errors** — ensure all new functions are properly exported

- [ ] **Step 3: Fix and re-run until green**

```bash
pytest tests/ -v
```

Expected: 100% pass.

- [ ] **Step 4: Commit fixes if any**

```bash
git add -u
git commit -m "fix: resolve test regressions from v2.1 gate and layout changes"
```

---

### Task 9: End-to-end validation

**Files:** None (this is a manual validation task).

- [ ] **Step 1: Re-run extract on OLMo 3 to generate figure PNGs**

```bash
cd /Users/bytedance/github/deepaper
deepaper extract 2512.13961
```

Verify: `.deepaper/runs/2512.13961/figures/figure-1.png` and `figure-2.png` exist.

- [ ] **Step 2: Verify top_level_sections in profile**

```bash
python -c "
import json
p = json.load(open('.deepaper/runs/2512.13961/paper_profile.json'))
for s in p.get('top_level_sections', []):
    print(f\"{s['title']:20s} pages {s['page_start']:3d}-{s['page_end']:3d}\")
"
```

- [ ] **Step 3: Re-run gates on existing merged.md**

```bash
deepaper gates 2512.13961
```

Expected: H1-H10 pass (same as before). H11 will FAIL (current merged.md has no image embeds). H12 should pass or fail depending on page ref distribution. H2 should show SKIPPED.

- [ ] **Step 4: Re-run full pipeline with v2.1 writers**

Run the full `/deepaper https://arxiv.org/abs/2512.13961` pipeline with new prompts. This produces a new `merged.md` → `merged_fixed.md` → save to `papers/llm/pretraining/olmo-3/olmo-3.md`.

- [ ] **Step 5: Verify P2 output structure**

```bash
ls -la papers/llm/pretraining/olmo-3/
```

Expected:
```
olmo-3.md
assets/
  figure-1.png
  figure-2.png
```

- [ ] **Step 6: Run gates on new output**

```bash
deepaper gates 2512.13961
```

Expected: all gates H1-H12 pass (except H4 which is permanently SKIPPED).

- [ ] **Step 7: Open in Obsidian**

Open `papers/llm/pretraining/olmo-3/olmo-3.md` in Obsidian. Verify:
- Figure 1 and Figure 2 render inline
- Confusion points use ❌/✅/🚨 format
- Depth signals (反事实/怀疑/实现细节) present in 第一性原理分析 and 技术精要

- [ ] **Step 8: Run golden regression**

```bash
pytest tests/test_golden_regression.py -v
```

Expected: all pass (structural metrics should not regress; they should improve with depth additions).

- [ ] **Step 9: Final full test suite**

```bash
pytest tests/ -v
```

Expected: 100% green.

- [ ] **Step 10: Commit any final adjustments**

```bash
git add -A
git commit -m "chore: v2.1 end-to-end validation complete"
```
