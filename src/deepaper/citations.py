"""Citation fetcher and formatter using OpenAlex (default) or Semantic Scholar (optional)."""
from __future__ import annotations

import logging
import re
import time
from datetime import date

import httpx

logger = logging.getLogger(__name__)

_last_request_time: float = 0.0
_RATE_LIMIT_SECONDS = 3.0  # Semantic Scholar: 3s
_OA_RATE_LIMIT_SECONDS = 1.0  # OpenAlex: 1s (generous limit)
_SS_BASE = "https://api.semanticscholar.org/graph/v1"
_OA_BASE = "https://api.openalex.org"
_MAX_RETRIES = 3
_OA_MAILTO = "deepaper@users.noreply.github.com"
_OA_USER_AGENT = f"deepaper/0.1 (mailto:{_OA_MAILTO})"


def _rate_limit(seconds: float = _RATE_LIMIT_SECONDS) -> None:
    """Sleep until at least `seconds` have elapsed since the last request."""
    global _last_request_time
    elapsed = time.monotonic() - _last_request_time
    if elapsed < seconds:
        time.sleep(seconds - elapsed)
    _last_request_time = time.monotonic()


def _get_api_key() -> str:
    """Get Semantic Scholar API key from config or environment."""
    import os
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    if key:
        return key
    try:
        from deepaper.config import load_config
        config = load_config()
        return config.semantic_scholar_api_key
    except Exception:
        return ""


def _get_with_retry(url: str, params: dict | None = None, headers: dict | None = None,
                    rate_limit_seconds: float = _RATE_LIMIT_SECONDS) -> httpx.Response:
    """GET request with retry on 429 rate limit errors."""
    req_headers = headers or {}
    for attempt in range(_MAX_RETRIES):
        _rate_limit(rate_limit_seconds)
        resp = httpx.get(url, params=params, headers=req_headers, timeout=30.0)
        if resp.status_code == 429:
            wait = 5 * (attempt + 1)
            logger.info("Rate limited (429), retrying in %ds...", wait)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


def _empty_result(source: str = "openalex") -> dict:
    return {
        "total_citations": 0,
        "citing_papers": [],
        "fetch_date": date.today().isoformat(),
        "source": source,
    }


def _reconstruct_abstract(inverted_index: dict | None) -> str:
    """Reconstruct plain text abstract from OpenAlex's abstract_inverted_index."""
    if not inverted_index or not isinstance(inverted_index, dict):
        return ""
    word_positions: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


