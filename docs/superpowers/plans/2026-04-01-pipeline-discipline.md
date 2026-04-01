# Pipeline Discipline Enhancement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add programmatic quality gates, structural validation, and disciplined retry logic to the deepaper multi-agent pipeline, reducing token consumption ~50% while improving analysis completeness.

**Architecture:** New Python modules (`registry.py`, `gates.py`, `extractor.py`) provide programmatic validation. The slash command (`deepaper.md`) is rewritten to orchestrate the enhanced pipeline. `writer.py` gains quality metadata fields. All intermediate artifacts are stored in `.deepaper/runs/{ARXIV_ID}/`.

**Tech Stack:** Python 3.10+, PyMuPDF (fitz), typer, pyyaml, re (regex), pathlib

**Spec:** `docs/superpowers/specs/2026-04-01-pipeline-discipline-design.md`

---

## File Structure

### New files

| File | Responsibility |
|------|---------------|
| `src/deepaper/registry.py` | `build_visual_registry()`, `identify_core_figures()`, `extract_figure_contexts()`, `compute_paper_profile()`, `build_coverage_checklist()` |
| `src/deepaper/gates.py` | `run_hard_gates()`, individual gate checks (H1-H8), `extract_number_fingerprint()`, `verify_writer_numbers()` |
| `src/deepaper/extractor.py` | `struct_check()`, `audit_coverage()`, `parse_notes_sections()` |
| `src/deepaper/pipeline_io.py` | `safe_write_json()`, `safe_read_json()`, `ensure_run_dir()`, `write_report()` |
| `tests/test_registry.py` | Tests for registry, core figures, figure contexts, paper profile |
| `tests/test_gates.py` | Tests for all 8 HardGates |
| `tests/test_extractor_checks.py` | Tests for StructCheck + Auditor |
| `tests/test_pipeline_io.py` | Tests for JSON safety layer |

### Modified files

| File | Changes |
|------|---------|
| `src/deepaper/writer.py` | `write_paper_note()` accepts `quality`, `failed_gates`, `pipeline_version` |
| `src/deepaper/cli.py` | New subcommands: `registry`, `gates`, `profile`, `report` |
| `src/deepaper/__init__.py` | Bump version |
| `.gitignore` | Add `.deepaper/` |
| `.claude/commands/deepaper.md` | Full rewrite: new pipeline orchestration |
| `pyproject.toml` | Add `pymupdf` dependency |

---

## Task 1: JSON Safety Layer (`pipeline_io.py`)

**Files:**
- Create: `src/deepaper/pipeline_io.py`
- Create: `tests/test_pipeline_io.py`

- [ ] **Step 1: Write failing tests for safe_write_json**

```python
# tests/test_pipeline_io.py
"""Tests for pipeline I/O safety layer."""
import json
from pathlib import Path

import pytest


def test_safe_write_json_creates_file(tmp_path):
    from deepaper.pipeline_io import safe_write_json

    path = tmp_path / "test.json"
    result = safe_write_json(str(path), {"key": "value"})
    assert result is True
    assert path.exists()
    data = json.loads(path.read_text())
    assert data == {"key": "value"}


def test_safe_write_json_creates_parent_dirs(tmp_path):
    from deepaper.pipeline_io import safe_write_json

    path = tmp_path / "nested" / "dir" / "test.json"
    result = safe_write_json(str(path), {"nested": True})
    assert result is True
    assert path.exists()


def test_safe_write_json_returns_false_on_failure():
    from deepaper.pipeline_io import safe_write_json

    result = safe_write_json("/nonexistent/readonly/test.json", {"fail": True})
    assert result is False


def test_safe_write_json_atomic_no_partial(tmp_path):
    """If write fails mid-way, no .tmp file is left behind."""
    from deepaper.pipeline_io import safe_write_json

    path = tmp_path / "test.json"
    # First write succeeds
    safe_write_json(str(path), {"first": True})
    original = path.read_text()
    # Simulate a failure scenario — read-only dir won't apply here,
    # but we verify .tmp is cleaned up on success
    tmp_file = path.with_suffix(".tmp")
    assert not tmp_file.exists()


def test_safe_read_json_reads_valid(tmp_path):
    from deepaper.pipeline_io import safe_read_json

    path = tmp_path / "test.json"
    path.write_text('{"key": "value"}')
    result = safe_read_json(str(path))
    assert result == {"key": "value"}


def test_safe_read_json_returns_default_on_missing():
    from deepaper.pipeline_io import safe_read_json

    result = safe_read_json("/nonexistent/file.json", default={"fallback": True})
    assert result == {"fallback": True}


def test_safe_read_json_returns_default_on_corrupt(tmp_path):
    from deepaper.pipeline_io import safe_read_json

    path = tmp_path / "bad.json"
    path.write_text("{broken json content")
    result = safe_read_json(str(path), default=None)
    assert result is None


def test_safe_read_json_returns_default_on_empty(tmp_path):
    from deepaper.pipeline_io import safe_read_json

    path = tmp_path / "empty.json"
    path.write_text("")
    result = safe_read_json(str(path), default={})
    assert result == {}


def test_ensure_run_dir_creates_structure(tmp_path):
    from deepaper.pipeline_io import ensure_run_dir

    run_dir = ensure_run_dir(tmp_path, "2401.12345")
    assert run_dir.exists()
    assert run_dir == tmp_path / ".deepaper" / "runs" / "2401.12345"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_pipeline_io.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'deepaper.pipeline_io'`

- [ ] **Step 3: Implement pipeline_io.py**

```python
# src/deepaper/pipeline_io.py
"""Safe JSON I/O and run directory management for the pipeline."""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger("deepaper")


def safe_write_json(path: str, data: dict) -> bool:
    """Atomic JSON write. Returns True on success, False on failure."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        tmp.rename(p)
        return True
    except Exception as e:
        logger.warning("JSON write failed: %s: %s", path, e)
        # Clean up partial .tmp if it exists
        try:
            Path(path).with_suffix(".tmp").unlink(missing_ok=True)
        except Exception:
            pass
        return False


def safe_read_json(path: str, default=None):
    """Read JSON file. Returns default on any failure."""
    try:
        text = Path(path).read_text(encoding="utf-8")
        if not text.strip():
            return default
        return json.loads(text)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.warning("JSON read failed: %s: %s", path, e)
        return default


def ensure_run_dir(project_root: Path, arxiv_id: str) -> Path:
    """Create and return .deepaper/runs/{arxiv_id}/ directory."""
    run_dir = project_root / ".deepaper" / "runs" / arxiv_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_pipeline_io.py -v`
Expected: All 9 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/pipeline_io.py tests/test_pipeline_io.py
git commit -m "feat: add safe JSON I/O layer for pipeline artifacts"
```

---

## Task 2: Visual Registry (`registry.py` — Part 1)

**Files:**
- Create: `src/deepaper/registry.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: Write failing tests for build_visual_registry**

