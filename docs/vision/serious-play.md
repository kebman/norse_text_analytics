# Serious Play

Related docs: [Data Model Philosophy](../data-model/philosophy.md), [Invariants](../invariants.md), [Query Acceptance Tests](../query-acceptance-tests.md)

## What "Serious Play" Means Here

This project is exploratory-first: we ingest quickly, inspect patterns early, and refine models in public. "Serious" means every exploratory step is still traceable and upgradeable to academic-grade output without rewriting history.

## Modes

### A) Play Mode

- Fast ingestion is allowed.
- Rough segmentation is allowed.
- Low-confidence annotations are allowed.
- Missing sources are allowed temporarily, but must be explicitly flagged (for example unpublished/manual status).

### B) Publish Mode

- Provenance is strict and auditable.
- Claims require citations (`Source` records linked via `SUPPORTED_BY`).
- Edition dates/ranges are documented and reviewable.
- Conflicts are modeled explicitly (`CONTRADICTS`, competing claims), not hidden.

## Rules of Engagement

- Evidence is immutable once ingested: `Token`, `Segment`, and `Edition` are treated as stable evidence records.
- Interpretation is layered and versioned: `MorphAnalysis` and `Claim` are append-only interpretation layers.
- No destructive edits for interpretation changes: supersede or deactivate old interpretations; keep history queryable.

## Upgrade Path Checklist

- Add proper `Source` entries for provisional/manual claims.
- Add or verify `Edition` date ranges and notes.
- Replace placeholder analyses with analyzer-tagged analyses (`analyzer`, `analyzer_version`, timestamped outputs).
- Mark claims as `disputed`/`accepted` with supporting citations.

## Acceptance Standard

A dataset is publish-ready when acceptance queries stay green, provenance is complete for claims, and interpretation history remains auditable without destructive rewrites.
