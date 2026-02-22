from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Work:
    work_id: str
    title: str


@dataclass(slots=True, frozen=True)
class Edition:
    edition_id: str
    work_id: str
    label: str | None = None
    version: str | None = None


@dataclass(slots=True, frozen=True)
class Segment:
    segment_id: str
    edition_id: str
    text: str
    position: int
    ref: str | None = None


@dataclass(slots=True, frozen=True)
class Token:
    token_id: str
    segment_id: str
    surface: str
    position: int
    normalized: str | None = None


@dataclass(slots=True, frozen=True)
class Form:
    form_id: str
    orthography: str
    language: str


@dataclass(slots=True, frozen=True)
class Lemma:
    lemma_id: str
    headword: str
    language: str
    pos: str | None = None


@dataclass(slots=True, frozen=True)
class MorphAnalysis:
    analysis_id: str
    analyzer: str
    confidence: float
    pos: str
    is_ambiguous: bool
    analyzer_version: str | None = None
    created_at: str | None = None
    supersedes: str | None = None
    is_active: bool = True


@dataclass(slots=True, frozen=True)
class Feature:
    key: str
    value: str
    lemma_guess: str | None = None


@dataclass(slots=True, frozen=True)
class Claim:
    claim_id: str
    type: str
    statement: str
    confidence: float | None = None
    status: str | None = None


@dataclass(slots=True, frozen=True)
class Source:
    source_id: str
    citekey: str
    title: str
    year: int | None = None
    authors: tuple[str, ...] | None = None
    url: str | None = None
