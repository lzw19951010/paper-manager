"""Visual registry, core figure detection, and paper profiling.

Pure-text analysis of paper structure — no LLM involvement.
Provides the foundation for quality gate validation by scanning
extracted text for tables, figures, sections, and equations.
"""

from __future__ import annotations

import re
from collections import defaultdict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_CORE = 3  # hard cap on core figures
CORE_RATIO_CAP = 0.20  # at most 20% of figures can be core
MIN_CORE_SCORE = 3  # minimum score to qualify

# Regex for Table/Figure/Fig./Fig references in running text
_REF_RE = re.compile(
    r"(?:Table|Figure|Fig\.?)\s+(\d+)", re.IGNORECASE
)

# Regex for captions: "Table N:" or "Figure N:" or "Fig. N:" at line start
_CAPTION_RE = re.compile(
    r"^(Table|Figure|Fig\.?)\s+(\d+)\s*:", re.MULTILINE | re.IGNORECASE
)

# Section heading patterns (line starts with known heading, possibly numbered)
_SECTION_RE = re.compile(
    r"^(?:\d+\.?\s+)?"
    r"(Introduction|Related\s+Work|Background|Method(?:ology|s)?|"
    r"Approach|Experiments?|Results?|Discussion|Conclusion|"
    r"Abstract|Appendix|References|Evaluation)",
    re.MULTILINE | re.IGNORECASE,
)

# Subsection heading: numbered like "3.1 Something" or "3.1. Something"
_SUBSECTION_RE = re.compile(
    r"^(\d+\.\d+\.?\s+\S.*)$", re.MULTILINE
)

# Numbered equations: (1), (2), etc. on a line
_EQUATION_RE = re.compile(r"\((\d+)\)")

# Canonical section name mapping
_SECTION_ALIASES: dict[str, str] = {
    "introduction": "Introduction",
    "related work": "Related Work",
    "background": "Background",
    "method": "Method",
    "methods": "Method",
    "methodology": "Method",
    "approach": "Method",
    "experiment": "Experiments",
    "experiments": "Experiments",
    "result": "Experiments",
    "results": "Experiments",
    "evaluation": "Experiments",
    "discussion": "Discussion",
    "conclusion": "Conclusion",
    "abstract": "Abstract",
    "appendix": "Appendix",
    "references": "References",
}


def _normalize_type(raw: str) -> str:
    """Normalize 'Fig', 'Fig.', 'fig', etc. to 'Figure'."""
    lowered = raw.lower().rstrip(".")
    if lowered == "fig":
        return "Figure"
    return raw.capitalize()


def _canonical_section(name: str) -> str:
    """Map a detected section name to its canonical form."""
    return _SECTION_ALIASES.get(name.lower().strip(), name.strip().title())


# ===========================================================================
# Part 1: build_visual_registry + verify_registry_completeness
# ===========================================================================

def build_visual_registry(text_by_page: dict[int, str]) -> dict:
    """Scan text for Table/Figure references and captions.

    Returns dict keyed by "Table_N" / "Figure_N" with fields:
      type, id, pages (set of pages where referenced),
      definition_page, has_caption.
    """
    registry: dict[str, dict] = {}

    for page, text in text_by_page.items():
        # Find all references
        for m in _REF_RE.finditer(text):
            raw_type = m.group(0).split()[0]  # "Table", "Figure", "Fig.", etc.
            norm_type = _normalize_type(raw_type)
            num = int(m.group(1))
            key = f"{norm_type}_{num}"
            if key not in registry:
                registry[key] = {
                    "type": norm_type,
                    "id": num,
                    "pages": set(),
                    "definition_page": None,
                    "has_caption": False,
                }
            registry[key]["pages"].add(page)

        # Find captions
        for m in _CAPTION_RE.finditer(text):
            raw_type = m.group(1)
            norm_type = _normalize_type(raw_type)
            num = int(m.group(2))
            key = f"{norm_type}_{num}"
            if key not in registry:
                registry[key] = {
                    "type": norm_type,
                    "id": num,
                    "pages": set(),
                    "definition_page": None,
                    "has_caption": False,
                }
            registry[key]["definition_page"] = page
            registry[key]["has_caption"] = True
            registry[key]["pages"].add(page)

    # Convert page sets to sorted lists for JSON-friendliness
    for entry in registry.values():
        entry["pages"] = sorted(entry["pages"])

    return registry