```python
# tests/test_registry.py
"""Tests for visual registry, core figure detection, and paper profile."""
import pytest


class TestBuildVisualRegistry:
    def test_detects_tables_and_figures(self):
        from deepaper.registry import build_visual_registry

        text_by_page = {
            1: "Introduction. As shown in Figure 1, our method...",
            2: "Figure 1: Overview of the architecture.\nWe propose a new approach.",
            3: "Table 1: Main results on benchmarks.\n| Model | Acc |\n| A | 95.2 |",
            4: "As shown in Table 1 and Figure 1, our approach outperforms...",
            5: "Table 2: Ablation results.\n| Config | Score |\n| Base | 80.1 |",
        }
        registry = build_visual_registry(text_by_page)

        assert "Table_1" in registry
        assert "Table_2" in registry
        assert "Figure_1" in registry
        assert registry["Table_1"]["definition_page"] == 3
        assert registry["Figure_1"]["definition_page"] == 2
        assert registry["Table_1"]["has_caption"] is True

    def test_detects_fig_dot_notation(self):
        from deepaper.registry import build_visual_registry

        text_by_page = {
            1: "As shown in Fig. 3, the model converges.",
            2: "Fig. 3. Training loss over epochs.",
        }
        registry = build_visual_registry(text_by_page)
        assert "Figure_3" in registry
        assert registry["Figure_3"]["definition_page"] == 2

    def test_reference_without_caption(self):
        from deepaper.registry import build_visual_registry

        text_by_page = {
            1: "See Table 5 for details.",
        }
        registry = build_visual_registry(text_by_page)
        assert "Table_5" in registry
        assert registry["Table_5"]["has_caption"] is False

    def test_empty_text_returns_empty_registry(self):
        from deepaper.registry import build_visual_registry

        registry = build_visual_registry({})
        assert registry == {}

    def test_numbering_gap_detection(self):
        from deepaper.registry import verify_registry_completeness

        registry = {
            "Table_1": {"type": "Table", "id": "1", "has_caption": True},
            "Table_3": {"type": "Table", "id": "3", "has_caption": True},
        }
        issues = verify_registry_completeness(registry)
        assert any("Table 2" in issue for issue in issues)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_registry.py::TestBuildVisualRegistry -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement build_visual_registry and verify_registry_completeness**

```python
# src/deepaper/registry.py
"""Visual registry: table/figure detection, core figure identification, paper profiling."""
from __future__ import annotations

import re
from collections import defaultdict


def build_visual_registry(text_by_page: dict[int, str]) -> dict:
    """Build a registry of all Tables and Figures from extracted text.

    Scans each page for Table/Figure/Fig. references and captions.
    Returns a dict keyed by "Table_N" or "Figure_N".
    """
    registry: dict[str, dict] = {}

    for page_no, text in text_by_page.items():
        # Match: Table N, Figure N, Fig. N, Fig N
        for match in re.finditer(
            r"(Table|Figure|Fig)\s*\.?\s*(\d+)", text, re.IGNORECASE
        ):
            raw_type = match.group(1)
            fig_id = match.group(2)
            # Normalize "Fig" / "Fig." to "Figure"
            norm_type = "Figure" if raw_type.lower().startswith("fig") else "Table"
            key = f"{norm_type}_{fig_id}"

            if key not in registry:
                registry[key] = {
                    "type": norm_type,
                    "id": fig_id,
                    "pages": [],
                    "definition_page": None,
                    "has_caption": False,
                }

            if page_no not in registry[key]["pages"]:
                registry[key]["pages"].append(page_no)

        # Detect captions: "Table N:" or "Table N." or "Figure N:" at line start
        for match in re.finditer(
            r"(?:^|\n)\s*(?:Table|Figure|Fig)\s*\.?\s*(\d+)\s*[:.：。]",
            text,
            re.IGNORECASE,
        ):
            fig_id = match.group(1)
            # Determine type from the match text
            match_text = match.group(0).strip()
            norm_type = (
                "Figure"
                if re.match(r"(?:Figure|Fig)", match_text, re.IGNORECASE)
                else "Table"
            )
            key = f"{norm_type}_{fig_id}"
            if key in registry:
                registry[key]["has_caption"] = True
                registry[key]["definition_page"] = page_no

    return registry


def verify_registry_completeness(registry: dict) -> list[str]:
    """Check for numbering gaps and missing captions."""
    issues = []

    for item_type in ["Table", "Figure"]:
        ids = sorted(
            int(v["id"])
            for v in registry.values()
            if v["type"] == item_type
        )
        if not ids:
            continue
        for i in range(1, max(ids) + 1):
            if i not in ids:
                issues.append(f"Missing {item_type} {i} (gap in numbering)")

        for key, val in registry.items():
            if val["type"] == item_type and not val["has_caption"]:
                issues.append(
                    f"{key}: referenced but no caption found"
                )

    return issues
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_registry.py::TestBuildVisualRegistry -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/registry.py tests/test_registry.py
git commit -m "feat: add visual registry for table/figure detection"
```

---

## Task 3: Core Figure Identification (`registry.py` — Part 2)

**Files:**
- Modify: `src/deepaper/registry.py`
- Modify: `tests/test_registry.py`

- [ ] **Step 1: Write failing tests for identify_core_figures and extract_figure_contexts**

Append to `tests/test_registry.py`:

```python
class TestCoreFigures:
    def _make_text_by_page(self):
        """Paper with 10 pages. Figure 1 is clearly the 'soul figure'."""
        text = {}
        text[1] = (
            "Abstract. We propose FooNet. As shown in Figure 1, "
            "our architecture uses a novel routing mechanism."
        )
        text[2] = (
            "Figure 1: Overview of the FooNet architecture showing "
            "the multi-head routing module and load balancer. "
            "The key insight is decoupling expert selection from capacity."
        )
        text[3] = (
            "As illustrated in Figure 1, the routing module distributes tokens. "
            "Figure 2 shows the training loss."
        )
        text[4] = "Figure 2: Training loss curves.\nThe model converges in 10K steps."
        text[5] = "We compare with baselines in Table 1. See also Figure 1 for context."
        text[6] = "Table 1: Main results.\n| Model | Acc |\n| Ours | 95.2 |"
        text[7] = "Additional results in Table 2 and Figure 3."
        text[8] = "Table 2: Ablation study.\n| Config | Score |"
        text[9] = "Figure 3: Attention visualization.\nAppendix details."
        text[10] = "Figure 4: Additional ablation charts."
        return text

    def test_identifies_core_figure(self):
        from deepaper.registry import build_visual_registry, identify_core_figures

        text = self._make_text_by_page()
        registry = build_visual_registry(text)
        cores = identify_core_figures(registry, text, total_pages=10)

        # Figure 1 should be identified as core (high ref count, in intro, early page)
        core_ids = [c["id"] for c in cores]
        assert "1" in core_ids

    def test_max_core_budget(self):
        from deepaper.registry import build_visual_registry, identify_core_figures

        text = self._make_text_by_page()
        registry = build_visual_registry(text)
        cores = identify_core_figures(registry, text, total_pages=10)

        # MAX_CORE = 3, and 20% of 4 figures = 0.8 → max(1, 0) = 1
        assert len(cores) <= 3

    def test_no_core_when_no_figures(self):
        from deepaper.registry import identify_core_figures

        cores = identify_core_figures({}, {}, total_pages=5)
        assert cores == []

    def test_extract_figure_contexts(self):
        from deepaper.registry import (
            build_visual_registry,
            identify_core_figures,
            extract_figure_contexts,
        )

        text = self._make_text_by_page()
        registry = build_visual_registry(text)
        cores = identify_core_figures(registry, text, total_pages=10)
        contexts = extract_figure_contexts(text, cores)

        assert "Figure_1" in contexts
        assert contexts["Figure_1"]["caption"]  # non-empty
        assert len(contexts["Figure_1"]["references"]) >= 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_registry.py::TestCoreFigures -v`
Expected: FAIL — `ImportError` for `identify_core_figures`

- [ ] **Step 3: Implement identify_core_figures and extract_figure_contexts**

Append to `src/deepaper/registry.py`:

```python
MAX_CORE_FIGURES = 3
CORE_RATIO_CAP = 0.2
MIN_CORE_SCORE = 3


