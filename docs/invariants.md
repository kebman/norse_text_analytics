# Invariants

Related docs: [Schema](schema.md), [IDs and References](ids-and-references.md), [Adapter Contract](ingest/adapter-contract.md)

## Core Invariants

- Every `Token` belongs to exactly one `Segment`.
Why: preserves unambiguous textual provenance for every word occurrence.

- Every `Segment` belongs to one ingest `Edition`.
Why: keeps edition-specific line/token boundaries explicit.

- `Token` identity is stable and tokens are append-only once ingested.
Why: reproducible analytics and safe reruns without identity drift.

- `Token -> INSTANCE_OF_FORM -> Form` is mandatory for ingested tokens.
Why: supports normalization and frequency analysis without losing raw evidence.

- `Token -> HAS_ANALYSIS -> MorphAnalysis` may have multiple edges per token, but one analysis per analyzer id (`analysis_id = token_id:analyzer`).
Why: interpretations evolve and analyzers disagree; evidence should not be overwritten.

- Analyses are layered and replaceable; evidence nodes (`Token`, `Segment`) are not rewritten for new interpretation runs.
Why: keeps provenance stable while allowing incremental model improvement.

- If analyzer differs, create a new `MorphAnalysis`; do not mutate prior analyzer outputs into a single record.
Why: preserves reproducibility and supports side-by-side evaluation.

- Interpretations are layered on top of evidence.
Why: avoids rewriting evidence when analysis changes.

- Claims are reified as nodes (`Claim`) and linked to `Source`.
Why: allows competing hypotheses, traceability, and confidence/status metadata.

- Ingest operations must be idempotent (`MERGE`-based).
Why: reruns are expected in development and should not duplicate graph entities.

- IDs are deterministic for all model entities.
Why: stable references across reruns, adapters, and downstream exports.
