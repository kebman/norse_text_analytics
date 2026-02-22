# Schema

Related docs: [Glossary](glossary.md), [Invariants](invariants.md), [IDs and References](ids-and-references.md), [Ingest Overview](ingest/ingest-overview.md)

## Node Types and Key Properties

- `Work`: `work_id`, `title`
- `Witness` (planned): `witness_id`, `type`, `place`, `date_start`, `date_end`, `date_note`, `siglum`, `description`
- `Edition` (canonical dating layer in Sprint 1): `edition_id`, `title`, `language`, `normalization_policy`, `source_label`, `date_start`, `date_end`, `date_approx`, `date_note`, `provenance`, `cover`, `writer`, `version`
- `Segment`: `segment_id`, `verse`, `strophe`, `line_index`, `ref`, `text`, `position`
- `Token`: `token_id`, `surface`, `normalized`, `position`
- `Form`: `form_id`, `orthography`, `language`
- `Lemma`: `lemma_id`, `headword`, `language`, `pos`
- `Sense`: `sense_id`, `gloss`, `definition`
- `MorphAnalysis`: `analysis_id`, `analyzer`, `confidence`, `pos`, `is_ambiguous`
- `Feature`: `key`, `value`, `lemma_guess`
- `Etymon`: `etymon_id`, `form`, `language`, `period`
- `CognateSet`: `set_id`, `label`
- `Claim`: `claim_id`, `type`, `statement`, `confidence`, `status`
- `Source`: `source_id`, `citekey`, `title`, `year`, `authors`, `url`

## Relationship Types and Direction

- `(:Work)-[:HAS_EDITION]->(:Edition)`
- `(:Work)-[:HAS_WITNESS]->(:Witness)`
- `(:Edition)-[:HAS_SEGMENT]->(:Segment)`
- `(:Segment)-[:HAS_TOKEN]->(:Token)`
- `(:Token)-[:INSTANCE_OF_FORM]->(:Form)`
- `(:Token)-[:HAS_ANALYSIS]->(:MorphAnalysis)`
- `(:Form)-[:REALIZES]->(:Lemma)`
- `(:MorphAnalysis)-[:ANALYZES_AS]->(:Lemma)` (optional)
- `(:MorphAnalysis)-[:HAS_FEATURE]->(:Feature)`
- `(:Form)-[:ORTHOGRAPHIC_VARIANT_OF {type}]->(:Form)`
- `(:Token)-[:NORMALIZED_TO {policy}]->(:Form)`
- `(:Claim)-[:SUPPORTED_BY]->(:Source)`
- `(:Claim)-[:ASSERTS]->(:Lemma|:Etymon)`
- `(:Claim)-[:CONTRADICTS]->(:Claim)`
- `(:Lemma)-[:DERIVES_FROM]->(:Etymon|:Lemma)`
- `(:Lemma)-[:IN_COGNATE_SET]->(:CognateSet)`
- `(:Edition)-[:TRANSLATES]->(:Edition)`
- `(:Segment)-[:ALIGNED_TO {method, confidence}]->(:Segment)`

## Token -> Form -> Lemma Separation

- `Token` is immutable textual evidence at a location.
- `Form` groups orthographic/normalization variants across tokens.
- `Lemma` is lexeme abstraction and can later diverge from `Form` when true lemmatization is added.
- `MorphAnalysis` is an interpretation layer attached to tokens; multiple analyses can coexist for different analyzers.

## MVP vs Planned Full Model

### MVP (Sprint 1 reality)

- Active ingest: `Work`, `Edition`, `Segment`, `Token`, `Form`
- Temporary support in code: `Lemma` (placeholder mapping), `MorphAnalysis` (placeholder analyzer)
- Core edges: `HAS_EDITION`, `HAS_SEGMENT`, `HAS_TOKEN`, `INSTANCE_OF_FORM`, `HAS_ANALYSIS`

### Planned full model

- Add robust use of: `Witness`, `Sense`, `MorphAnalysis`, `Etymon`, `CognateSet`, `Claim`, `Source`
- Expand claim-backed scholarship workflows and lineage queries
- Add token-level alignment derived from segment alignment

## Dating Model (Current Policy)

- Canonical temporal fields live on `Edition` for now.
- `date_start`/`date_end` are integer years (negative allowed for BCE).
- `date_approx` should be `true` when ranges are estimated placeholders.
- `source_label` is required for human-readable fallback sorting/filtering when dates are missing.
- `Witness` date fields are planned and may later override or refine edition-level dating for manuscript-specific queries.
