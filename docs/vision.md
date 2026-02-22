# Vision

Related docs: [Index](index.md), [Schema](schema.md), [Invariants](invariants.md), [Word Lineage Queries](queries/word-lineage.md)

## System Goals

- Build a graph-native evidence model for Norse text analytics.
- Keep text evidence (`Segment`, `Token`) separate from interpretation (`Form`, `Lemma`, `Claim`).
- Support rerunnable, deterministic ingest pipelines.
- Enable historical-to-modern language lineage exploration (Old Norse to Bokmål/Nynorsk).

## Primary User Story

- As a researcher, I can look up a Norse word and trace attestations across sources over time.
- I can inspect orthographic variants and interpretation layers.
- I can branch into modern descendants (Bokmål/Nynorsk), including competing scholarly claims.

## Secondary User Stories

- As an engineer, I can add a new source adapter without changing core model invariants.
- As an analyst, I can run canonical Cypher queries for counts, frequency, and lineage checks.

## Non-Goals (Current Scope)

- Production-grade lemmatization.
- Automatic token-to-token translation alignment.
- Finalized historical chronology for all sources.
- UI product features; focus is backend model and ingest reliability.
