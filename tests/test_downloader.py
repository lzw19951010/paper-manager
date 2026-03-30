"""Tests for paper_manager.downloader."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from paper_manager.downloader import download_pdf, fetch_metadata, parse_arxiv_id

# ---------------------------------------------------------------------------
# Sample HTML returned by the arxiv abs page
# ---------------------------------------------------------------------------
SAMPLE_ABS_HTML = """\
<html><head>
<meta name="citation_title" content="Test Paper: A Survey of Testing">
<meta name="citation_author" content="Smith, Alice">
<meta name="citation_author" content="Jones, Bob">
<meta name="citation_date" content="2023/01/01">
</head><body>
<blockquote class="abstract mathjax">
<span class="descriptor">Abstract:</span> This paper surveys testing methodologies in depth.
</blockquote>
<span class="primary-subject">Software Engineering (cs.SE)</span>
</body></html>
"""

EMPTY_ABS_HTML = """\
<html><head><title>404 Not Found</title></head><body></body></html>
"""


# ---------------------------------------------------------------------------
# parse_arxiv_id
# ---------------------------------------------------------------------------

def test_parse_arxiv_id_abs_url():
    assert parse_arxiv_id("https://arxiv.org/abs/2301.00001") == "2301.00001"


def test_parse_arxiv_id_pdf_url():
    assert parse_arxiv_id("https://arxiv.org/pdf/2301.00001v2") == "2301.00001"


def test_parse_arxiv_id_hf_url():
    assert parse_arxiv_id("https://huggingface.co/papers/2301.00001") == "2301.00001"


def test_parse_arxiv_id_bare():
    assert parse_arxiv_id("2301.00001") == "2301.00001"


def test_parse_arxiv_id_invalid():
    with pytest.raises(ValueError, match="Unrecognised arxiv URL"):
        parse_arxiv_id("https://google.com")


# ---------------------------------------------------------------------------
# fetch_metadata
# ---------------------------------------------------------------------------

def _make_httpx_response(text: str, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


def test_fetch_metadata_parses_html():
    resp = _make_httpx_response(SAMPLE_ABS_HTML)

    with patch("httpx.get", return_value=resp):
        meta = fetch_metadata("2301.00001")

    assert meta["arxiv_id"] == "2301.00001"
    assert meta["title"] == "Test Paper: A Survey of Testing"
    assert meta["authors"] == ["Alice Smith", "Bob Jones"]
    assert meta["date"] == "2023-01-01"
    assert "surveys testing" in meta["abstract"]
    assert "cs.SE" in meta["categories"]
    assert meta["url"] == "https://arxiv.org/abs/2301.00001"


def test_fetch_metadata_raises_on_empty_response():
    resp = _make_httpx_response(EMPTY_ABS_HTML)

    with patch("httpx.get", return_value=resp):
        with pytest.raises(ValueError, match="Could not extract title"):
            fetch_metadata("9999.99999")


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

def test_rate_limiter_enforces_delay():
    """When less than 3 seconds have elapsed, sleep should be called."""
    import paper_manager.downloader as dl

    # Simulate last request happening 1 second ago (monotonic time)
    fake_now = 1000.0
    fake_last = fake_now - 1.0  # only 1 second elapsed → need ~2 more seconds

    with patch("paper_manager.downloader._last_request_time", fake_last), \
         patch("time.monotonic", side_effect=[fake_now, fake_now + 2.0]), \
         patch("time.sleep") as mock_sleep:
        dl._rate_limit()

    mock_sleep.assert_called_once()
    sleep_arg = mock_sleep.call_args[0][0]
    assert 1.9 <= sleep_arg <= 2.1, f"Expected ~2.0s sleep, got {sleep_arg}"


# ---------------------------------------------------------------------------
# download_pdf
# ---------------------------------------------------------------------------

def _make_stream_response(content: bytes, status_code: int = 200):
    """Build a mock context manager for httpx.stream."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.raise_for_status = MagicMock()
    resp.iter_bytes = MagicMock(return_value=[content])
    resp.__enter__ = lambda s: resp
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_download_pdf_saves_file(tmp_path: Path):
    fake_pdf_bytes = b"%PDF-1.4 fake content"
    stream_resp = _make_stream_response(fake_pdf_bytes)

    with patch("httpx.stream", return_value=stream_resp):
        result = download_pdf("2301.00001", tmp_path / "pdfs")

    assert result == tmp_path / "pdfs" / "2301.00001.pdf"
    assert result.exists()
    assert result.read_bytes() == fake_pdf_bytes


def test_download_pdf_raises_on_404(tmp_path: Path):
    stream_resp = _make_stream_response(b"", status_code=404)

    with patch("httpx.stream", return_value=stream_resp):
        with pytest.raises(ValueError, match="not found \\(404\\)"):
            download_pdf("2301.00001", tmp_path)


def test_download_pdf_raises_on_410(tmp_path: Path):
    stream_resp = _make_stream_response(b"", status_code=410)

    with patch("httpx.stream", return_value=stream_resp):
        with pytest.raises(ValueError, match="withdrawn \\(410\\)"):
            download_pdf("2301.00001", tmp_path)
