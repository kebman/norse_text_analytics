# Commit conventions

This repo uses a lightweight prefix convention to keep history readable and make it easy to skim `git log` and `git blame`.

## Format

```

:

(optional body)

- bullets for notable changes
    
- include constraints/invariants changes explicitly
    

```

### Examples

- `infra: add dockerized Neo4j with env-driven auth`
- `graph: add schema constraints and indexes`
- `ingest: add Hávamál JSON adapter with stable IDs`
- `morph: add MorphAnalysis nodes and feature model`
- `docs: document ID conventions and canonical queries`
- `chore: ignore pycache and add dev tooling`

## Prefixes

### Core
- **infra:** runtime environment, Docker, services, secrets handling, CI
- **graph:** database schema, indexes/constraints, repo/driver layer, query primitives
- **ingest:** source adapters, parsing, normalization, tokenization, import pipelines
- **morph:** morphological analysis, features, inflection models, analyzers
- **etym:** etymology/cognates, claims/sources, lineage relationships
- **align:** alignment between editions/translations (segment/token alignment)
- **query:** canonical queries, report scripts, performance fixes for queries
- **docs:** documentation only (schema/vision/query cookbook/dev logs)

### Maintenance
- **chore:** housekeeping (formatting, ignores, tooling) with no behavioral change
- **test:** tests only
- **fix:** bug fix (use when not better represented by a domain prefix)
- **refactor:** code moves/reshapes with no behavior change

## Rules

1. One commit = one concern (avoid mixing infra + logic + docs).
2. Changes to the graph model must be accompanied by doc updates:
   - `docs/schema.md`
   - `docs/invariants.md` (if rules changed)
   - relevant `docs/queries/*.md` if query patterns changed
3. Ingestion must remain rerunnable:
   - deterministic IDs
   - `MERGE` patterns
   - avoid destructive updates to evidence nodes (Token/Segment).
4. Anything with secrets:
   - must be env-driven
   - never commit `.env`
   - only commit `.env.example`.

## Tagging

Use annotated tags for sprint milestones.

Recommended formats:

- `sprint-<n>` (e.g. `sprint-1`)
- `s<n>-YYYY-MM-DD` (e.g. `s1-2026-02-22`)

Tag after a green, runnable state:
- `docker compose up -d`
- schema applied
- ingest succeeds
- basic counts verified in Neo4j.
