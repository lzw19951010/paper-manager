"""Tests for core figure image extraction."""
from __future__ import annotations

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
