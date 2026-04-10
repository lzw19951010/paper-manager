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

from deepaper.content_checklist import check_content_markers
from deepaper.output_schema import (
    CODE_BLOCKS_EXEMPT_FROM_HEADING_CHECK,
    FRONTMATTER_FIELDS,
    H2_MIN_COVERAGE,
    H8_SKIP_WHEN_NO_DEFINITION_PAGES,
    H8_TOLERANCE,
    H8_UNTRACED_THRESHOLD,
    H12_MIN_BUCKET_COVERAGE,
    HEADING_FORBIDDEN,
)

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
        "passed": coverage >= H2_MIN_COVERAGE,
        "coverage": round(coverage, 4),
        "missing": missing,
    }


# ===========================================================================
# H3: Section Existence (v2)
# ===========================================================================

def check_sections_exist(md: str) -> dict:
    """H3 v2: verify all 4 required section headings exist.

    Replaces char-floor based H3 from v1. In v2 we enforce structural
    presence, not character count. Paper length grows via tables, so a
    section can legitimately be short.
    """
    from deepaper.output_schema import SECTION_ORDER
    body = _extract_body(md)
    missing: list[str] = []
    for sec_name in SECTION_ORDER:
        # Match #### <name> at heading level 4 (or higher)
        pattern = re.compile(rf"^#{{4,6}}\s*{re.escape(sec_name)}\s*$", re.MULTILINE)
        if not pattern.search(body):
            missing.append(sec_name)
    return {
        "passed": len(missing) == 0,
        "missing": missing,
    }


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
    """Check TL;DR contains >= 2 numbers.

    Checks YAML frontmatter ``tldr`` field first. If not found, falls back
    to the body ``##### TL;DR`` section text. This dual-source approach
    matches the output_schema contract where tldr is a required frontmatter
    field, while gracefully handling writers that put it in the body.

    Returns ``{passed, count, source}``.
    """
    min_numbers = FRONTMATTER_FIELDS["tldr"].min_numbers

    # Primary: check frontmatter
    fm = _extract_frontmatter(md)
    tldr = fm.get("tldr", "")
    if isinstance(tldr, str) and tldr.strip():
        numbers = _NUMBER_RE.findall(tldr)
        return {"passed": len(numbers) >= min_numbers, "count": len(numbers), "source": "frontmatter"}

    # Fallback: check body ##### TL;DR section
    body = _extract_body(md)
    tldr_match = re.search(
        r"#{4,5}\s*TL;DR.*?\n(.*?)(?=\n#{4,5}\s|\Z)",
        body,
        re.DOTALL,
    )
    if tldr_match:
        tldr_text = tldr_match.group(1).strip()
        numbers = _NUMBER_RE.findall(tldr_text)
        return {"passed": len(numbers) >= min_numbers, "count": len(numbers), "source": "body"}

    return {"passed": False, "count": 0, "source": "not_found"}


# ===========================================================================
# H6: Heading Levels
# ===========================================================================

def _strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks (```...```) from text."""
    return re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.DOTALL)


def check_heading_levels(md: str) -> dict:
    """Check body only uses h4/h5/h6. Reject h1/h2/h3/h7+.

    Code blocks are exempt — ``# comment`` inside ```python blocks
    is not a heading.

    Returns ``{passed, violations}`` where violations is a list of strings.
    """
    body = _extract_body(md)

    if CODE_BLOCKS_EXEMPT_FROM_HEADING_CHECK:
        body = _strip_code_blocks(body)

    violations: list[str] = []

    for m in _HEADING_RE.finditer(body):
        hashes = m.group(1)
        level = len(hashes)
        if level in HEADING_FORBIDDEN:
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
# H10: Figure Reference Density
# ===========================================================================

def check_figure_ref_density(md: str, core_figures: list[dict] | None) -> dict:
    """Check each core figure is referenced >= 2 times in the body.

    Returns ``{passed, failures, total_figures}``.
    Skipped when *core_figures* is None or empty.
    """
    if not core_figures:
        return {"passed": True, "skipped": True, "reason": "no core_figures"}

    body = _extract_body(md)
    failures: list[dict] = []

    for fig in core_figures:
        fig_id = fig.get("id", "")
        label = f"Figure {fig_id}"
        count = len(re.findall(re.escape(label), body, re.IGNORECASE))
        if count < 2:
            failures.append({"figure": label, "count": count, "required": 2})

    return {
        "passed": len(failures) == 0,
        "failures": failures,
        "total_figures": len(core_figures),
    }


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
    threshold: float = H8_UNTRACED_THRESHOLD,
    tolerance: float = H8_TOLERANCE,
) -> dict:
    """Cross-validate numbers between source PDF tables and writer markdown.

    Extract numbers from Table definition pages as fingerprint.
    Extract numbers from Writer's markdown tables.
    >30% untraced = fail.

    Returns ``{passed, untraced_ratio, suspect_tables, ...}``.
    """
    source_numbers = _extract_table_definition_numbers(text_by_page, registry)

    # Skip when no table definition pages were found — cross-validation
    # is impossible without a source-of-truth number set.
    if H8_SKIP_WHEN_NO_DEFINITION_PAGES and not source_numbers:
        return {
            "passed": True,
            "skipped": True,
            "reason": "no table definition pages found in registry",
            "untraced_ratio": 0.0,
            "suspect_tables": [],
        }

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


# ===========================================================================
# Orchestrator
# ===========================================================================

def run_hard_gates(
    merged_md: str,
    coverage_checklist: dict,
    core_figures: list[dict],
    text_by_page: dict[int, str] | None,
    registry: dict | None,
    paper_profile: dict | None = None,  # NEW — v2.1
) -> dict:
    """Run all hard gates (H1-H12). Return summary dict.

    When ``text_by_page`` or ``registry`` is None, gates H4, H7, and H8
    are skipped (marked ``{"passed": True, "skipped": True}``).
    H2 is permanently skipped (replaced by H12).
    H12 is skipped when ``paper_profile`` is None or has no top_level_sections.

    Returns ``{passed, results, failed}`` where *failed* lists gate names
    that did not pass.
    """
    _SKIPPED: dict[str, Any] = {"passed": True, "skipped": True}

    results: dict[str, dict] = {}

    # H1: Baselines Format
    results["H1"] = check_baselines_format(merged_md)

    # H2: SKIPPED (v2.1 — replaced by H12 section-bucket coverage)
    results["H2"] = dict(_SKIPPED)

    # H3: Section existence (v2 — replaces char-floor check)
    results["H3"] = check_sections_exist(merged_md)

    # H4: Table Count — permanently skipped (tables are now selectively extracted)
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

    # H9: Content Markers
    results["H9"] = check_content_markers(merged_md)

    # H10: Figure Reference Density — requires core_figures
    if core_figures:
        results["H10"] = check_figure_ref_density(merged_md, core_figures)
    else:
        results["H10"] = dict(_SKIPPED)

    # H11: Core Figures Embedded (image syntax) — v2.1
    if core_figures:
        results["H11"] = check_core_figures_embedded(merged_md, core_figures)
    else:
        results["H11"] = dict(_SKIPPED)

    # H12: Section-bucket coverage (v2.1, replaces H2)
    if paper_profile:
        results["H12"] = check_section_bucket_coverage(merged_md, paper_profile)
    else:
        results["H12"] = dict(_SKIPPED)

    failed = [name for name, res in results.items() if not res.get("passed")]
    return {
        "passed": len(failed) == 0,
        "results": results,
        "failed": failed,
    }
