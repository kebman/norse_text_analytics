from __future__ import annotations

import re


SURROUNDING_PUNCT: str = " \t\n\r.,;:!?\"'()[]{}<>«»„“”‘’`´…—-"
NORMALIZATION_POLICY_V0: str = "punct_strip_whitespace_collapse_v0"


def normalize_v0(surface: str) -> str:
    """v0 normalization: strip surrounding punctuation and collapse whitespace."""
    normalized = surface.strip(SURROUNDING_PUNCT)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def tokenize_v0(line: str) -> list[str]:
    """v0 tokenization: whitespace split + surrounding punctuation strip."""
    tokens: list[str] = []
    for raw in line.split():
        cleaned = raw.strip(SURROUNDING_PUNCT)
        if cleaned:
            tokens.append(cleaned)
    return tokens

