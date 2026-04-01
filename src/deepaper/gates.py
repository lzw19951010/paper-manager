"""HardGates — programmatic quality checks (H1-H8).

All checks run *before* the LLM Critic pass. Each gate returns a dict
with at minimum ``{"passed": bool}``, plus gate-specific detail fields.
The orchestrator ``run_hard_gates`` collects all results and marks gates
as *skipped* when prerequisite data is unavailable.
"""

from __future__ import annotations

import re
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Character-floor thresholds per h4 section (Chinese heading → min chars)
# ---------------------------------------------------------------------------

CHAR_FLOORS: dict[str, int] = {
    "方法详解": 2000,
    "实验与归因": 1500,
    "核心速览": 500,
    "动机与第一性原理": 800,
    "专家批判": 800,
    "机制迁移分析": 800,
    "背景知识补充": 300,
}

# Regex to extract numbers (integers and decimals) from text.
# Uses a lookahead for the trailing boundary so "3x" still captures "3".
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?(?=[^.\d]|$)")

# Regex to detect markdown headings at any level
_HEADING_RE = re.compile(r"^(#{1,7})\s+", re.MULTILINE)


# ===========================================================================
# Helper functions
# ===========================================================================

def _extract_frontmatter(md: str) -> dict:
    """Parse YAML frontmatter from markdown text.

    Expects ``---`` delimiters. Returns empty dict if none found.
    """
    md = md.strip()
    if not md.startswith("---"):
        return {}
    # Find the closing ---
    end = md.find("---", 3)
    if end == -1:
        return {}
    yaml_block = md[3:end].strip()
    try:
        parsed = yaml.safe_load(yaml_block)
        return parsed if isinstance(parsed, dict) else {}
    except yaml.YAMLError:
        return {}


def _extract_body(md: str) -> str:
    """Get markdown body after YAML frontmatter."""
    md = md.strip()
    if not md.startswith("---"):
        return md
    end = md.find("---", 3)
    if end == -1:
        return md
    return md[end + 3:].strip()


def _extract_sections_h4(body: str) -> dict[str, str]:
    """Split body by ``####`` headings into ``{title: content}``."""
    sections: dict[str, str] = {}
    pattern = re.compile(r"^####\s+(.+)$", re.MULTILINE)

    matches = list(pattern.finditer(body))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(body)
        content = body[start:end].strip()
        sections[title] = content

    return sections


# ===========================================================================
# H1: Baselines Format
# ===========================================================================

def check_baselines_format(md: str) -> dict:
    """Check YAML frontmatter has baselines list with >= 2 entries.

    Returns ``{passed, count}`` on success, ``{passed, reason}`` on failure.
    """
    fm = _extract_frontmatter(md)
    baselines = fm.get("baselines")

    if not isinstance(baselines, list):
        return {"passed": False, "reason": "baselines field missing or not a list"}

    count = len(baselines)
    if count < 2:
        return {"passed": False, "reason": f"only {count} baseline(s), need >= 2", "count": count}

    return {"passed": True, "count": count}


# ===========================================================================
# H2: Structural Coverage
# ===========================================================================

def check_structural_coverage(merged: str, checklist: dict) -> dict:
    """Check coverage >= 60% of structural elements.

    Each checklist entry has ``match_pattern`` or ``match_text``.
    Empty checklist = automatic pass.

    Returns ``{passed, coverage, missing}``.
    """
    if not checklist:
        return {"passed": True, "coverage": 1.0, "missing": []}

    matched = 0
    missing: list[str] = []

    for label, entry in checklist.items():
        found = False
        if "match_pattern" in entry:
            if re.search(entry["match_pattern"], merged):
                found = True
        if not found and "match_text" in entry:
            if entry["match_text"] in merged:
                found = True
        if found:
            matched += 1
        else:
            missing.append(label)

    coverage = matched / len(checklist)
    return {
        "passed": coverage >= 0.6,
        "coverage": round(coverage, 4),
        "missing": missing,
    }


# ===========================================================================
# H3: Character Floors
# ===========================================================================

def check_char_floors(md: str) -> dict:
    """Check each h4 section meets its minimum character floor.

    Returns ``{passed, failures}`` where failures is a list of dicts
    describing which sections fell short.
    """
    body = _extract_body(md)
    sections = _extract_sections_h4(body)

    failures: list[dict] = []
    for heading, floor in CHAR_FLOORS.items():
        if heading in sections:
            actual = len(sections[heading])
            if actual < floor:
                failures.append({
                    "section": heading,
                    "floor": floor,
                    "actual": actual,
                })

    return {"passed": len(failures) == 0, "failures": failures}


