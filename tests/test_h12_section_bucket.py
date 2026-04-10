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
    md = "Section 3.2, p.5 and Table 3, p.15 and p.30 and p.45 and p.1"
    result = check_section_bucket_coverage(md, _profile_5_sections())
    assert result["passed"] is True


def test_h12_80_percent_coverage():
    """4/5 sections referenced (80%) → pass at threshold."""
    md = "p.1 and p.5 and p.15 and p.30"
    result = check_section_bucket_coverage(md, _profile_5_sections())
    assert result["passed"] is True
    assert result["coverage"] >= 0.8


def test_h12_below_threshold():
    """Only 2/5 sections → fail."""
    md = "p.1 and p.5"
    result = check_section_bucket_coverage(md, _profile_5_sections())
    assert result["passed"] is False
    assert len(result["uncovered"]) >= 3


def test_h12_no_sections_in_profile():
    """Missing top_level_sections → skip (pass)."""
    result = check_section_bucket_coverage("any text", {})
    assert result["passed"] is True
    assert result.get("skipped") is True


def test_h12_figure_page_ref():
    """Page refs like p.30 should satisfy the Experiments bucket (26-40)."""
    md = "See results on p.30"
    profile = _profile_5_sections()
    result = check_section_bucket_coverage(md, profile)
    # Only Experiments bucket should be covered (p.30 is in 26-40)
    assert "Experiments" not in result.get("uncovered", [])
