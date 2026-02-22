# Raw Sources and Adapters

Related docs: [Ingest Overview](ingest-overview.md), [Adapter Contract](adapter-contract.md), [IDs and References](../ids-and-references.md), [Data Model Philosophy](../data-model/philosophy.md)

## RawSource

`RawSource` captures acquisition metadata for non-JSON and messy inputs:

- `source_id`
- `kind` (for example `html`, `plain_text`, `tei_xml`, `pdf_ocr`)
- `origin` (URL or file path)
- `retrieved_at`
- `notes`

This metadata is provenance for adapter runs; it does not replace `Edition` metadata in the graph model.

## Adapter Pipeline Stages

Adapters should expose deterministic outputs via four stages:

1. Acquire -> raw text
- Pull/read source from URL or local path.
- Keep `RawSource` metadata for traceability.

2. Segment -> segment records
- Produce segment records with `text` and ordinal position.
- Keep `ref` when source references exist (chapter/line/etc).

3. Tokenize -> token records with offsets
- Produce tokens per segment with `surface`, `position`.
- Include `char_start`/`char_end` when available.

4. Normalize -> normalized token + variant links
- Populate `normalized` token value.
- Preserve `surface` and map normalization as graph links (not destructive replacement).

## Adapter Output Contract

Aligned with [Adapter Contract](adapter-contract.md):

- Work metadata:
  - `work_id`, `title`
- Edition metadata:
  - `edition_id`, `source_label`, `language_stage`
  - optional `date_start`, `date_end`
- Iterable segments:
  - `{ref, text, verse?, strophe?, line?, ordinal}`
- Iterable tokens per segment:
  - `{surface, normalized, position, char_start?, char_end?}`

## Deterministic IDs for Messy Sources

When the source has no stable references:

- `segment_id` = `<edition_id>:segment:<ordinal>`
- `token_id` = `<segment_id>:token:<token_index>`

If source refs are available, keep them in `Segment.ref` and still keep IDs deterministic.

## Stability Tradeoff

For messy corpora, stable evidence is more important than perfect first-pass structure.

- Prefer ordinal-based stable IDs over unstable heuristic IDs.
- Keep reruns idempotent even if segmentation is coarse.
- Improve segmentation/tokenization later without mutating prior evidence nodes.

## Play Mode Guidance

Play mode may use rough segmentation/tokenization for rapid exploration.

- Allowed: imperfect boundaries, partial refs, incomplete offsets.
- Required: provenance (`RawSource` + edition/source metadata) and deterministic IDs.
- Result: data stays auditable and can be refined by later adapters without losing traceability.