def _fetch_openalex(arxiv_id: str, limit: int = 50) -> dict:
    """Fetch citing papers from OpenAlex API (no API key required).

    Args:
        arxiv_id: A bare arxiv ID such as "2301.00001".
        limit: Maximum number of citing papers to return.

    Returns:
        Dict with keys: total_citations, citing_papers, fetch_date, source.
    """
    fetch_date = date.today().isoformat()
    oa_headers = {"User-Agent": _OA_USER_AGENT}

    # Step 1: resolve arxiv ID to OpenAlex work via DOI
    # OpenAlex doesn't support `arxiv:ID` as a direct lookup key,
    # but arxiv papers have DOIs in the format `10.48550/arXiv.{id}`
    try:
        arxiv_doi = f"10.48550/arXiv.{arxiv_id}"
        paper_url = f"{_OA_BASE}/works/doi:{arxiv_doi}"
        resp = _get_with_retry(
            paper_url,
            params={"mailto": _OA_MAILTO, "select": "id,display_name,cited_by_count"},
            headers=oa_headers,
            rate_limit_seconds=_OA_RATE_LIMIT_SECONDS,
        )
        paper_data = resp.json()
        total_citations: int = paper_data.get("cited_by_count", 0) or 0
        openalex_id = paper_data.get("id", "")
        # OpenAlex IDs are full URLs like "https://openalex.org/W2741809807"
        # The filter API wants just the short form e.g. "W2741809807"
        if openalex_id.startswith("https://openalex.org/"):
            openalex_short = openalex_id[len("https://openalex.org/"):]
        else:
            openalex_short = openalex_id
    except Exception as exc:
        logger.warning("Failed to fetch paper details from OpenAlex: %s", exc)
        return _empty_result("openalex")

    if not openalex_short:
        logger.warning("OpenAlex returned no ID for arxiv:%s", arxiv_id)
        return _empty_result("openalex")

    # Step 2: fetch citing works sorted by citation count
    try:
        citing_url = f"{_OA_BASE}/works"
        params = {
            "filter": f"cites:{openalex_short}",
            "sort": "cited_by_count:desc",
            "per_page": min(limit, 200),
            "select": "id,display_name,authorships,publication_year,cited_by_count,ids,primary_location,abstract_inverted_index",
            "mailto": _OA_MAILTO,
        }
        resp = _get_with_retry(
            citing_url,
            params=params,
            headers=oa_headers,
            rate_limit_seconds=_OA_RATE_LIMIT_SECONDS,
        )
        citing_data = resp.json()
    except Exception as exc:
        logger.warning("Failed to fetch citing papers from OpenAlex: %s", exc)
        return _empty_result("openalex")

    citing_papers: list[dict] = []
    for work in citing_data.get("results", []):
        # Author string: "LastName et al." or single last name
        authorships = work.get("authorships") or []
        if authorships:
            first_author = authorships[0].get("author", {}).get("display_name", "")
            last_name = first_author.split()[-1] if first_author else ""
            if len(authorships) > 1:
                author_str = f"{last_name} et al."
            else:
                author_str = last_name
        else:
            author_str = ""

        # Extract arxiv ID from ids dict if present
        ids = work.get("ids") or {}
        arxiv_url = ids.get("arxiv") or ""
        paper_arxiv_id: str | None = None
        if arxiv_url:
            paper_arxiv_id = arxiv_url.rstrip("/").split("/")[-1]

        # URL: prefer arxiv, then primary_location
        primary_loc = work.get("primary_location") or {}
        landing_page = primary_loc.get("landing_page_url") or ""
        url = arxiv_url or landing_page or ""

        # Reconstruct abstract from inverted index
        abstract = _reconstruct_abstract(work.get("abstract_inverted_index"))

        citing_papers.append({
            "title": work.get("display_name") or "",
            "authors": author_str,
            "year": work.get("publication_year"),
            "citation_count": work.get("cited_by_count") or 0,
            "is_influential": False,  # not available from OpenAlex
            "url": url,
            "arxiv_id": paper_arxiv_id,
            "abstract": abstract,
        })

    return {
        "total_citations": total_citations,
        "citing_papers": citing_papers[:limit],
        "fetch_date": fetch_date,
        "source": "openalex",
    }