def identify_core_figures(
    registry: dict,
    text_by_page: dict[int, str],
    total_pages: int,
) -> list[dict]:
    """Identify 'soul figures' — Figures that carry the paper's core idea.

    Uses 5 scoring signals. Applies anti-inflation: hard cap, ratio cap,
    competitive ranking.
    """
    if not registry or not text_by_page or total_pages == 0:
        return []

    full_text = "\n".join(str(v) for v in text_by_page.values())
    intro_end = max(1, int(total_pages * 0.2))
    intro_text = "\n".join(
        str(text_by_page[p]) for p in text_by_page if p <= intro_end
    )

    total_figures = sum(1 for v in registry.values() if v["type"] == "Figure")
    if total_figures == 0:
        return []

    budget = min(MAX_CORE_FIGURES, max(1, int(total_figures * CORE_RATIO_CAP)))

    candidates = []
    for key, info in registry.items():
        if info["type"] != "Figure":
            continue

        fig_id = info["id"]
        pattern = rf"(?:Figure|Fig)\s*\.?\s*{fig_id}(?!\d)"

        ref_count = len(re.findall(pattern, full_text, re.IGNORECASE))
        in_intro = bool(re.search(pattern, intro_text, re.IGNORECASE))
        def_page = info.get("definition_page") or 999
        is_early = def_page <= total_pages * 0.3

        # Caption length: find caption text on definition page
        caption_len = 0
        if info.get("definition_page") and info["definition_page"] in text_by_page:
            cap_match = re.search(
                rf"(?:Figure|Fig)\s*\.?\s*{fig_id}\s*[:.：。]\s*(.*?)(?:\n\n|\Z)",
                text_by_page[info["definition_page"]],
                re.IGNORECASE | re.DOTALL,
            )
            if cap_match:
                caption_len = len(cap_match.group(1).strip())

        score = sum([
            ref_count >= 3,
            in_intro,
            is_early,
            caption_len > 80,
            int(fig_id) <= 2,
        ])

        if score >= MIN_CORE_SCORE:
            candidates.append({
                "key": key,
                "id": fig_id,
                "page": def_page,
                "score": score,
                "ref_count": ref_count,
            })

    # Competitive ranking: sort by score desc, page asc, ref_count desc
    candidates.sort(key=lambda x: (-x["score"], x["page"], -x["ref_count"]))
    return candidates[:budget]


def extract_figure_contexts(
    text_by_page: dict[int, str],
    core_figures: list[dict],
) -> dict:
    """Extract text-based descriptions for each core figure.

    Returns caption + all paragraphs referencing the figure.
    More token-efficient than reading PDF images.
    """
    contexts = {}

    for fig in core_figures:
        fig_id = fig["id"]
        fig_key = fig["key"]
        pattern = rf"(?:Figure|Fig)\s*\.?\s*{fig_id}(?!\d)"

        # Caption
        caption = ""
        def_page = fig.get("page")
        if def_page and def_page in text_by_page:
            cap_match = re.search(
                rf"(?:Figure|Fig)\s*\.?\s*{fig_id}\s*[:.：。]\s*(.*?)(?:\n\n|\Z)",
                text_by_page[def_page],
                re.IGNORECASE | re.DOTALL,
            )
            if cap_match:
                caption = cap_match.group(1).strip()

        # All referencing paragraphs
        references = []
        for _page_no, text in text_by_page.items():
            for para in text.split("\n\n"):
                if re.search(pattern, para, re.IGNORECASE):
                    stripped = para.strip()
                    if stripped and stripped not in references:
                        references.append(stripped)

        contexts[fig_key] = {
            "caption": caption,
            "references": references,
        }

    return contexts
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_registry.py::TestCoreFigures -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/registry.py tests/test_registry.py
git commit -m "feat: add core figure identification and context extraction"
```

---

## Task 4: Paper Profile (`registry.py` — Part 3)

**Files:**
- Modify: `src/deepaper/registry.py`
- Modify: `tests/test_registry.py`

- [ ] **Step 1: Write failing tests for compute_paper_profile and build_coverage_checklist**

Append to `tests/test_registry.py`:

```python
class TestPaperProfile:
    def test_basic_profile(self):
        from deepaper.registry import compute_paper_profile

        text_by_page = {
            1: "1. Introduction\nWe study language models.",
            2: "2. Method\n2.1 Attention Mechanism\nWe propose Eq. 1.\n2.2 Training\nWe use Adam.",
            3: "3. Experiments\nTable 1 shows results. See Eq. 2.",
            4: "4. Related Work\nPrior work includes BERT.",
        }
        registry = {
            "Table_1": {"type": "Table", "id": "1", "has_caption": True},
            "Figure_1": {"type": "Figure", "id": "1", "has_caption": True},
        }
        profile = compute_paper_profile(text_by_page, registry)

        assert profile["total_pages"] == 4
        assert profile["num_tables"] == 1
        assert profile["num_figures"] == 1
        assert profile["num_equations"] >= 1
        assert isinstance(profile["subsection_headings"], list)

    def test_empty_input(self):
        from deepaper.registry import compute_paper_profile

        profile = compute_paper_profile({}, {})
        assert profile["total_pages"] == 0
        assert profile["num_tables"] == 0

    def test_section_detection(self):
        from deepaper.registry import compute_paper_profile

        text_by_page = {
            1: "1. Introduction\n" + "word " * 100,
            2: "2. Method\n2.1 Sub Method A\n" + "word " * 200,
            3: "3. Experiments\n" + "word " * 150,
        }
        profile = compute_paper_profile(text_by_page, {})
        # Should detect some section structure
        assert profile["total_chars"] > 0


class TestCoverageChecklist:
    def test_builds_checklist_from_registry(self):
        from deepaper.registry import build_coverage_checklist

        text_by_page = {
            1: "1. Introduction",
            2: "2. Method\n2.1 Attention\nSee Eq. 1.\n2.2 Routing\nSee Eq. 2.",
            3: "3. Experiments",
        }
        registry = {
            "Table_1": {"type": "Table", "id": "1", "has_caption": True},
            "Figure_1": {"type": "Figure", "id": "1", "has_caption": True, "is_core": True},
        }
        subsection_headings = ["2.1 Attention", "2.2 Routing"]

        checklist = build_coverage_checklist(
            text_by_page, registry, subsection_headings
        )

        # Should contain entries for headings, equations, tables, figures
        assert any("heading:" in k for k in checklist)
        assert any("equation:" in k for k in checklist)
        assert any("table:" in k for k in checklist)
        assert any("figure:" in k for k in checklist)

    def test_empty_inputs(self):
        from deepaper.registry import build_coverage_checklist

        checklist = build_coverage_checklist({}, {}, [])
        assert checklist == {}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_registry.py::TestPaperProfile tests/test_registry.py::TestCoverageChecklist -v`
Expected: FAIL — `ImportError`

- [ ] **Step 3: Implement compute_paper_profile and build_coverage_checklist**

Append to `src/deepaper/registry.py`:

```python
# --- Section header patterns for academic papers ---
_SECTION_PATTERNS = [
    # "1. Introduction", "2. Method", "3. Experiments", "4. Related Work"
    re.compile(r"^(\d+)\.\s+(\w[\w\s]+)", re.MULTILINE),
    # "Introduction", "Methodology", "Experiments" (no numbering)
    re.compile(
        r"^(Introduction|Abstract|Method(?:ology|s)?|Approach|"
        r"Experiment(?:s|al)?|Results?|Discussion|"
        r"Related\s+Work|Background|Conclusion(?:s)?|"
        r"Analysis|Evaluation|Implementation|Training|"
        r"Appendix)\b",
        re.MULTILINE | re.IGNORECASE,
    ),
]

_SUBSECTION_PATTERN = re.compile(
    r"^(\d+\.\d+)\s+(.+)", re.MULTILINE
)

# Map detected section names to canonical names
_SECTION_ALIASES = {
    "introduction": "Introduction",
    "abstract": "Introduction",
    "method": "Method", "methodology": "Method", "methods": "Method",
    "approach": "Method",
    "experiment": "Experiments", "experiments": "Experiments",
    "experimental": "Experiments",
    "results": "Experiments", "result": "Experiments",
    "evaluation": "Experiments", "analysis": "Experiments",
    "related work": "Related Work", "background": "Related Work",
    "discussion": "Discussion",
    "conclusion": "Conclusion", "conclusions": "Conclusion",
    "training": "Method", "implementation": "Method",
    "appendix": "Appendix",
}


