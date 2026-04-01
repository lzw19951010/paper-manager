"""Extractor validation: StructCheck and Auditor.

Validates Extractor output before it reaches Writers.
StructCheck ensures all required sections exist with adequate content.
Auditor ensures page coverage is not missing large segments.
"""

from __future__ import annotations

import re
from collections import Counter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS = [
    "META",
    "MAIN_RESULTS",
    "ABLATIONS",
    "HYPERPARAMETERS",
    "FORMULAS",
    "DATA_COMPOSITION",
    "EVAL_CONFIG",
    "TRAINING_COSTS",
    "DESIGN_DECISIONS",
    "RELATED_WORK",
    "BASELINES",
]

# Absolute floor minimum characters per section (used when paper_profile
# does not provide enough information for dynamic thresholds).
_ABSOLUTE_FLOOR: dict[str, int] = {
    "META": 50,
    "MAIN_RESULTS": 100,
    "ABLATIONS": 60,
    "HYPERPARAMETERS": 60,
    "FORMULAS": 40,
    "DATA_COMPOSITION": 60,
    "EVAL_CONFIG": 60,
    "TRAINING_COSTS": 40,
    "DESIGN_DECISIONS": 60,
    "RELATED_WORK": 80,
    "BASELINES": 60,
}

# Regex to split notes on "## HEADER" lines
_SECTION_HEADER_RE = re.compile(r"^##\s+(\S+)", re.MULTILINE)

# Common English stop-words to exclude from distinctive-word extraction
_STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "as", "was", "are", "be",
    "this", "that", "which", "not", "have", "has", "had", "been", "will",
    "can", "do", "does", "did", "we", "our", "they", "their", "its",
    "also", "than", "more", "each", "all", "some", "such", "other",
    "these", "those", "about", "into", "over", "after", "between",
    "through", "where", "when", "how", "what", "who", "no", "if",
    "up", "out", "one", "two", "may", "would", "could", "should",
    "page", "content",  # generic filler from text_by_page patterns
})


# ===========================================================================
# parse_notes_sections
# ===========================================================================

def parse_notes_sections(notes: str) -> dict[str, str]:
    """Parse Extractor notes into sections by ``## HEADER``.

    Returns a dict mapping section names to their content strings.
    Content is the text between the current header and the next header
    (or end of string).
    """
    sections: dict[str, str] = {}
    matches = list(_SECTION_HEADER_RE.finditer(notes))

    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(notes)
        sections[name] = notes[start:end].strip()

    return sections


# ===========================================================================
# struct_check
# ===========================================================================

def _compute_thresholds(
    total_pages: int,
    paper_profile: dict,
) -> dict[str, int]:
    """Derive per-section minimum char thresholds.

    Uses ``paper_profile`` fields (``section_chars``, ``num_tables``,
    ``num_equations``, ``total_pages``) to scale expectations dynamically.
    Falls back to absolute floor values when the profile is empty.
    """
    section_chars: dict[str, int] = paper_profile.get("section_chars", {})
    num_tables = paper_profile.get("num_tables", 0)
    num_equations = paper_profile.get("num_equations", 0)
    pp_pages = paper_profile.get("total_pages", total_pages)

    # Dynamic scaling factor based on page count (longer papers -> higher bar)
    page_factor = max(1.0, pp_pages / 10.0)

    thresholds: dict[str, int] = {}
    for sec in REQUIRED_SECTIONS:
        floor = _ABSOLUTE_FLOOR.get(sec, 50)

        # If the profile has section_chars, use a fraction of the paper's
        # own section length as the threshold (notes should capture at
        # least ~5% of the original section's char count).
        dynamic = 0
        if section_chars:
            # Map some extractor sections to paper sections heuristically
            mapping = {
                "META": "Abstract",
                "MAIN_RESULTS": "Experiments",
                "RELATED_WORK": "Related Work",
                "ABLATIONS": "Experiments",
                "EVAL_CONFIG": "Experiments",
                "DESIGN_DECISIONS": "Method",
                "BASELINES": "Experiments",
            }
            paper_sec = mapping.get(sec)
            if paper_sec and paper_sec in section_chars:
                dynamic = int(section_chars[paper_sec] * 0.05)

        # Boost certain sections when paper has many tables/equations
        if sec == "FORMULAS" and num_equations > 5:
            dynamic = max(dynamic, int(floor * 1.5))
        if sec in ("MAIN_RESULTS", "ABLATIONS") and num_tables > 5:
            dynamic = max(dynamic, int(floor * 1.3))

        # Scale by page factor but never below absolute floor
        threshold = max(floor, int(dynamic * page_factor))
        # Cap so thresholds stay reasonable
        threshold = max(floor, min(threshold, floor * 10))
        thresholds[sec] = threshold

    return thresholds


