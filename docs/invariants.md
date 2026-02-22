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

- Interpretations are layered on top of evidence.
Why: avoids rewriting evidence when analysis changes.

- Claims are reified as nodes (`Claim`) and linked to `Source`.
Why: allows competing hypotheses, traceability, and confidence/status metadata.

- Ingest operations must be idempotent (`MERGE`-based).
Why: reruns are expected in development and should not duplicate graph entities.

- IDs are deterministic for all model entities.
Why: stable references across reruns, adapters, and downstream exports.