def verify_registry_completeness(registry: dict) -> list[str]:
    """Check for numbering gaps and missing captions.

    Returns a list of human-readable issue strings.
    """
    issues: list[str] = []

    # Group by type
    by_type: dict[str, list[int]] = defaultdict(list)
    for key, entry in registry.items():
        by_type[entry["type"]].append(entry["id"])

    # Check numbering gaps
    for vtype, ids in by_type.items():
        if not ids:
            continue
        ids_sorted = sorted(ids)
        expected = set(range(1, max(ids_sorted) + 1))
        missing = expected - set(ids_sorted)
        for m in sorted(missing):
            issues.append(f"{vtype} {m} is missing (gap in numbering)")

    # Check missing captions
    for key, entry in registry.items():
        if not entry["has_caption"]:
            issues.append(
                f"{entry['type']} {entry['id']} has no caption"
            )

    return issues


# ===========================================================================
# Part 2: identify_core_figures + extract_figure_contexts
# ===========================================================================

def identify_core_figures(
    registry: dict,
    text_by_page: dict[int, str],
    total_pages: int,
) -> list[dict]:
    """Score each Figure on 5 signals and return top core figures.

    Signals (1 point each):
      - ref_count >= 3
      - in_intro (definition in first 20% of pages)
      - early_position (definition in first 30% of pages)
      - caption > 80 chars
      - id <= 2

    Anti-inflation: MAX_CORE=3, ratio cap 20%, competitive ranking, min score 3.
    """
    figures = {k: v for k, v in registry.items() if v["type"] == "Figure"}
    if not figures:
        return []

    intro_cutoff = max(1, int(total_pages * 0.20))
    early_cutoff = max(1, int(total_pages * 0.30))

    scored: list[dict] = []
    for key, entry in figures.items():
        ref_count = len(entry["pages"])
        def_page = entry.get("definition_page") or min(entry["pages"])

        # Determine caption length
        caption_text = _find_caption_text(text_by_page, entry["type"], entry["id"])
        caption_len = len(caption_text) if caption_text else 0

        score = 0
        if ref_count >= 3:
            score += 1
        if def_page <= intro_cutoff:
            score += 1
        if def_page <= early_cutoff:
            score += 1
        if caption_len > 80:
            score += 1
        if entry["id"] <= 2:
            score += 1

        scored.append({
            "key": key,
            "id": entry["id"],
            "page": def_page,
            "score": score,
            "ref_count": ref_count,
        })

    # Filter by minimum score
    scored = [s for s in scored if s["score"] >= MIN_CORE_SCORE]

    # Competitive ranking: sort by score desc, then ref_count desc
    scored.sort(key=lambda x: (-x["score"], -x["ref_count"]))

    # Apply budget: min(MAX_CORE, 20% of total figures)
    budget = min(MAX_CORE, max(1, int(len(figures) * CORE_RATIO_CAP)))
    budget = min(budget, MAX_CORE)

    return scored[:budget]


def _find_caption_text(
    text_by_page: dict[int, str], vtype: str, vid: int
) -> str | None:
    """Extract the caption text for a given visual element."""
    # Build patterns that match the various forms
    patterns = []
    if vtype == "Figure":
        patterns = [
            re.compile(
                rf"^(?:Figure|Fig\.?)\s+{vid}\s*:\s*(.+)$",
                re.MULTILINE | re.IGNORECASE,
            ),
        ]
    else:
        patterns = [
            re.compile(
                rf"^{vtype}\s+{vid}\s*:\s*(.+)$",
                re.MULTILINE | re.IGNORECASE,
            ),
        ]

    for _page, text in text_by_page.items():
        for pat in patterns:
            m = pat.search(text)
            if m:
                return m.group(1).strip()
    return None