# ===========================================================================
# H4: Table Count
# ===========================================================================

def check_table_count(md: str, registry: dict) -> dict:
    """Check writer output contains >= registry Table count markdown tables.

    A markdown table is a block of 3+ consecutive pipe-delimited lines.

    Returns ``{passed, actual, required}``.
    """
    required = sum(
        1 for v in registry.values() if v.get("type") == "Table"
    )

    # Count markdown tables: blocks of 3+ consecutive lines starting with |
    body = _extract_body(md)
    lines = body.split("\n")
    actual = 0
    consecutive = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            consecutive += 1
        else:
            if consecutive >= 3:
                actual += 1
            consecutive = 0
    # Handle trailing table
    if consecutive >= 3:
        actual += 1

    return {
        "passed": actual >= required,
        "actual": actual,
        "required": required,
    }


# ===========================================================================
# H5: TL;DR Numbers
# ===========================================================================

def check_tldr_numbers(md: str) -> dict:
    """Check TL;DR in YAML frontmatter contains >= 2 numbers.

    Returns ``{passed, count}``.
    """
    fm = _extract_frontmatter(md)
    tldr = fm.get("tldr", "")
    if not isinstance(tldr, str):
        tldr = str(tldr)

    numbers = _NUMBER_RE.findall(tldr)
    count = len(numbers)
    return {"passed": count >= 2, "count": count}


# ===========================================================================
# H6: Heading Levels
# ===========================================================================

def check_heading_levels(md: str) -> dict:
    """Check body only uses h4/h5/h6. Reject h1/h2/h3/h7+.

    Returns ``{passed, violations}`` where violations is a list of strings.
    """
    body = _extract_body(md)
    violations: list[str] = []

    for m in _HEADING_RE.finditer(body):
        hashes = m.group(1)
        level = len(hashes)
        if level not in (4, 5, 6):
            # Get the heading text for context
            line_end = body.find("\n", m.start())
            if line_end == -1:
                line_end = len(body)
            heading_text = body[m.start():line_end].strip()
            violations.append(f"h{level}: {heading_text}")

    return {"passed": len(violations) == 0, "violations": violations}


# ===========================================================================
# H7: Core Figures Referenced
# ===========================================================================

def check_core_figures_referenced(md: str, core_figures: list[dict]) -> dict:
    """Check every core figure's ID appears in body.

    Returns ``{passed, missing}``.
    """
    if not core_figures:
        return {"passed": True, "missing": []}

    body = _extract_body(md)
    missing: list[str] = []

    for cf in core_figures:
        fig_id = cf.get("id") or cf.get("key", "")
        key = cf.get("key", f"Figure_{fig_id}")
        # Search for Figure N or Fig. N or Fig N references
        pattern = re.compile(
            rf"(?:Figure|Fig\.?)\s+{fig_id}\b", re.IGNORECASE
        )
        if not pattern.search(body):
            missing.append(key)

    return {"passed": len(missing) == 0, "missing": missing}


# ===========================================================================
# H8: Number Fingerprint
# ===========================================================================

def _extract_table_definition_numbers(
    text_by_page: dict[int, str],
    registry: dict,
) -> set[str]:
    """Extract numbers from pages where Tables are defined (source of truth)."""
    numbers: set[str] = set()
    for key, entry in registry.items():
        if entry.get("type") != "Table":
            continue
        def_page = entry.get("definition_page")
        if def_page is None:
            continue
        page_text = text_by_page.get(def_page, "")
        for n in _NUMBER_RE.findall(page_text):
            numbers.add(n)
    return numbers


def _extract_md_table_numbers(md: str) -> list[dict]:
    """Extract numbers from each markdown table in the body.

    Returns list of dicts: [{table_index, numbers}].
    """
    body = _extract_body(md)
    lines = body.split("\n")
    tables: list[dict] = []
    current_block: list[str] = []
    table_idx = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            current_block.append(stripped)
        else:
            if len(current_block) >= 3:
                block_text = "\n".join(current_block)
                nums = _NUMBER_RE.findall(block_text)
                tables.append({
                    "table_index": table_idx,
                    "numbers": nums,
                })
                table_idx += 1
            current_block = []

    # Handle trailing table
    if len(current_block) >= 3:
        block_text = "\n".join(current_block)
        nums = _NUMBER_RE.findall(block_text)
        tables.append({
            "table_index": table_idx,
            "numbers": nums,
        })

    return tables