def struct_check(
    notes: str,
    total_pages: int,
    paper_profile: dict,
) -> dict:
    """Check that all 11 required sections exist with sufficient content.

    Parameters
    ----------
    notes:
        Raw Extractor notes text with ``## SECTION`` headers.
    total_pages:
        Number of pages in the source paper.
    paper_profile:
        Output from ``registry.compute_paper_profile`` (may be empty).

    Returns
    -------
    dict with keys:
        passed (bool), missing_sections (list[str]),
        thin_sections (list[str]), thresholds (dict[str, int]).
    """
    sections = parse_notes_sections(notes)
    thresholds = _compute_thresholds(total_pages, paper_profile or {})

    missing: list[str] = []
    thin: list[str] = []

    for sec in REQUIRED_SECTIONS:
        if sec not in sections:
            missing.append(sec)
        else:
            content = sections[sec]
            min_chars = thresholds.get(sec, _ABSOLUTE_FLOOR.get(sec, 50))
            if len(content) < min_chars:
                thin.append(sec)

    passed = len(missing) == 0 and len(thin) == 0

    return {
        "passed": passed,
        "missing_sections": missing,
        "thin_sections": thin,
        "thresholds": thresholds,
    }


# ===========================================================================
# audit_coverage
# ===========================================================================

def _extract_distinctive_words(text: str, min_len: int = 4) -> set[str]:
    """Extract distinctive (non-stop, long-enough) words from text."""
    words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
    return {
        w for w in words
        if len(w) >= min_len and w not in _STOP_WORDS
    }


def audit_coverage(
    text_by_page: dict[int, str],
    notes: str,
    total_pages: int,
    chunk_size: int = 10,
) -> dict:
    """Check that notes cover content from all page segments.

    Divides pages into chunks of ``chunk_size``, extracts distinctive
    words per chunk, and checks how many appear in the notes.

    A segment with < 30% word overlap is considered uncovered.

    Parameters
    ----------
    text_by_page:
        Mapping from page number to extracted text.
    notes:
        The Extractor notes to audit.
    total_pages:
        Total page count (used to determine segment boundaries).
    chunk_size:
        Number of pages per segment.

    Returns
    -------
    dict with keys:
        coverage_ratio (float), uncovered_segments (list[tuple[int,int]]).
    """
    if not text_by_page or not notes:
        return {"coverage_ratio": 0.0, "uncovered_segments": []}

    pages = sorted(text_by_page.keys())
    notes_words = _extract_distinctive_words(notes)

    # Build segments
    segments: list[tuple[int, int]] = []
    for start in range(pages[0], pages[-1] + 1, chunk_size):
        end = min(start + chunk_size - 1, pages[-1])
        segments.append((start, end))

    covered_count = 0
    uncovered: list[tuple[int, int]] = []

    for seg_start, seg_end in segments:
        # Concatenate text for pages in this segment
        seg_text = " ".join(
            text_by_page[p]
            for p in range(seg_start, seg_end + 1)
            if p in text_by_page
        )
        seg_words = _extract_distinctive_words(seg_text)

        if not seg_words:
            # Empty segment counts as covered (nothing to miss)
            covered_count += 1
            continue

        overlap = len(seg_words & notes_words)
        ratio = overlap / len(seg_words)

        if ratio >= 0.30:
            covered_count += 1
        else:
            uncovered.append((seg_start, seg_end))

    coverage_ratio = covered_count / len(segments) if segments else 0.0

    return {
        "coverage_ratio": coverage_ratio,
        "uncovered_segments": uncovered,
    }
