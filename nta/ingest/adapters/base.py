from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Protocol
from typing import Sequence
from typing import runtime_checkable


@dataclass(slots=True, frozen=True)
class RawSource:
    """Metadata for unstructured source acquisition."""

    source_id: str
    kind: str
    origin: str
    retrieved_at: datetime | None = None
    notes: str | None = None


@dataclass(slots=True, frozen=True)
class AdapterWorkMetadata:
    work_id: str
    title: str


@dataclass(slots=True, frozen=True)
class AdapterEditionMetadata:
    edition_id: str
    title: str
    source_label: str | None = None
    language: str | None = None
    language_stage: str | None = None
    date_start: int | None = None
    date_end: int | None = None
    normalization_policy: str | None = None
    version: str | None = None


@dataclass(slots=True, frozen=True)
class AdapterTokenRecord:
    surface: str
    normalized: str
    position: int
    token_id: str | None = None
    char_start: int | None = None
    char_end: int | None = None


@dataclass(slots=True, frozen=True)
class AdapterSegmentRecord:
    text: str
    ordinal: int
    tokens: Sequence[AdapterTokenRecord]
    ref: str | None = None
    segment_id: str | None = None
    verse: str | None = None
    strophe: str | None = None
    line: str | None = None


@dataclass(slots=True, frozen=True)
class AdapterOutput:
    """Deterministic output emitted by any source adapter."""

    work: AdapterWorkMetadata
    edition: AdapterEditionMetadata
    segments: Sequence[AdapterSegmentRecord] = field(default_factory=tuple)


@runtime_checkable
class SourceAdapter(Protocol):
    """Protocol for adapter implementations."""

    def adapt(self, raw_source: RawSource) -> AdapterOutput:
        ...


class BaseSourceAdapter(ABC):
    """Optional abstract base class for concrete adapters."""

    @abstractmethod
    def adapt(self, raw_source: RawSource) -> AdapterOutput:
        raise NotImplementedError

