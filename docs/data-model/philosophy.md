# Data Model Philosophy

Related docs: [Schema](../schema.md), [Invariants](../invariants.md), [Word Lineage Queries](../queries/word-lineage.md)

This project treats Neo4j as the canonical record and keeps a deliberate split between observed text and human/machine interpretation. The goal is to preserve an exploratory playground feel now while keeping a clean path to publishable, auditable outputs later.

## Epistemic Layers

- Evidence: directly observed textual artifacts from a source ingest (for example `Edition`, `Segment`, `Token`, raw references, line text).
- Interpretation: structured analysis attached to evidence (for example `Form` mapping, `Lemma` assignment, `MorphAnalysis`).
- Reconstruction: modeled historical lineage that is not directly observed in a single token stream (for example `DERIVES_FROM`, `BORROWED_FROM`, etymological structure).
- Hypothesis: explicit, contestable scholarly assertions represented as `Claim` nodes with support and possible contradiction links.
- Normalization: reversible processing choices (token cleanup, orthographic normalization, normalization policy metadata) that improve queryability without replacing evidence.
- Annotation: human or tool-added metadata layered onto evidence/interpretation (POS tags, notes, confidence, manual flags, feature assignments).

## Core Rules

- Evidence is primary; interpretation must not overwrite evidence.
- Interpretation and hypothesis can change over time and must preserve history.
- Competing hypotheses are expected; model them explicitly rather than collapsing to one "truth".
- Normalization is a policy decision, not an evidentiary fact; keep raw forms and normalized forms linked.

## Immutability and Versioning

- `Token` and `Segment` are evidence and immutable once ingested.
- `MorphAnalysis` and `Claim` are append-only and versioned (non-destructive updates).
- If a mapping changes (for example `Form-[:REALIZES]->Lemma`), deactivate prior interpretation (`is_active=false`) and add a new active mapping; do not delete historical edges.

## Provenance Requirements

- Every `Claim` must be traceable to at least one `Source`, or explicitly marked as `"unpublished/manual"` in its provenance metadata.
- Every `MorphAnalysis` must record analyzer identity, analyzer version, and creation timestamp.
- Interpretation updates should preserve who/what assigned them (`assigned_by`) and confidence where available.

## Operating Modes

### Play Mode

- Allows low-confidence claims, partial metadata, and manual notes.
- Useful for exploration, iterative graph design, and rapid source onboarding.
- Must still preserve non-destructive history and basic provenance markers.

### Publish Mode

- Requires source-backed claims (or explicit unpublished designation).
- Requires confidence values and explicit conflict modeling where disagreement exists.
- Requires reproducible queries and deterministic IDs for reruns/audit.

## Practical Standard

- Prefer to ingest first, interpret second, hypothesize third.
- Keep evidence stable, keep interpretation explicit, keep uncertainty modeled.
- Use acceptance queries (see [Word Lineage Queries](../queries/word-lineage.md)) to verify that historical output is traceable back to concrete source evidence.
