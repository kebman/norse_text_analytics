from __future__ import annotations

import hashlib
import re
import unicodedata


def _normalize(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _digest(*parts: str) -> str:
    joined = "\t".join(_normalize(part) for part in parts)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()


def work_id(title_or_slug: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", _normalize(title_or_slug)).strip("-")
    return slug or "work"


def witness_id(siglum: str) -> str:
    return f"witness:{_digest(siglum)}"


def edition_id(work: str, source: str, version: str) -> str:
    return f"edition:{_digest(work, source, version)}"


def segment_id(edition: str, position: int) -> str:
    return f"{edition}:segment:{position}"


def token_id(segment: str, position: int) -> str:
    return f"{segment}:token:{position}"


def form_id(language: str, orthography: str) -> str:
    return f"form:{_normalize(language)}:{_digest(language, orthography)}"


def lemma_id(language: str, headword: str) -> str:
    return f"lemma:{_normalize(language)}:{_digest(language, headword)}"


def sense_id(lemma: str, sense_key: str) -> str:
    return f"sense:{_digest(lemma, sense_key)}"


def morph_analysis_id(target_id: str, analyzer: str, features: str) -> str:
    return f"morph:{_digest(target_id, analyzer, features)}"


def etymon_id(language: str, form: str, period: str = "") -> str:
    return f"etymon:{_digest(language, form, period)}"


def cognate_set_id(label: str) -> str:
    return f"cset:{_digest(label)}"


def source_id(citekey: str) -> str:
    return f"source:{_digest(citekey)}"


def claim_id(
    claim_type: str, asserts_target_id: str, statement: str, source_id: str
) -> str:
    return f"claim:{_digest(claim_type, asserts_target_id, statement, source_id)}"