def _number_matches(a: str, b: str, tolerance: float) -> bool:
    """Check if two number strings match within tolerance."""
    try:
        fa = float(a)
        fb = float(b)
    except ValueError:
        return a == b

    if fa == 0 and fb == 0:
        return True
    if fa == 0 or fb == 0:
        return abs(fa - fb) <= tolerance
    return abs(fa - fb) / max(abs(fa), abs(fb)) <= tolerance


def check_number_fingerprint(
    md: str,
    text_by_page: dict[int, str],
    registry: dict,
    threshold: float = 0.3,
    tolerance: float = 0.15,
) -> dict:
    """Cross-validate numbers between source PDF tables and writer markdown.

    Extract numbers from Table definition pages as fingerprint.
    Extract numbers from Writer's markdown tables.
    >30% untraced = fail.

    Returns ``{passed, untraced_ratio, suspect_tables, ...}``.
    """
    source_numbers = _extract_table_definition_numbers(text_by_page, registry)
    md_tables = _extract_md_table_numbers(md)

    if not md_tables:
        return {
            "passed": True,
            "untraced_ratio": 0.0,
            "suspect_tables": [],
            "detail": "no markdown tables found",
        }

    total_md_numbers = 0
    untraced_count = 0
    suspect_tables: list[int] = []

    for tbl in md_tables:
        tbl_untraced = 0
        for num in tbl["numbers"]:
            total_md_numbers += 1
            # Check if this number is traceable to any source number
            traceable = any(
                _number_matches(num, src, tolerance)
                for src in source_numbers
            )
            if not traceable:
                tbl_untraced += 1
                untraced_count += 1
        # If majority of numbers in this table are untraced, mark suspect
        if tbl["numbers"] and tbl_untraced / len(tbl["numbers"]) > 0.5:
            suspect_tables.append(tbl["table_index"])

    if total_md_numbers == 0:
        untraced_ratio = 0.0
    else:
        untraced_ratio = untraced_count / total_md_numbers

    return {
        "passed": untraced_ratio <= threshold,
        "untraced_ratio": round(untraced_ratio, 4),
        "suspect_tables": suspect_tables,
        "total_md_numbers": total_md_numbers,
        "untraced_count": untraced_count,
    }


# ===========================================================================
# Orchestrator
# ===========================================================================

def run_hard_gates(
    merged_md: str,
    coverage_checklist: dict,
    core_figures: list[dict],
    text_by_page: dict[int, str] | None,
    registry: dict | None,
) -> dict:
    """Run all 8 gates. Return summary dict.

    When ``text_by_page`` or ``registry`` is None, gates H4, H7, and H8
    are skipped (marked ``{"passed": True, "skipped": True}``).

    Returns ``{passed, results, failed}`` where *failed* lists gate names
    that did not pass.
    """
    _SKIPPED: dict[str, Any] = {"passed": True, "skipped": True}

    results: dict[str, dict] = {}

    # H1: Baselines Format
    results["H1"] = check_baselines_format(merged_md)

    # H2: Structural Coverage
    results["H2"] = check_structural_coverage(merged_md, coverage_checklist)

    # H3: Character Floors
    results["H3"] = check_char_floors(merged_md)

    # H4: Table Count — requires registry
    if registry is not None:
        results["H4"] = check_table_count(merged_md, registry)
    else:
        results["H4"] = dict(_SKIPPED)

    # H5: TL;DR Numbers
    results["H5"] = check_tldr_numbers(merged_md)

    # H6: Heading Levels
    results["H6"] = check_heading_levels(merged_md)

    # H7: Core Figures Referenced — requires core_figures AND text_by_page
    if text_by_page is not None and core_figures:
        results["H7"] = check_core_figures_referenced(merged_md, core_figures)
    else:
        results["H7"] = dict(_SKIPPED)

    # H8: Number Fingerprint — requires text_by_page AND registry
    if text_by_page is not None and registry is not None:
        results["H8"] = check_number_fingerprint(
            merged_md, text_by_page, registry,
        )
    else:
        results["H8"] = dict(_SKIPPED)

    failed = [name for name, res in results.items() if not res.get("passed")]
    return {
        "passed": len(failed) == 0,
        "results": results,
        "failed": failed,
    }
