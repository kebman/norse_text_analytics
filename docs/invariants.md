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

- `Token` nodes are immutable evidence.
Why: textual attestations must remain stable across re-analysis.

- `MorphAnalysis` nodes are append-only interpretation records.
Why: enables versioned analyzer history without destructive updates.

- At most one active `MorphAnalysis` should exist per `(Token, analyzer)` at a time.
Why: query semantics stay predictable while still preserving historical analyses.

- Historical `MorphAnalysis` nodes must remain queryable after supersession.
Why: auditing and reproducibility require access to old analyses.

- `Token -> HAS_ANALYSIS -> MorphAnalysis` may have multiple edges per token; analysis identity uses `analysis_id = token_id:analyzer`.
Why: supports multi-analyzer layering while keeping deterministic IDs.

- `Form -> REALIZES -> Lemma` mappings are non-destructive and versioned at the relationship level.
Why: lemma assignments can change with scholarship, but prior interpretations must remain auditable.

- When a `Form`-to-`Lemma` interpretation changes, do not delete old `REALIZES` edges.
Why: deleting history destroys historiography and prevents reproducible interpretation lineage.

- Update pattern for changed mapping: add new `REALIZES {is_active:true}` edge and set prior edge `is_active=false`; optionally attach a `Claim` explaining the change.
Why: keeps one current mapping while preserving previous scholarly states with provenance.

- Interpretations are layered on top of evidence.
Why: avoids rewriting evidence when analysis changes.

- Claims are reified as nodes (`Claim`) and linked to `Source`.
Why: allows competing hypotheses, traceability, and confidence/status metadata.

- Ingest operations must be idempotent (`MERGE`-based).
Why: reruns are expected in development and should not duplicate graph entities.

- IDs are deterministic for all model entities.
Why: stable references across reruns, adapters, and downstream exports.