def _fetch_semantic_scholar(arxiv_id: str, limit: int = 50) -> dict:
    """Fetch citing papers from Semantic Scholar API (requires API key).

    Args:
        arxiv_id: A bare arxiv ID such as "2301.00001".
        limit: Maximum number of citing papers to return (sorted by citation count).

    Returns:
        Dict with keys: total_citations, citing_papers, fetch_date, source.
    """
    fetch_date = date.today().isoformat()

    api_key = _get_api_key()
    ss_headers: dict = {}
    if api_key:
        ss_headers["x-api-key"] = api_key

    # Step 1: fetch total citation count for the paper itself
    try:
        paper_url = f"{_SS_BASE}/paper/ArXiv:{arxiv_id}"
        resp = _get_with_retry(
            paper_url,
            params={"fields": "citationCount"},
            headers=ss_headers,
            rate_limit_seconds=_RATE_LIMIT_SECONDS,
        )
        paper_data = resp.json()
        total_citations: int = paper_data.get("citationCount", 0) or 0
    except Exception as exc:
        logger.warning("Failed to fetch paper details from Semantic Scholar: %s", exc)
        return _empty_result("semantic_scholar")

    # Step 2: fetch citing papers (paginate up to 1000)
    citing_papers: list[dict] = []
    offset = 0
    page_size = 100

    while True:
        try:
            citations_url = f"{_SS_BASE}/paper/ArXiv:{arxiv_id}/citations"
            params = {
                "fields": "title,authors,year,citationCount,externalIds,url,isInfluential,abstract",
                "limit": page_size,
                "offset": offset,
            }
            resp = _get_with_retry(
                citations_url,
                params=params,
                headers=ss_headers,
                rate_limit_seconds=_RATE_LIMIT_SECONDS,
            )
            page = resp.json()
        except Exception as exc:
            logger.warning("Failed to fetch citations from Semantic Scholar: %s", exc)
            if not citing_papers:
                return _empty_result("semantic_scholar")
            break

        items = page.get("data", [])
        for item in items:
            paper = item.get("citingPaper", {})
            if not paper:
                continue

            # Build author string: "Last Name et al." or single author name
            authors_raw = paper.get("authors") or []
            if authors_raw:
                first = authors_raw[0].get("name", "")
                last_name = first.split()[-1] if first else ""
                if len(authors_raw) > 1:
                    author_str = f"{last_name} et al."
                else:
                    author_str = last_name
            else:
                author_str = ""

            # Extract arxiv ID from externalIds
            external_ids = paper.get("externalIds") or {}
            paper_arxiv_id = external_ids.get("ArXiv") or external_ids.get("arxiv")

            citing_papers.append({
                "title": paper.get("title") or "",
                "authors": author_str,
                "year": paper.get("year"),
                "citation_count": paper.get("citationCount") or 0,
                "is_influential": bool(item.get("isInfluential")),
                "url": paper.get("url") or "",
                "arxiv_id": paper_arxiv_id,
                "abstract": paper.get("abstract") or "",
            })

        # Check if there are more pages
        next_offset = page.get("next")
        if next_offset is None or len(items) < page_size or offset + page_size >= 1000:
            break
        offset = next_offset if isinstance(next_offset, int) else offset + page_size

    # Sort by citation count descending, take top `limit`
    citing_papers.sort(key=lambda p: p["citation_count"], reverse=True)
    citing_papers = citing_papers[:limit]

    return {
        "total_citations": total_citations,
        "citing_papers": citing_papers,
        "fetch_date": fetch_date,
        "source": "semantic_scholar",
    }


def fetch_citing_papers(arxiv_id: str, limit: int = 50) -> dict:
    """Fetch citing papers, using OpenAlex by default or Semantic Scholar when configured.

    OpenAlex requires no API key and is the default data source.
    If a Semantic Scholar API key is configured (via SEMANTIC_SCHOLAR_API_KEY env var
    or the config file), Semantic Scholar is used instead.

    Args:
        arxiv_id: A bare arxiv ID such as "2301.00001".
        limit: Maximum number of citing papers to return (sorted by citation count).

    Returns:
        Dict with keys: total_citations, citing_papers, fetch_date, source.
        On API failure, returns the empty fallback structure with a warning logged.
    """
    if _get_api_key():
        logger.info("Using Semantic Scholar (API key configured)")
        return _fetch_semantic_scholar(arxiv_id, limit)
    logger.info("Using OpenAlex (default, no API key required)")
    return _fetch_openalex(arxiv_id, limit)


_RELATION_LABELS = {
    "core": "🔴 核心续作",
    "extension": "🟠 扩展应用",
    "application": "🟡 组件引用",
    "survey": "🔵 综述收录",
    "casual": "",
}


