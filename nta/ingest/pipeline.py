from __future__ import annotations

from nta.graph.repo import Neo4jRepository
from nta.ingest.adapters.base import AdapterOutput
from nta.ingest.adapters.base import AdapterTokenRecord
from nta.model import ids
from nta.model.types import Edition
from nta.model.types import Form
from nta.model.types import Segment
from nta.model.types import Token
from nta.model.types import Work


def ingest_adapter_output(
    repo: Neo4jRepository, adapter_output: AdapterOutput
) -> dict[str, int]:
    """
    Persist adapter output using MERGE-based repository writes.

    IDs are deterministic. If adapter records omit IDs, fallback IDs are used:
    - segment_id: <edition_id>:segment:<ordinal>
    - token_id: <segment_id>:token:<position>
    """

    work_meta = adapter_output.work
    edition_meta = adapter_output.edition

    work = Work(work_id=work_meta.work_id, title=work_meta.title)
    edition = Edition(
        edition_id=edition_meta.edition_id,
        work_id=work_meta.work_id,
        label=edition_meta.source_label or edition_meta.title,
        version=edition_meta.version,
    )

    repo.upsert_work(work)
    repo.upsert_edition(edition)
    repo.link_work_edition(work.work_id, edition.edition_id)

    language = edition_meta.language or "UNKNOWN"
    normalization_policy = edition_meta.normalization_policy or "adapter"

    segments_ingested = 0
    tokens_ingested = 0

    for segment_record in adapter_output.segments:
        segment_id = segment_record.segment_id or ids.segment_id(
            edition.edition_id, segment_record.ordinal
        )
        segment = Segment(
            segment_id=segment_id,
            edition_id=edition.edition_id,
            text=segment_record.text,
            position=segment_record.ordinal,
            ref=segment_record.ref or str(segment_record.ordinal),
        )
        repo.upsert_segment(segment)
        repo.link_edition_segment(edition.edition_id, segment_id)
        segments_ingested += 1

        for token_record in segment_record.tokens:
            _ingest_token(
                repo=repo,
                token_record=token_record,
                segment_id=segment_id,
                language=language,
                normalization_policy=normalization_policy,
            )
            tokens_ingested += 1

    return {"segments": segments_ingested, "tokens": tokens_ingested}


def _ingest_token(
    repo: Neo4jRepository,
    token_record: AdapterTokenRecord,
    segment_id: str,
    language: str,
    normalization_policy: str,
) -> None:
    token_id = token_record.token_id or ids.token_id(segment_id, token_record.position)
    normalized = token_record.normalized or token_record.surface

    token = Token(
        token_id=token_id,
        segment_id=segment_id,
        surface=token_record.surface,
        position=token_record.position,
        normalized=normalized,
    )
    surface_form = Form(
        form_id=ids.form_id(language, token_record.surface),
        orthography=token_record.surface,
        language=language,
    )

    repo.upsert_token_and_form(token=token, form=surface_form)
    repo.link_segment_token(segment_id=segment_id, token_id=token_id)

    if normalized != token_record.surface:
        normalized_form = Form(
            form_id=ids.form_id(language, normalized),
            orthography=normalized,
            language=language,
        )
        repo.upsert_form(normalized_form)
        repo.link_form_orthographic_variant(
            form_id=surface_form.form_id,
            normalized_form_id=normalized_form.form_id,
            variant_type="adapter_normalization",
        )
        repo.link_token_normalized_to(
            token_id=token_id,
            form_id=normalized_form.form_id,
            policy=normalization_policy,
        )

