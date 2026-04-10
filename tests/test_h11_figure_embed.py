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
