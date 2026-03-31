"""Paper analysis response parsing."""
from __future__ import annotations

import logging
import re

import yaml

logger = logging.getLogger(__name__)


def parse_analysis_response(response: str) -> tuple[dict, str]:
    """Parse Claude's markdown response into (frontmatter_dict, body_str).

    Tolerantly extracts YAML frontmatter. If parsing fails, returns empty
    dict and the full response as body — the note is still readable.
    """
    frontmatter: dict = {}
    body = response

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", response, re.DOTALL)
    if match:
        yaml_text = match.group(1)
        body = match.group(2)
        try:
            parsed = yaml.safe_load(yaml_text)
            if isinstance(parsed, dict):
                frontmatter = parsed
        except yaml.YAMLError as exc:
            logger.warning("YAML frontmatter parse failed (using defaults): %s", exc)

    return frontmatter, body.strip()