MAX_CORE_TABLES = 8
MIN_CORE_TABLE_SCORE = 2


def identify_core_tables(
    registry: dict,
    text_by_page: dict[int, str],
    total_pages: int,
) -> list[dict]:
    """Score each Table and return top core tables as candidates.

    Scoring mirrors identify_core_figures:
      - ref_count >= 3  (+3 points)
      - ref_count >= 2  (+1 point, if not already +3)
      - in first 30% of pages  (+2 points)
      - caption length > 80 chars  (+1 point)

    Budget: max(3, min(8, num_tables * 0.2))
    Returns: [{key, id, page, score, ref_count}] sorted by score desc.
    """
    tables = {k: v for k, v in registry.items() if v["type"] == "Table"}
    if not tables:
        return []

    early_cutoff = max(1, int(total_pages * 0.30))

    scored: list[dict] = []
    for key, entry in tables.items():
        ref_count = len(entry["pages"])
        def_page = entry.get("definition_page") or min(entry["pages"])

        caption_text = _find_caption_text(text_by_page, "Table", entry["id"])
        caption_len = len(caption_text) if caption_text else 0

        score = 0
        if ref_count >= 3:
            score += 3
        elif ref_count >= 2:
            score += 1
        if def_page <= early_cutoff:
            score += 2
        if caption_len > 80:
            score += 1

        scored.append({
            "key": key,
            "id": entry["id"],
            "page": def_page,
            "score": score,
            "ref_count": ref_count,
        })

    scored = [s for s in scored if s["score"] >= MIN_CORE_TABLE_SCORE]
    scored.sort(key=lambda x: (-x["score"], -x["ref_count"]))

    budget = max(3, min(MAX_CORE_TABLES, int(len(tables) * 0.2)))
    return scored[:budget]


def extract_figure_contexts(
    text_by_page: dict[int, str],
    core_figures: list[dict],
) -> dict:
    """For each core figure, extract caption + referencing paragraphs.

    Returns dict keyed by "Figure_N" with:
      caption: str
      references: list[str]  (paragraphs that mention the figure)
    """
    result: dict[str, dict] = {}

    for cf in core_figures:
        key = cf["key"]
        fig_id = cf["id"]
        caption = _find_caption_text(text_by_page, "Figure", fig_id) or ""

        # Collect paragraphs that reference this figure
        ref_pattern = re.compile(
            rf"(?:Figure|Fig\.?)\s+{fig_id}\b", re.IGNORECASE
        )
        references: list[str] = []
        for _page, text in text_by_page.items():
            # Split into paragraphs (by blank lines or newlines)
            paragraphs = re.split(r"\n\s*\n|\n", text)
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if ref_pattern.search(para):
                    # Skip if this is the caption line itself
                    caption_check = re.match(
                        rf"^(?:Figure|Fig\.?)\s+{fig_id}\s*:",
                        para, re.IGNORECASE,
                    )
                    if not caption_check:
                        references.append(para)

        result[key] = {
            "caption": caption,
            "references": references,
        }

    return result


# ===========================================================================
# Part 3: compute_paper_profile + build_coverage_checklist
# ===========================================================================