def _detect_sections(full_text: str) -> dict[str, int]:
    """Detect paper sections and estimate character count per section."""
    # Find section boundaries
    boundaries = []
    for pattern in _SECTION_PATTERNS:
        for m in pattern.finditer(full_text):
            name = m.group(0).strip().rstrip(".")
            # Remove leading number: "1. Introduction" → "Introduction"
            clean = re.sub(r"^\d+\.\s*", "", name).strip()
            canonical = _SECTION_ALIASES.get(clean.lower(), clean)
            boundaries.append((m.start(), canonical))

    if not boundaries:
        return {}

    boundaries.sort(key=lambda x: x[0])

    section_chars = {}
    for i, (start, name) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(full_text)
        char_count = end - start
        # Accumulate if same canonical name appears multiple times
        section_chars[name] = section_chars.get(name, 0) + char_count

    return section_chars


def compute_paper_profile(
    text_by_page: dict[int, str],
    visual_registry: dict,
) -> dict:
    """Extract structural features from the paper text. Zero LLM cost.

    This is the ground truth anchor for all dynamic thresholds.
    """
    full_text = "\n".join(str(v) for v in text_by_page.values())
    total_pages = len(text_by_page)

    section_chars = _detect_sections(full_text)

    subsection_headings = [
        m.group(0).strip()
        for m in _SUBSECTION_PATTERN.finditer(full_text)
    ]

    num_tables = sum(
        1 for v in visual_registry.values()
        if v["type"] == "Table" and v.get("has_caption")
    )
    num_figures = sum(
        1 for v in visual_registry.values()
        if v["type"] == "Figure" and v.get("has_caption")
    )
    num_equations = len(
        set(re.findall(r"(?:Eq\.|Equation)\s*\(?(\d+)", full_text, re.IGNORECASE))
    )

    return {
        "total_pages": total_pages,
        "total_chars": len(full_text),
        "section_chars": section_chars,
        "subsection_headings": subsection_headings,
        "num_tables": num_tables,
        "num_figures": num_figures,
        "num_equations": num_equations,
    }


def build_coverage_checklist(
    text_by_page: dict[int, str],
    visual_registry: dict,
    subsection_headings: list[str],
) -> dict:
    """Build a checklist of structural elements the Writer output should cover.

    Only includes elements the paper explicitly declared as important:
    subsection headings, numbered equations, tables, core figures.
    """
    if not text_by_page and not visual_registry and not subsection_headings:
        return {}

    full_text = "\n".join(str(v) for v in text_by_page.values())
    checklist = {}

    # Subsection headings
    for heading in subsection_headings:
        # Extract the text part: "2.1 Attention" → "Attention"
        text_part = re.sub(r"^\d+\.\d+\s*", "", heading).strip()
        if text_part:
            checklist[f"heading:{heading}"] = {
                "source": "subsection",
                "match_text": text_part,
            }

    # Numbered equations
    equations = set(
        re.findall(r"(?:Eq\.|Equation)\s*\(?(\d+)", full_text, re.IGNORECASE)
    )
    for eq_id in equations:
        checklist[f"equation:{eq_id}"] = {
            "source": "equation",
            "match_pattern": rf"(?:Eq|Equation|公式|式)\s*\.?\s*\(?{eq_id}\)?",
        }

    # Tables with captions
    for key, info in visual_registry.items():
        if info["type"] == "Table" and info.get("has_caption"):
            checklist[f"table:{info['id']}"] = {
                "source": "table",
                "match_pattern": rf"(?:Table|表)\s*{info['id']}",
            }

    # Core figures
    for key, info in visual_registry.items():
        if info.get("is_core"):
            checklist[f"figure:{info['id']}"] = {
                "source": "core_figure",
                "match_pattern": rf"(?:Figure|Fig|图)\s*\.?\s*{info['id']}",
            }

    return checklist
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_registry.py::TestPaperProfile tests/test_registry.py::TestCoverageChecklist -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/registry.py tests/test_registry.py
git commit -m "feat: add paper profile extraction and coverage checklist"
```

---

## Task 5: Extractor Checks (`extractor.py`)

**Files:**
- Create: `src/deepaper/extractor.py`
- Create: `tests/test_extractor_checks.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_extractor_checks.py
"""Tests for StructCheck and Auditor."""
import pytest


class TestStructCheck:
    def test_all_sections_present(self):
        from deepaper.extractor import struct_check

        notes = "\n".join(
            f"## {s}\n{'x' * 300}"
            for s in [
                "META", "MAIN_RESULTS", "ABLATIONS", "HYPERPARAMETERS",
                "FORMULAS", "DATA_COMPOSITION", "EVAL_CONFIG",
                "TRAINING_COSTS", "DESIGN_DECISIONS", "RELATED_WORK", "BASELINES",
            ]
        )
        result = struct_check(notes, total_pages=30, paper_profile={})
        assert result["passed"] is True
        assert result["missing_sections"] == []

    def test_missing_section(self):
        from deepaper.extractor import struct_check

        # Omit ABLATIONS and TRAINING_COSTS
        notes = "\n".join(
            f"## {s}\n{'x' * 300}"
            for s in [
                "META", "MAIN_RESULTS", "HYPERPARAMETERS",
                "FORMULAS", "DATA_COMPOSITION", "EVAL_CONFIG",
                "DESIGN_DECISIONS", "RELATED_WORK", "BASELINES",
            ]
        )
        result = struct_check(notes, total_pages=30, paper_profile={})
        assert result["passed"] is False
        assert "ABLATIONS" in result["missing_sections"]
        assert "TRAINING_COSTS" in result["missing_sections"]

    def test_thin_section(self):
        from deepaper.extractor import struct_check

        notes = "\n".join(
            f"## {s}\n{'x' * 300}"
            for s in [
                "META", "MAIN_RESULTS", "ABLATIONS", "HYPERPARAMETERS",
                "FORMULAS", "DATA_COMPOSITION", "EVAL_CONFIG",
                "TRAINING_COSTS", "DESIGN_DECISIONS", "RELATED_WORK", "BASELINES",
            ]
        )
        # Make META too thin
        notes = notes.replace("## META\n" + "x" * 300, "## META\nshort")
        result = struct_check(notes, total_pages=30, paper_profile={})
        assert "META" in result["thin_sections"]


class TestParseNotesSections:
    def test_parses_sections(self):
        from deepaper.extractor import parse_notes_sections

        notes = "## META\nSome meta\n## MAIN_RESULTS\nSome results\n## ABLATIONS\nSome ablations"
        sections = parse_notes_sections(notes)
        assert "META" in sections
        assert "MAIN_RESULTS" in sections
        assert "ABLATIONS" in sections
        assert "Some meta" in sections["META"]


class TestAuditCoverage:
    def test_full_coverage(self):
        from deepaper.extractor import audit_coverage

        text_by_page = {
            i: f"page {i} content alpha beta gamma delta {i * 100}"
            for i in range(1, 21)
        }
        # Notes mention content from all pages
        notes = " ".join(f"alpha beta gamma delta {i * 100}" for i in range(1, 21))
        result = audit_coverage(text_by_page, notes, total_pages=20)
        assert result["coverage_ratio"] >= 0.7

    def test_partial_coverage(self):
        from deepaper.extractor import audit_coverage

        text_by_page = {
            i: f"unique_term_page{i} " * 20
            for i in range(1, 21)
        }
        # Notes only reference first 5 pages
        notes = " ".join(f"unique_term_page{i}" for i in range(1, 6))
        result = audit_coverage(text_by_page, notes, total_pages=20)
        assert len(result["uncovered_segments"]) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_extractor_checks.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement extractor.py**

