# Ingest Overview

Related docs: [Adapter Contract](adapter-contract.md), [Hávamál Notes](havamal-source-notes.md), [Schema](../schema.md), [Invariants](../invariants.md)

## Pipeline Overview

1. Read source input (JSON/text/export).
2. Adapt source into deterministic structural units (`Work`, `Edition`, iterable `Segment` records, token stream).
3. Normalize/tokenize with declared policy.
4. Persist via MERGE-based graph writes.
5. Run sanity checks (counts, duplication checks).

## Source Adapters

- Adapters isolate source-specific parsing.
- Core graph persistence should not depend on source-specific field names.
- Adapter output must be deterministic and reproducible.

## Canonical vs Export

- Canonical system of record: Neo4j graph.
- JSON/source files are inputs and optional exports, not the authoritative interpretation layer.
- Any derived exports should be regeneratable from graph + deterministic adapters.

## Sprint 1 Reality

- Implemented ingest for `data/Hávamál1.json`.
- Core ingested layers used in production path: `Work`, `Edition`, `Segment`, `Token`, `Form`.
