# Language Scope

Related docs: [Language Stages](language-stages.md), [Branching Queries](../queries/branching.md), [Schema](../schema.md)

## Primary Focus

Default project scope is Norse languages and historical stages:

- Old Norse
- Old West Norse / Old East Norse
- Old Norwegian
- Old Icelandic
- Old Danish
- Old Swedish
- Middle Norwegian / Middle Danish / Middle Swedish
- Modern Icelandic
- Faroese
- Norwegian Bokmål / Norwegian Nynorsk
- Swedish
- Danish

This is the default vocabulary and query focus for the current repository.

## Border Area (Supported for Comparison)

Closely related Germanic languages are supported when useful for comparison and contact history:

- Old English
- Middle English (optional)
- Frisian (Old / West)
- Old Saxon (optional contact language)
- Middle Low German (optional contact language)

These are in-bounds when they improve lineage, borrowing, or cognacy analysis.

## Design Principle

The system is language-agnostic by design:

- Source adapters are not language-specific in architecture.
- Stage assignment uses controlled vocabulary, not hardcoded language logic.

Repository defaults target Norse use cases, but data model primitives are reusable.

## How to Add a New Language/Stage

1. Extend controlled vocabulary in [Language Stages](language-stages.md).
2. Set `Edition.language_stage` for ingested sources.
3. Set `Lemma.language_stage` (and keep `language` populated).
4. Add lineage edges between lemmas:
   - `(:Lemma)-[:DERIVES_FROM]->(:Lemma)`
   - `(:Lemma)-[:BORROWED_FROM]->(:Lemma)`
5. Add/update branching queries to include the new stage codes.

## Forkability

To target another language family, minimal required changes are:

- New controlled vocabulary entries for that family/stages.
- New or adapted source adapters for that corpus.
- Seed examples and acceptance queries for lineage/morphology/provenance.

Core graph semantics (evidence vs interpretation vs hypothesis) stay unchanged.

## Dialect Continuum Guidance

For dialect-heavy corpora, represent dialect as an edition/witness dimension first:

- `Edition.dialect_region` (optional)
- `Witness.place` and `Witness.iso_area` (optional)
- `Edition.place` if source-level place is known

Planned optional nodes for richer geolinguistic modeling:

- `(:DialectArea)`
- `(:Place)`

Use these as additive layers; do not overload `language_stage` to encode fine-grained dialect geography.
