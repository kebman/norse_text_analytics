# Adapter Contract

Related docs: [Ingest Overview](ingest-overview.md), [IDs and References](../ids-and-references.md), [Invariants](../invariants.md)

## Purpose

Define a language-agnostic output contract for any source adapter so ingest remains consistent.

## Required Adapter Output

- Work metadata:
  - `work_id`, `title`
- Edition metadata:
  - `edition_id`, `title`, optional source metadata fields
- Iterable segments where each item includes:
  - `segment_id` (deterministic)
  - `ref` (human readable)
  - `text`
  - structural fields when available (`verse`, `strophe`, `line_index`, `position`)
- Token stream per segment where each token includes:
  - `token_id` (deterministic)
  - `surface`
  - `normalized`
  - `position`
  - `form_id` + `orthography` + `language`

## Determinism Rule

Raw sources may be messy or inconsistent, but adapter output must be deterministic for identical input.

## Validation Expectations

- No empty token surfaces after normalization.
- Stable segment/token counts across reruns.
- No duplicate IDs emitted within one adapter run.