def format_descendants_section(citation_data: dict) -> str:
    """Format citation data into a markdown descendants section.

    Filters out 0-citation papers. Shows relation classification
    and one-line analysis for papers with abstracts.

    Args:
        citation_data: Dict returned by fetch_citing_papers().

    Returns:
        Markdown string for the descendants section.
    """
    fetch_date = citation_data.get("fetch_date", date.today().isoformat())
    total = citation_data.get("total_citations", 0)
    citing_papers = citation_data.get("citing_papers", [])
    source = citation_data.get("source", "openalex")
    source_label = "OpenAlex" if source == "openalex" else "Semantic Scholar"

    # Filter out 0-citation papers
    citing_papers = [p for p in citing_papers if p.get("citation_count", 0) > 0]

    if not citing_papers:
        return (
            f"#### 后代 (Descendants) — 基于引用分析\n\n"
            f"> 截至 {fetch_date}，本文共被引用 **{total:,}** 次"
            f"（数据来源：{source_label}）\n\n"
            f"暂无高影响力引用论文。\n"
        )

    header = (
        f"#### 后代 (Descendants) — 基于引用分析\n\n"
        f"> 截至 {fetch_date}，本文共被引用 **{total:,}** 次"
        f"（数据来源：{source_label}）\n\n"
    )

    # Split into core/meaningful vs casual
    core_papers = [p for p in citing_papers if p.get("relation") in ("core", "extension", "application")]
    other_papers = [p for p in citing_papers if p.get("relation") not in ("core", "extension", "application")]

    parts = [header]

    # Core follow-ups with detailed analysis
    if core_papers:
        parts.append("##### 核心后续工作\n")
        for p in core_papers:
            title = p.get("title") or ""
            authors = p.get("authors") or ""
            year = p.get("year") or "—"
            cite_count = p.get("citation_count") or 0
            relation = _RELATION_LABELS.get(p.get("relation", ""), "")
            one_line = p.get("one_line") or ""

            parts.append(f"- **{title}** ({authors}, {year}) — 被引 {cite_count:,}")
            if relation:
                parts.append(f"  - {relation}")
            if one_line:
                parts.append(f"  - {one_line}")
        parts.append("")

    # Remaining notable papers as compact table
    table_papers = [p for p in other_papers if p.get("relation") != "casual"]
    # Also include papers without analysis (no abstract)
    unanalyzed = [p for p in citing_papers if not p.get("relation") and p not in core_papers]
    table_papers.extend(unanalyzed)

    if table_papers:
        parts.append("##### 其他引用\n")
        parts.append("| 论文 | 年份 | 被引数 | 关系 |")
        parts.append("|------|------|--------|------|")
        for p in table_papers[:15]:
            title = p.get("title") or ""
            if len(title) > 50:
                title = title[:48] + "..."
            authors = p.get("authors") or ""
            year = p.get("year") or "—"
            cite_count = p.get("citation_count") or 0
            relation = _RELATION_LABELS.get(p.get("relation", ""), "—")
            paper_cell = f"{title} ({authors})" if authors else title
            parts.append(f"| {paper_cell} | {year} | {cite_count:,} | {relation} |")
        parts.append("")

    # Year-by-year trend
    year_counts: dict[int, int] = {}
    for p in citing_papers:
        y = p.get("year")
        if y and isinstance(y, int):
            year_counts[y] = year_counts.get(y, 0) + 1

    if year_counts:
        sorted_years = sorted(year_counts.keys())
        trend_parts = [f"{y}: {year_counts[y]:,} 篇" for y in sorted_years]
        parts.append("##### 引用趋势\n- " + " | ".join(trend_parts))

    return "\n".join(parts) + "\n"


def enrich_mechanism_transfer(mechanism_transfer_md: str, citation_data: dict) -> str:
    """Replace or append the descendants subsection in mechanism_transfer markdown.

    Finds '#### 后代 (Descendants)' in the text and replaces everything from
    there until the next '####' or '**创新增量**'. If no descendants section
    is found, appends before '**创新增量**'.

    Args:
        mechanism_transfer_md: Existing mechanism_transfer markdown content.
        citation_data: Dict returned by fetch_citing_papers().

    Returns:
        Updated markdown string with the real citation data injected.
    """
    new_section = format_descendants_section(citation_data)

    # Pattern: from #### 后代 until next #### or **创新增量** (non-greedy)
    descendants_pattern = re.compile(
        r"(#### 后代.*?)(?=\n#### |\n\*\*创新增量\*\*|\Z)",
        re.DOTALL,
    )

    if descendants_pattern.search(mechanism_transfer_md):
        return descendants_pattern.sub(new_section.rstrip("\n"), mechanism_transfer_md, count=1)

    # No descendants section found — insert before **创新增量** if present
    innovation_pattern = re.compile(r"(\*\*创新增量\*\*)", re.DOTALL)
    if innovation_pattern.search(mechanism_transfer_md):
        return innovation_pattern.sub(
            new_section + r"\1",
            mechanism_transfer_md,
            count=1,
        )

    # Append at end
    return mechanism_transfer_md.rstrip("\n") + "\n\n" + new_section