```python
# src/deepaper/extractor.py
"""Extractor validation: StructCheck and Auditor."""
from __future__ import annotations

import re
from collections import Counter

REQUIRED_SECTIONS = [
    "META", "MAIN_RESULTS", "ABLATIONS", "HYPERPARAMETERS",
    "FORMULAS", "DATA_COMPOSITION", "EVAL_CONFIG",
    "TRAINING_COSTS", "DESIGN_DECISIONS", "RELATED_WORK", "BASELINES",
]

# Minimum char per section. Dynamic values use paper_profile when available;
# these are the absolute floors.
_SECTION_FLOORS = {
    "META": 100,
    "MAIN_RESULTS": 200,
    "ABLATIONS": 100,
    "HYPERPARAMETERS": 50,
    "FORMULAS": 30,
    "DATA_COMPOSITION": 50,
    "EVAL_CONFIG": 50,
    "TRAINING_COSTS": 30,
    "DESIGN_DECISIONS": 50,
    "RELATED_WORK": 100,
    "BASELINES": 50,
}


def parse_notes_sections(notes: str) -> dict[str, str]:
    """Parse Extractor notes into sections by ## header."""
    sections: dict[str, str] = {}
    current_section = None
    current_lines: list[str] = []

    for line in notes.split("\n"):
        header_match = re.match(r"^##\s+(\S+)", line)
        if header_match:
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = header_match.group(1)
            current_lines = []
        else:
            current_lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def _compute_thresholds(
    total_pages: int,
    paper_profile: dict,
) -> dict[str, int]:
    """Compute dynamic minimum char counts from paper_profile."""
    sc = paper_profile.get("section_chars", {})
    experiment_chars = sc.get("Experiments", 0)
    method_chars = sc.get("Method", 0)
    related_chars = sc.get("Related Work", 0)
    num_tables = paper_profile.get("num_tables", 0)
    num_equations = paper_profile.get("num_equations", 0)

    return {
        "META": 100,
        "MAIN_RESULTS": max(200, int(experiment_chars * 0.3)),
        "ABLATIONS": max(100, int(experiment_chars * 0.15)),
        "HYPERPARAMETERS": max(50, int(total_pages * 20)),
        "FORMULAS": max(30, num_equations * 30),
        "DATA_COMPOSITION": max(50, int(total_pages * 15)),
        "EVAL_CONFIG": max(50, int(experiment_chars * 0.1)),
        "TRAINING_COSTS": 30,
        "DESIGN_DECISIONS": max(50, int(method_chars * 0.15)),
        "RELATED_WORK": max(100, int(related_chars * 0.3)),
        "BASELINES": max(50, num_tables * 50),
    }


def struct_check(
    notes: str,
    total_pages: int,
    paper_profile: dict,
) -> dict:
    """Check that Extractor notes contain all required sections with enough content."""
    sections = parse_notes_sections(notes)
    thresholds = _compute_thresholds(total_pages, paper_profile)

    missing = [s for s in REQUIRED_SECTIONS if s not in sections]
    thin = [
        s for s in REQUIRED_SECTIONS
        if s in sections and len(sections[s]) < thresholds.get(s, _SECTION_FLOORS.get(s, 0))
    ]

    return {
        "passed": len(missing) == 0 and len(thin) == 0,
        "missing_sections": missing,
        "thin_sections": thin,
        "thresholds": thresholds,
    }


def audit_coverage(
    text_by_page: dict[int, str],
    notes: str,
    total_pages: int,
    chunk_size: int = 10,
) -> dict:
    """Check that notes cover content from all page segments."""
    if total_pages == 0:
        return {"coverage_ratio": 1.0, "uncovered_segments": []}

    segments = []
    pages = sorted(text_by_page.keys())
    for i in range(0, len(pages), chunk_size):
        seg_pages = pages[i : i + chunk_size]
        segments.append((seg_pages[0], seg_pages[-1]))

    notes_lower = notes.lower()
    uncovered = []

    for seg_start, seg_end in segments:
        # Extract distinctive words from this segment
        seg_text = " ".join(
            str(text_by_page.get(p, ""))
            for p in range(seg_start, seg_end + 1)
        )
        words = re.findall(r"\b[a-zA-Z]{4,}\b", seg_text.lower())
        word_counts = Counter(words)
        # Take top-20 most frequent words as fingerprint
        distinctive = [w for w, _ in word_counts.most_common(20)]

        if not distinctive:
            continue

        overlap = sum(1 for w in distinctive if w in notes_lower)
        if overlap / len(distinctive) < 0.3:
            uncovered.append((seg_start, seg_end))

    covered_segments = len(segments) - len(uncovered)
    coverage_ratio = covered_segments / max(len(segments), 1)

    return {
        "coverage_ratio": round(coverage_ratio, 2),
        "uncovered_segments": uncovered,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_extractor_checks.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/extractor.py tests/test_extractor_checks.py
git commit -m "feat: add StructCheck and Auditor for Extractor validation"
```

---

## Task 6: HardGates (`gates.py`)

**Files:**
- Create: `src/deepaper/gates.py`
- Create: `tests/test_gates.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_gates.py
"""Tests for HardGates programmatic quality checks."""
import pytest


class TestH1BaselinesFormat:
    def test_valid_baselines(self):
        from deepaper.gates import check_baselines_format

        md = "---\nbaselines:\n  - GPT-4 (1.8T params, dense)\n  - LLaMA-3 (70B params, dense)\n---\nBody"
        assert check_baselines_format(md)["passed"] is True

    def test_missing_baselines(self):
        from deepaper.gates import check_baselines_format

        md = "---\ntitle: test\n---\nBody"
        assert check_baselines_format(md)["passed"] is False


class TestH2Coverage:
    def test_good_coverage(self):
        from deepaper.gates import check_structural_coverage

        checklist = {
            "heading:2.1 Attention": {"source": "subsection", "match_text": "Attention"},
            "equation:1": {"source": "equation", "match_pattern": r"(?:Eq|公式)\s*\.?\s*\(?1\)?"},
            "table:1": {"source": "table", "match_pattern": r"(?:Table|表)\s*1"},
        }
        merged = "We describe the Attention mechanism. See Eq. 1. Table 1 shows results."
        result = check_structural_coverage(merged, checklist)
        assert result["passed"] is True
        assert result["coverage"] >= 0.6

    def test_low_coverage(self):
        from deepaper.gates import check_structural_coverage

        checklist = {
            "heading:2.1 Attention": {"source": "subsection", "match_text": "Attention"},
            "heading:2.2 Routing": {"source": "subsection", "match_text": "Routing"},
            "heading:2.3 Training": {"source": "subsection", "match_text": "Training"},
            "equation:1": {"source": "equation", "match_pattern": r"(?:Eq|公式)\s*\.?\s*\(?1\)?"},
            "table:1": {"source": "table", "match_pattern": r"(?:Table|表)\s*1"},
        }
        merged = "We describe something. Not much detail."
        result = check_structural_coverage(merged, checklist)
        assert result["passed"] is False

    def test_empty_checklist_passes(self):
        from deepaper.gates import check_structural_coverage

        result = check_structural_coverage("Any content", {})
        assert result["passed"] is True


class TestH3CharFloors:
    def test_passes_when_sufficient(self):
        from deepaper.gates import check_char_floors

        md = "#### 方法详解\n" + "x" * 2500 + "\n#### 实验与归因\n" + "x" * 2000
        result = check_char_floors(md)
        assert result["passed"] is True

    def test_fails_when_degenerate(self):
        from deepaper.gates import check_char_floors

        md = "#### 方法详解\nshort\n#### 实验与归因\nshort"
        result = check_char_floors(md)
        assert result["passed"] is False


class TestH5TldrNumbers:
    def test_enough_numbers(self):
        from deepaper.gates import check_tldr_numbers

        md = '---\ntldr: "Achieves 95.2% accuracy and 3x speedup on benchmark"\n---\nBody'
        assert check_tldr_numbers(md)["passed"] is True

    def test_too_few_numbers(self):
        from deepaper.gates import check_tldr_numbers

        md = '---\ntldr: "A new method for language modeling"\n---\nBody'
        assert check_tldr_numbers(md)["passed"] is False


class TestH6HeadingLevels:
    def test_valid_h4_h5_h6(self):
        from deepaper.gates import check_heading_levels

        md = "---\ntitle: test\n---\n#### Main\n##### Sub\n###### Detail\nContent"
        assert check_heading_levels(md)["passed"] is True

    def test_rejects_h1(self):
        from deepaper.gates import check_heading_levels

        md = "---\ntitle: test\n---\n# Bad Heading\n#### Good Heading"
        assert check_heading_levels(md)["passed"] is False

    def test_rejects_h2(self):
        from deepaper.gates import check_heading_levels

        md = "---\ntitle: test\n---\n## Bad Heading"
        assert check_heading_levels(md)["passed"] is False


class TestH8NumberFingerprint:
    def test_traceable_numbers(self):
        from deepaper.gates import check_number_fingerprint

        text_by_page = {8: "Model A achieves 95.2 accuracy and 87.6 F1 score."}
        registry = {
            "Table_1": {"type": "Table", "id": "1", "definition_page": 8, "has_caption": True}
        }
        merged = "| Model | Acc | F1 |\n|---|---|---|\n| A | 95.2 | 87.6 |"
        result = check_number_fingerprint(merged, text_by_page, registry)
        assert result["passed"] is True

    def test_fabricated_numbers(self):
        from deepaper.gates import check_number_fingerprint

        text_by_page = {8: "Model A achieves 95.2 accuracy."}
        registry = {
            "Table_1": {"type": "Table", "id": "1", "definition_page": 8, "has_caption": True}
        }
        # Writer fabricated 99.1 and 88.3 which don't exist in source
        merged = "| Model | Acc | F1 |\n|---|---|---|\n| A | 99.1 | 88.3 |\n| B | 77.4 | 66.5 |"
        result = check_number_fingerprint(merged, text_by_page, registry)
        assert result["passed"] is False
        assert result["untraced_ratio"] > 0.3


class TestRunHardGates:
    def test_skips_gates_when_data_unavailable(self):
        from deepaper.gates import run_hard_gates

        # Minimal valid markdown
        md = (
            "---\ntldr: 'Achieves 95.2% and 3x speedup'\n"
            "baselines:\n  - GPT-4 (1.8T, dense)\n  - LLaMA (70B, dense)\n---\n"
            "#### 方法详解\n" + "x" * 2500 + "\n"
            "#### 实验与归因\n" + "x" * 2000 + "\n"
        )
        result = run_hard_gates(
            merged_md=md,
            coverage_checklist={},
            core_figures=[],
            text_by_page=None,  # unavailable
            registry=None,      # unavailable
        )
        # H4, H7, H8 should be skipped
        assert result["results"]["H4"]["skipped"] is True
        assert result["results"]["H7"]["skipped"] is True
        assert result["results"]["H8"]["skipped"] is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_gates.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement gates.py**

```python
# src/deepaper/gates.py
"""HardGates: programmatic quality checks for Writer output."""
from __future__ import annotations