def compute_paper_profile(
    text_by_page: dict[int, str],
    visual_registry: dict,
) -> dict:
    """Extract structural profile of a paper.

    Returns dict with:
      total_pages, total_chars, section_chars, subsection_headings,
      num_tables, num_figures, num_equations.
    """
    if not text_by_page:
        return {
            "total_pages": 0,
            "total_chars": 0,
            "section_chars": {},
            "subsection_headings": [],
            "num_tables": 0,
            "num_figures": 0,
            "num_equations": 0,
        }

    total_chars = sum(len(t) for t in text_by_page.values())

    # Detect sections and compute section_chars
    section_chars = _compute_section_chars(text_by_page)

    # Collect subsection headings
    subsection_headings: list[str] = []
    for text in text_by_page.values():
        for m in _SUBSECTION_RE.finditer(text):
            subsection_headings.append(m.group(1).strip())

    # Count visuals from registry
    num_tables = sum(
        1 for v in visual_registry.values() if v["type"] == "Table"
    )
    num_figures = sum(
        1 for v in visual_registry.values() if v["type"] == "Figure"
    )

    # Count equations
    equation_ids: set[int] = set()
    for text in text_by_page.values():
        for m in _EQUATION_RE.finditer(text):
            equation_ids.add(int(m.group(1)))
    num_equations = len(equation_ids)

    return {
        "total_pages": len(text_by_page),
        "total_chars": total_chars,
        "section_chars": section_chars,
        "subsection_headings": subsection_headings,
        "num_tables": num_tables,
        "num_figures": num_figures,
        "num_equations": num_equations,
    }


def _compute_section_chars(text_by_page: dict[int, str]) -> dict[str, int]:
    """Detect sections and compute approximate character counts for each.

    Concatenates all pages, finds section headings, and measures text
    between consecutive headings.
    """
    # Build full text preserving page boundaries
    full_text = "\n".join(
        text_by_page[p] for p in sorted(text_by_page.keys())
    )

    # Find all section heading positions
    headings: list[tuple[int, str]] = []
    for m in _SECTION_RE.finditer(full_text):
        raw_name = m.group(1).strip()
        canonical = _canonical_section(raw_name)
        headings.append((m.start(), canonical))

    if not headings:
        return {}

    # Sort by position
    headings.sort(key=lambda x: x[0])

    section_chars: dict[str, int] = {}
    for i, (pos, name) in enumerate(headings):
        if i + 1 < len(headings):
            end = headings[i + 1][0]
        else:
            end = len(full_text)
        chars = end - pos
        # Accumulate if same canonical name appears multiple times
        section_chars[name] = section_chars.get(name, 0) + chars

    return section_chars


def build_coverage_checklist(
    text_by_page: dict[int, str],
    registry: dict,
    subsection_headings: list[str],
) -> dict:
    """Build a checklist of structural elements declared in the paper.

    Each entry has: source (where detected) and match_pattern or match_text.
    Returns dict keyed by a descriptive label.
    """
    checklist: dict[str, dict] = {}

    if not text_by_page and not registry and not subsection_headings:
        return checklist

    # Subsection headings
    for heading in subsection_headings:
        label = f"subsection:{heading}"
        checklist[label] = {
            "source": "subsection_heading",
            "match_text": heading,
        }

    # Numbered equations
    equation_ids: set[int] = set()
    for text in text_by_page.values():
        for m in _EQUATION_RE.finditer(text):
            equation_ids.add(int(m.group(1)))
    for eid in sorted(equation_ids):
        label = f"equation:{eid}"
        checklist[label] = {
            "source": "equation",
            "match_pattern": rf"\({eid}\)",
        }

    # Tables with captions
    for key, entry in registry.items():
        if entry["type"] == "Table" and entry["has_caption"]:
            checklist[f"table:{key}"] = {
                "source": "table_caption",
                "match_pattern": rf"Table\s+{entry['id']}\s*:",
            }

    # Core figures (figures with captions)
    for key, entry in registry.items():
        if entry["type"] == "Figure" and entry["has_caption"]:
            checklist[f"figure:{key}"] = {
                "source": "figure_caption",
                "match_pattern": rf"(?:Figure|Fig\.?)\s+{entry['id']}\s*:",
            }

    return checklist
