# Schema

Related docs: [Glossary](glossary.md), [Invariants](invariants.md), [IDs and References](ids-and-references.md), [Ingest Overview](ingest/ingest-overview.md)

## Node Types and Key Properties

- `Work`: `work_id`, `title`
- `Witness`: `witness_id`, `siglum`, `description`
- `Edition`: `edition_id`, `title`, `cover`, `writer`, `language`, `version`
- `Segment`: `segment_id`, `verse`, `strophe`, `line_index`, `ref`, `text`, `position`
- `Token`: `token_id`, `surface`, `normalized`, `position`
- `Form`: `form_id`, `orthography`, `language`
- `Lemma`: `lemma_id`, `headword`, `language`, `pos`
- `Sense`: `sense_id`, `gloss`, `definition`
- `MorphAnalysis`: `analysis_id`, `tagset`, `features`, `analyzer`
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
- `(:Form)-[:REALIZES]->(:Lemma)`
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

## MVP vs Planned Full Model

### MVP (Sprint 1 reality)

- Active ingest: `Work`, `Edition`, `Segment`, `Token`, `Form`
- Temporary support in code: `Lemma` (placeholder mapping)
- Core edges: `HAS_EDITION`, `HAS_SEGMENT`, `HAS_TOKEN`, `INSTANCE_OF_FORM`

### Planned full model

- Add robust use of: `Witness`, `Sense`, `MorphAnalysis`, `Etymon`, `CognateSet`, `Claim`, `Source`
- Expand claim-backed scholarship workflows and lineage queries
- Add token-level alignment derived from segment alignment