import re

import yaml

# Section char floors — only catches degenerate (near-empty) output
_SECTION_CHAR_FLOORS = {
    "方法详解": 2000,
    "实验与归因": 1500,
    "核心速览": 500,
    "动机与第一性原理": 800,
    "专家批判": 800,
    "机制迁移分析": 800,
    "背景知识补充": 300,
}


def _extract_body(md: str) -> str:
    """Extract markdown body after YAML frontmatter."""
    if md.startswith("---"):
        end = md.find("---", 3)
        if end != -1:
            return md[end + 3:].strip()
    return md


def _extract_frontmatter(md: str) -> dict:
    """Extract YAML frontmatter dict from markdown."""
    if md.startswith("---"):
        end = md.find("---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(md[3:end])
                return fm if isinstance(fm, dict) else {}
            except yaml.YAMLError:
                return {}
    return {}


def _extract_sections_h4(body: str) -> dict[str, str]:
    """Split body by #### headings into {title: content}."""
    sections: dict[str, str] = {}
    current_title = None
    current_lines: list[str] = []

    for line in body.split("\n"):
        m = re.match(r"^####\s+(.+)", line)
        if m:
            if current_title:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title:
        sections[current_title] = "\n".join(current_lines).strip()

    return sections


# --- Individual Gate Checks ---


def check_baselines_format(md: str) -> dict:
    """H1: Baselines in YAML frontmatter, one per line, with params and type."""
    fm = _extract_frontmatter(md)
    baselines = fm.get("baselines", [])
    if not baselines or not isinstance(baselines, list):
        return {"passed": False, "reason": "No baselines in frontmatter"}
    if len(baselines) < 2:
        return {"passed": False, "count": len(baselines), "reason": "Need ≥2 baselines"}
    return {"passed": True, "count": len(baselines)}


def check_structural_coverage(merged: str, checklist: dict) -> dict:
    """H2: Coverage of paper's structural elements ≥ 60%."""
    if not checklist:
        return {"passed": True, "coverage": 1.0, "missing": []}

    covered = []
    missing = []

    for item_id, item in checklist.items():
        pattern = item.get("match_pattern") or re.escape(item.get("match_text", ""))
        if not pattern:
            covered.append(item_id)
            continue
        if re.search(pattern, merged, re.IGNORECASE):
            covered.append(item_id)
        else:
            missing.append(item_id)

    total = len(checklist)
    coverage = len(covered) / total
    return {
        "passed": coverage >= 0.6,
        "coverage": round(coverage, 2),
        "missing": missing,
    }


def check_char_floors(md: str) -> dict:
    """H3: Each section meets minimum character floor (anti-degenerate)."""
    body = _extract_body(md)
    sections = _extract_sections_h4(body)

    failures = {}
    for section_name, min_chars in _SECTION_CHAR_FLOORS.items():
        content = sections.get(section_name, "")
        if len(content) < min_chars:
            failures[section_name] = {
                "actual": len(content),
                "required": min_chars,
            }

    return {
        "passed": len(failures) == 0,
        "failures": failures,
    }


def check_table_count(md: str, registry: dict) -> dict:
    """H4: Writer output contains ≥ registry Table count markdown tables."""
    expected = sum(
        1 for v in registry.values()
        if v["type"] == "Table" and v.get("has_caption")
    )
    body = _extract_body(md)
    # Count markdown tables: lines starting with |
    table_blocks = re.findall(
        r"(?:^\|.+\|$\n?){3,}", body, re.MULTILINE
    )
    actual = len(table_blocks)
    return {
        "passed": actual >= expected,
        "actual": actual,
        "required": expected,
    }


def check_tldr_numbers(md: str) -> dict:
    """H5: TL;DR contains ≥ 2 numbers."""
    fm = _extract_frontmatter(md)
    tldr = str(fm.get("tldr", ""))
    numbers = re.findall(r"\d+\.?\d*", tldr)
    return {
        "passed": len(numbers) >= 2,
        "count": len(numbers),
    }


def check_heading_levels(md: str) -> dict:
    """H6: Only h4/h5/h6 headings in body (no h1/h2/h3/h7+)."""
    body = _extract_body(md)
    # Find any heading that is NOT h4/h5/h6
    bad_headings = re.findall(r"^(#{1,3}\s+.+|#{7,}\s+.+)", body, re.MULTILINE)
    return {
        "passed": len(bad_headings) == 0,
        "violations": bad_headings[:5],  # Show first 5
    }


def check_core_figures_referenced(md: str, core_figures: list[dict]) -> dict:
    """H7: Every core figure is mentioned in the output."""
    if not core_figures:
        return {"passed": True, "missing": []}

    body = _extract_body(md)
    missing = []
    for fig in core_figures:
        fig_id = fig["id"]
        pattern = rf"(?:Figure|Fig|图)\s*\.?\s*{fig_id}"
        if not re.search(pattern, body, re.IGNORECASE):
            missing.append(f"Figure_{fig_id}")

    return {"passed": len(missing) == 0, "missing": missing}


def check_number_fingerprint(
    md: str,
    text_by_page: dict[int, str],
    registry: dict,
    threshold: float = 0.3,
    tolerance: float = 0.15,
) -> dict:
    """H8: Numbers in Writer's tables must be traceable to source text."""
    body = _extract_body(md)

    # Build fingerprint: all numbers on Table definition pages
    source_numbers: set[str] = set()
    for key, info in registry.items():
        if info["type"] != "Table" or not info.get("has_caption"):
            continue
        def_page = info.get("definition_page")
        if def_page and def_page in text_by_page:
            page_nums = re.findall(r"(?<!\w)(\d+\.?\d*)", text_by_page[def_page])
            source_numbers.update(page_nums)

    if not source_numbers:
        return {"passed": True, "reason": "No source fingerprint available"}

    # Extract numbers from Writer's markdown tables
    table_lines = [
        line for line in body.split("\n")
        if line.strip().startswith("|") and not re.match(r"^\|[\s\-:]+\|$", line.strip())
    ]
    writer_numbers = re.findall(r"(?<!\w)(\d+\.?\d*)", "\n".join(table_lines))

    if not writer_numbers:
        return {"passed": True, "reason": "No tables in Writer output"}

    # Check traceability
    untraced = []
    for n in writer_numbers:
        if n in source_numbers:
            continue
        # Tolerance check
        try:
            n_float = float(n)
            if any(
                abs(n_float - float(s)) < tolerance
                for s in source_numbers
                if re.match(r"^\d+\.?\d*$", s)
            ):
                continue
        except ValueError:
            pass
        untraced.append(n)

    ratio = len(untraced) / max(len(writer_numbers), 1)
    suspect_tables = []
    if ratio > threshold:
        suspect_tables = [
            k for k, v in registry.items()
            if v["type"] == "Table" and v.get("has_caption")
        ]

    return {
        "passed": ratio <= threshold,
        "untraced_ratio": round(ratio, 2),
        "untraced_count": len(untraced),
        "total_numbers": len(writer_numbers),
        "suspect_tables": suspect_tables,
    }


# --- Orchestrator ---


def run_hard_gates(
    merged_md: str,
    coverage_checklist: dict,
    core_figures: list[dict],
    text_by_page: dict[int, str] | None,
    registry: dict | None,
) -> dict:
    """Run all 8 HardGates. Skips gates when required data is unavailable."""
    results = {}

    results["H1"] = check_baselines_format(merged_md)
    results["H2"] = check_structural_coverage(merged_md, coverage_checklist)
    results["H3"] = check_char_floors(merged_md)
    results["H5"] = check_tldr_numbers(merged_md)
    results["H6"] = check_heading_levels(merged_md)

    if registry:
        results["H4"] = check_table_count(merged_md, registry)
        results["H7"] = check_core_figures_referenced(merged_md, core_figures)
    else:
        results["H4"] = {"passed": True, "skipped": True}
        results["H7"] = {"passed": True, "skipped": True}

    if text_by_page and registry:
        results["H8"] = check_number_fingerprint(merged_md, text_by_page, registry)
    else:
        results["H8"] = {"passed": True, "skipped": True}

    failed = [k for k, v in results.items() if not v["passed"]]
    return {
        "passed": len(failed) == 0,
        "results": results,
        "failed": failed,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_gates.py -v`
Expected: All 12 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/gates.py tests/test_gates.py
git commit -m "feat: add HardGates programmatic quality checks (H1-H8)"
```

---

## Task 7: Update `writer.py` for Quality Metadata

**Files:**
- Modify: `src/deepaper/writer.py:112-186`
- Modify: `tests/test_writer.py`

- [ ] **Step 1: Write failing test**

Append to `tests/test_writer.py`:

```python
def test_write_paper_note_with_quality_fields(tmp_path):
    """write_paper_note should include quality, failed_gates, pipeline_version in frontmatter."""
    from deepaper.writer import write_paper_note
    import yaml

    metadata = {
        "title": "Test Paper",
        "authors": ["Author A"],
        "date": "2024-01-01",
        "arxiv_id": "2401.99999",
        "url": "https://arxiv.org/abs/2401.99999",
    }
    analysis_fm = {"venue": "arxiv", "tldr": "A test paper"}
    result = write_paper_note(
        analysis_fm, "Body content", metadata, ["test"],
        tmp_path, category="misc",
        quality="partial", failed_gates=["S5", "S7"], pipeline_version=2,
    )

    content = result.read_text()
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    fm = yaml.safe_load(fm_match.group(1))
    assert fm["quality"] == "partial"
    assert fm["failed_gates"] == ["S5", "S7"]
    assert fm["pipeline_version"] == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_writer.py::test_write_paper_note_with_quality_fields -v`
Expected: FAIL — `TypeError: write_paper_note() got an unexpected keyword argument 'quality'`

- [ ] **Step 3: Update write_paper_note signature and implementation**

In `src/deepaper/writer.py`, change the function signature (line 112) and frontmatter dict (line 150):

```python
def write_paper_note(
    analysis_fm: dict,
    analysis_body: str,
    metadata: dict,
    tags: list[str],
    output_dir: Path,
    force: bool = False,
    category: str = "misc",
    quality: str = "full",
    failed_gates: list[str] | None = None,
    pipeline_version: int = 1,
) -> Path:
```

And add to the frontmatter dict after `"category": category,` (line 173):

```python
        # --- Pipeline quality metadata ---
        "quality": quality,
        "failed_gates": failed_gates or [],
        "pipeline_version": pipeline_version,
```

- [ ] **Step 4: Run all writer tests to verify nothing broke**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_writer.py -v`
Expected: All tests PASS (including the new one)

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/writer.py tests/test_writer.py
git commit -m "feat: add quality metadata fields to paper note frontmatter"
```

---

## Task 8: New CLI Subcommands

**Files:**
- Modify: `src/deepaper/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_cli.py`:

```python
def test_registry_command(tmp_path, monkeypatch):
    """deepaper registry should output visual_registry.json content."""
    from typer.testing import CliRunner
    from deepaper.cli import app

    runner = CliRunner()
    # Create a minimal text_by_page.json
    import json
    run_dir = tmp_path / ".deepaper" / "runs" / "2401.00001"
    run_dir.mkdir(parents=True)
    (run_dir / "text_by_page.json").write_text(json.dumps({
        "1": "Figure 1: Architecture overview.\nWe propose a method.",
        "2": "Table 1: Results.\n| Model | Acc |\n| Ours | 95 |",
    }))

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["registry", "2401.00001"])
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert "Table_1" in output or "Figure_1" in output


def test_gates_command_basic(tmp_path, monkeypatch):
    """deepaper gates should run HardGates and output JSON."""
    from typer.testing import CliRunner
    from deepaper.cli import app
    import json

    run_dir = tmp_path / ".deepaper" / "runs" / "2401.00001"
    run_dir.mkdir(parents=True)
    merged = (
        "---\ntldr: 'Achieves 95.2% and 3x speedup'\n"
        "baselines:\n  - GPT-4 (1.8T, dense)\n  - LLaMA (70B, dense)\n---\n"
        "#### 方法详解\n" + "x" * 2500 + "\n"
        "#### 实验与归因\n" + "x" * 2000 + "\n"
    )
    (run_dir / "merged.md").write_text(merged)

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["gates", "2401.00001"])
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert "passed" in output
    assert "results" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_cli.py::test_registry_command tests/test_cli.py::test_gates_command_basic -v`
Expected: FAIL

- [ ] **Step 3: Add registry and gates commands to cli.py**

Append to `src/deepaper/cli.py` before the final line:

```python
# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

@app.command()
def registry(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to build registry for."),
) -> None:
    """Build visual registry from extracted text and output as JSON."""
    root = Path.cwd()
    run_dir = root / ".deepaper" / "runs" / arxiv_id

    from deepaper.pipeline_io import safe_read_json
    text_by_page_raw = safe_read_json(str(run_dir / "text_by_page.json"), default={})
    text_by_page = {int(k): v for k, v in text_by_page_raw.items()}

    if not text_by_page:
        typer.echo(json.dumps({"error": "text_by_page.json not found or empty"}))
        raise typer.Exit(1)

    from deepaper.registry import build_visual_registry
    reg = build_visual_registry(text_by_page)

    from deepaper.pipeline_io import safe_write_json
    safe_write_json(str(run_dir / "visual_registry.json"), reg)

    typer.echo(json.dumps(reg, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------

@app.command()
def gates(
    arxiv_id: str = typer.Argument(..., help="arxiv ID to run gates on."),
) -> None:
    """Run HardGates on merged analysis and output results as JSON."""
    root = Path.cwd()
    run_dir = root / ".deepaper" / "runs" / arxiv_id

    merged_path = run_dir / "merged.md"
    if not merged_path.exists():
        typer.echo(json.dumps({"error": "merged.md not found"}))
        raise typer.Exit(1)

    merged_md = merged_path.read_text(encoding="utf-8")

    from deepaper.pipeline_io import safe_read_json
    registry = safe_read_json(str(run_dir / "visual_registry.json"))
    text_by_page_raw = safe_read_json(str(run_dir / "text_by_page.json"))
    text_by_page = (
        {int(k): v for k, v in text_by_page_raw.items()}
        if text_by_page_raw
        else None
    )

    from deepaper.registry import build_coverage_checklist, identify_core_figures, compute_paper_profile
    checklist = {}
    core_figures = []
    if text_by_page and registry:
        profile = compute_paper_profile(text_by_page, registry)
        core_figures = identify_core_figures(registry, text_by_page, profile["total_pages"])
        checklist = build_coverage_checklist(
            text_by_page, registry, profile.get("subsection_headings", [])
        )

    from deepaper.gates import run_hard_gates
    result = run_hard_gates(merged_md, checklist, core_figures, text_by_page, registry)

    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/test_cli.py::test_registry_command tests/test_cli.py::test_gates_command_basic -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/deepaper/cli.py tests/test_cli.py
git commit -m "feat: add registry and gates CLI subcommands"
```

---

## Task 9: Update .gitignore and pyproject.toml

**Files:**
- Modify: `.gitignore`
- Modify: `pyproject.toml`

- [ ] **Step 1: Add .deepaper/ to .gitignore**

Append to `.gitignore`:

```
# Pipeline run artifacts
.deepaper/
```

- [ ] **Step 2: Add pymupdf dependency to pyproject.toml**

In `pyproject.toml`, add `"pymupdf>=1.24"` to the `dependencies` list.

- [ ] **Step 3: Verify**

Run: `cd /Users/bytedance/github/deepaper && python -c "import deepaper.registry; import deepaper.gates; import deepaper.extractor; import deepaper.pipeline_io; print('All modules importable')"`.
Expected: `All modules importable`

- [ ] **Step 4: Commit**

```bash
git add .gitignore pyproject.toml
git commit -m "chore: add .deepaper/ to gitignore, add pymupdf dependency"
```

---

## Task 10: Rewrite Slash Command (`deepaper.md`)

**Files:**
- Modify: `.claude/commands/deepaper.md`

This is the largest task. The slash command orchestrates the entire enhanced pipeline.

- [ ] **Step 1: Read the current slash command**

Run: `cat .claude/commands/deepaper.md` — understand every step before rewriting.

- [ ] **Step 2: Write the new slash command**

The new `.claude/commands/deepaper.md` must implement the full enhanced pipeline:

1. **Step 0: Setup** — check `which deepaper`, run `deepaper init` if needed
2. **Step 1: Download + Text Extract** — run `deepaper download $ARGUMENTS`, extract text with fitz page-by-page into `text_by_page.json`, extract full text to `text.txt`, build visual_registry via `deepaper registry {ARXIV_ID}`, compute paper_profile, identify core figures, extract figure contexts. All stored in `.deepaper/runs/{ARXIV_ID}/`.
3. **Step 2.1: Spawn Extractor** — reads `.deepaper/runs/{ARXIV_ID}/text.txt` (not PDF), outputs `notes.md`. Lightweight structural outline.
4. **Step 2.2: StructCheck + Auditor** — run programmatically via Bash. If missing/thin sections, send list back to Extractor for 1 retry.
5. **Step 2.3: Spawn Writers in parallel** — Writer-Visual (方法详解 + 实验与归因, gets figure_contexts + Table PDF pages), Writer-Text-1 (YAML + 核心速览 + 动机 + 专家批判, gets figure_contexts), Writer-Text-2 (机制迁移 + 背景补充, gets figure_contexts). Dynamic grouping based on registry.
6. **Step 2.4: Merge** — Conductor reads all three parts, concatenates: Text-1 + Visual + Text-2.
7. **Step 2.5: HardGates** — run `deepaper gates {ARXIV_ID}`. Parse JSON. If failed → skip Critic, go directly to Fixer with precise failure info.
8. **Step 2.6: SoftGates / Critic** — spawn Critic agent. Must output JSON verdict. If all pass → Step 3.
9. **Step 2.7: Fixer loop** — max 2 rounds. Each round: spawn Fixer with failed gate IDs + reasons. Re-run HardGates + Critic. Track best version. Special: if H8 fails, read suspect Table PDF pages and feed to Fixer.
10. **Step 3: Save** — run `deepaper save {ARXIV_ID} --category {category} --input .deepaper/runs/{ARXIV_ID}/merged.md`. Quality metadata passed via env or flags. Write report.json.

Key prompt content to include for each agent:
- **Extractor**: role, input path (text.txt not PDF), required 11 sections, output path
- **Writers**: assigned sections, format rules (h4/h5/h6), figure_contexts content, data discipline rules
- **Critic**: 7 SoftGates, must output JSON verdict with gate IDs
- **Fixer**: failed gate list + reasons, rules about not breaking passing sections

- [ ] **Step 3: Verify slash command is syntactically valid**

Run: `wc -l .claude/commands/deepaper.md` — confirm the file was written.
Run: `head -20 .claude/commands/deepaper.md` — check header looks right.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/deepaper.md
git commit -m "feat: rewrite slash command for enhanced pipeline with quality gates"
```

---

## Task 11: Run Full Test Suite and Fix

**Files:**
- All test files

- [ ] **Step 1: Run entire test suite**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/ -v`

- [ ] **Step 2: Fix any failures**

Address any test failures from integration between modules.

- [ ] **Step 3: Run again to confirm**

Run: `cd /Users/bytedance/github/deepaper && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Commit if fixes were needed**

```bash
git add -A
git commit -m "fix: resolve test failures from pipeline integration"
```

---

## Task 12: Update defaults.py Slash Command Loader

**Files:**
- Modify: `src/deepaper/defaults.py`

- [ ] **Step 1: Verify get_default_slash_command loads the new version**

The function reads from the package's `.claude/commands/deepaper.md`. Confirm it picks up the rewritten file.

Run: `cd /Users/bytedance/github/deepaper && python -c "from deepaper.defaults import get_default_slash_command; cmd = get_default_slash_command(); print(f'Length: {len(cmd)}'); print('HardGates' in cmd)"`
Expected: Length should be larger than before, and `HardGates` should appear in the content.

- [ ] **Step 2: If the loader doesn't pick up the new file, update the path**

Check `defaults.py` to see how `get_default_slash_command()` resolves the path. Update if needed to ensure it reads from the project's `.claude/commands/deepaper.md`.

- [ ] **Step 3: Commit if changes needed**

```bash
git add src/deepaper/defaults.py
git commit -m "fix: ensure slash command loader picks up enhanced pipeline version"
```

---

## Summary

| Task | Module | Tests | Description |
|------|--------|-------|-------------|
| 1 | pipeline_io.py | 9 | JSON safety layer |
| 2 | registry.py (part 1) | 5 | Visual registry: table/figure detection |
| 3 | registry.py (part 2) | 4 | Core figure identification + context extraction |
| 4 | registry.py (part 3) | 5 | Paper profile + coverage checklist |
| 5 | extractor.py | 6 | StructCheck + Auditor |
| 6 | gates.py | 12 | HardGates (H1-H8) |
| 7 | writer.py | 1 | Quality metadata in frontmatter |
| 8 | cli.py | 2 | New registry/gates subcommands |
| 9 | .gitignore, pyproject.toml | 0 | Config updates |
| 10 | deepaper.md | 0 | Slash command rewrite (largest task) |
| 11 | All tests | — | Integration test pass |
| 12 | defaults.py | 0 | Loader verification |
| **Total** | | **44** | |
