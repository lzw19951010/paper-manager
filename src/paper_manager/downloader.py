"""arxiv paper downloader with rate limiting."""
from __future__ import annotations

import logging
import time
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

_last_request_time: float = 0.0
_RATE_LIMIT_SECONDS = 3.0
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}


def _rate_limit() -> None:
    """Sleep until at least 3 seconds have elapsed since the last request."""
    global _last_request_time
    elapsed = time.monotonic() - _last_request_time
    if elapsed < _RATE_LIMIT_SECONDS:
        time.sleep(_RATE_LIMIT_SECONDS - elapsed)
    _last_request_time = time.monotonic()


def parse_arxiv_id(url: str) -> str:
    """Extract an arxiv ID from a URL or bare ID string.

    Supported formats:
        https://arxiv.org/abs/2301.00001
        https://arxiv.org/pdf/2301.00001
        https://arxiv.org/pdf/2301.00001v2
        https://huggingface.co/papers/2301.00001
        2301.00001  (bare ID)

    Version suffixes (e.g. v2) are stripped.

    Raises:
        ValueError: If the format is not recognised.
    """
    url = url.strip()

    # Bare ID: digits.digits with optional version suffix
    import re
    bare_pattern = re.compile(r"^(\d{4}\.\d{4,5})(v\d+)?$")
    m = bare_pattern.match(url)
    if m:
        return m.group(1)

    # arxiv.org abs or pdf URL
    arxiv_pattern = re.compile(
        r"https?://(?:export\.)?arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(v\d+)?(?:\.pdf)?$"
    )
    m = arxiv_pattern.match(url)
    if m:
        return m.group(1)

    # huggingface.co papers URL
    hf_pattern = re.compile(
        r"https?://huggingface\.co/papers/(\d{4}\.\d{4,5})(v\d+)?$"
    )
    m = hf_pattern.match(url)
    if m:
        return m.group(1)

    raise ValueError(
        f"Unrecognised arxiv URL or ID format: {url!r}. "
        "Expected formats: https://arxiv.org/abs/<id>, "
        "https://arxiv.org/pdf/<id>[v<n>], "
        "https://huggingface.co/papers/<id>, or bare ID like 2301.00001."
    )


def fetch_metadata(arxiv_id: str) -> dict:
    """Fetch paper metadata from the arxiv abs page (HTML, no API).

    Scrapes citation meta tags from the arxiv abstract page, which is the
    same as visiting the page in a browser — no API rate limits apply.

    Args:
        arxiv_id: A bare arxiv ID such as "2301.00001".

    Returns:
        dict with keys: arxiv_id, title, authors, date, abstract,
        categories, url.

    Raises:
        ValueError: If the arxiv ID is not found.
        httpx.HTTPError: On unrecoverable HTTP errors.
    """
    import re as _re

    abs_url = f"https://arxiv.org/abs/{arxiv_id}"

    last_exc: Exception | None = None
    for attempt in range(3):
        if attempt > 0:
            time.sleep(2 ** attempt)
        try:
            response = httpx.get(abs_url, timeout=30.0, headers=_HEADERS, follow_redirects=True)
            if response.status_code == 404:
                raise ValueError(f"arxiv ID not found: {arxiv_id!r}")
            response.raise_for_status()
            break
        except httpx.TimeoutException as exc:
            last_exc = exc
            continue
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code >= 500:
                last_exc = exc
                continue
            raise
    else:
        raise last_exc  # type: ignore[misc]

    html = response.text

    # Extract from <meta name="citation_*"> tags
    def _meta(name: str) -> str:
        m = _re.search(rf'<meta\s+name="{name}"\s+content="(.+?)"', html)
        return m.group(1).strip() if m else ""

    def _meta_all(name: str) -> list[str]:
        return [m.strip() for m in _re.findall(rf'<meta\s+name="{name}"\s+content="(.+?)"', html)]

    title = _meta("citation_title")
    if not title:
        raise ValueError(f"Could not extract title for arxiv ID: {arxiv_id!r}")

    # Authors come as "Last, First" — convert to "First Last"
    raw_authors = _meta_all("citation_author")
    authors = []
    for a in raw_authors:
        parts = [p.strip() for p in a.split(",", 1)]
        if len(parts) == 2:
            authors.append(f"{parts[1]} {parts[0]}")
        else:
            authors.append(a)

    date_raw = _meta("citation_date")  # "YYYY/MM/DD"
    date = date_raw.replace("/", "-") if date_raw else ""

    # Abstract from the page
    abs_match = _re.search(
        r'<blockquote class="abstract[^"]*">\s*<span[^>]*>Abstract:</span>\s*(.*?)</blockquote>',
        html,
        _re.DOTALL,
    )
    abstract = ""
    if abs_match:
        abstract = _re.sub(r"<[^>]+>", "", abs_match.group(1)).strip()
        abstract = " ".join(abstract.split())

    # Categories from primary-subject span
    categories = []
    cat_match = _re.search(r'<span class="primary-subject">([^<]+)</span>', html)
    if cat_match:
        # Extract short code like "cs.CL" from "Computation and Language (cs.CL)"
        code_match = _re.search(r"\(([^)]+)\)", cat_match.group(1))
        if code_match:
            categories.append(code_match.group(1))

    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "date": date,
        "abstract": abstract,
        "categories": categories,
        "url": abs_url,
    }


def download_pdf(arxiv_id: str, output_dir: Path) -> Path:
    """Download a paper PDF from arxiv via streaming.

    Uses arxiv.org/pdf/ (same as browser) with streaming download to handle
    large PDFs reliably. Verifies the downloaded file starts with %PDF.

    Args:
        arxiv_id: A bare arxiv ID such as "2301.00001".
        output_dir: Directory in which to save the PDF.

    Returns:
        Path to the saved PDF file.

    Raises:
        ValueError: On 404 (not found) or 410 (withdrawn).
        httpx.HTTPError: On other unrecoverable HTTP errors.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
    dest = output_dir / f"{arxiv_id}.pdf"

    last_exc: Exception | None = None
    for attempt in range(3):
        if attempt > 0:
            time.sleep(2 ** attempt)
        try:
            with httpx.stream(
                "GET", pdf_url, timeout=120.0, follow_redirects=True, headers=_HEADERS,
            ) as response:
                if response.status_code == 404:
                    raise ValueError(f"Paper {arxiv_id} not found (404)")
                if response.status_code == 410:
                    raise ValueError(f"Paper {arxiv_id} has been withdrawn (410)")
                if response.status_code >= 500:
                    last_exc = httpx.HTTPStatusError(
                        f"Server error {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                    continue
                response.raise_for_status()

                with open(dest, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=65536):
                        f.write(chunk)

            # Verify it's a valid PDF
            with open(dest, "rb") as f:
                header = f.read(5)
            if header != b"%PDF-":
                logger.warning("Downloaded file does not look like a PDF, retrying...")
                dest.unlink(missing_ok=True)
                last_exc = RuntimeError("Downloaded file is not a valid PDF")
                continue

            size_mb = dest.stat().st_size / (1024 * 1024)
            logger.info("Downloaded %s (%.1f MB)", dest.name, size_mb)
            return dest
        except ValueError:
            raise
        except httpx.TimeoutException as exc:
            last_exc = exc
            dest.unlink(missing_ok=True)
            continue
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code >= 500:
                last_exc = exc
                continue
            raise
    else:
        raise last_exc  # type: ignore[misc]

    return dest  # unreachable, satisfies type checker
