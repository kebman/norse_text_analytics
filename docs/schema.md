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
- `MorphAnalysis`: `analysis_id`, `analyzer`, `analyzer_version`, `confidence`, `pos`, `is_ambiguous`, `created_at`, `supersedes`, `is_active`
- `Analyzer`: `analyzer_id`, `name`, `version`, `description`, `author`, `created_at`
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
- `(:MorphAnalysis)-[:PRODUCED_BY]->(:Analyzer)`
- `(:Form)-[:REALIZES {is_active, assigned_by, confidence, created_at}]->(:Lemma)`
- `(:MorphAnalysis)-[:ANALYZES_AS]->(:Lemma)` (optional)
- `(:MorphAnalysis)-[:HAS_FEATURE]->(:Feature)`
- `(:Form)-[:ORTHOGRAPHIC_VARIANT_OF {type}]->(:Form)`
- `(:Token)-[:NORMALIZED_TO {policy}]->(:Form)`
- `(:Claim)-[:SUPPORTED_BY]->(:Source)`
- `(:Claim)-[:ASSERTS]->(:Lemma|:Etymon)`
- `(:Claim)-[:CONTRADICTS]->(:Claim)`
- `(:Lemma)-[:DERIVES_FROM]->(:Etymon|:Lemma)`
- `(:Lemma)-[:BORROWED_FROM]->(:Lemma|:Etymon)`
- `(:Lemma)-[:IN_COGNATE_SET]->(:CognateSet)`
- `(:Edition)-[:TRANSLATES]->(:Edition)`
- `(:Segment)-[:ALIGNED_TO {method, confidence}]->(:Segment)`

## Lemma Branching Semantics

- `DERIVES_FROM` (Lemma-level): historical development lineage, including transitions across language stages.
- `BORROWED_FROM` (Lemma-level): lexical borrowing relationship, distinct from inherited development.
- `ORTHOGRAPHIC_VARIANT_OF` (Form-level): spelling/normalization variation between forms; not a lemma lineage edge.
- `NORMALIZED_TO` (Token/Form-level): ingest normalization trace from token evidence to normalized form.

## Form -> Lemma Mapping Semantics

- `REALIZES` is a versioned interpretation edge from spelling/form evidence to lexeme abstraction.
- `REALIZES` may include:
  - `is_active` (`bool`): active mapping flag for current interpretation queries.
  - `assigned_by` (`string`): analyzer/project/person responsible for assignment.
  - `confidence` (`float`): confidence score for assignment.
  - `created_at` (`datetime`): assignment creation timestamp.
- Mapping updates are non-destructive: create a new active edge and mark previous edge inactive instead of deleting history.
- Optional `Claim` nodes can document rationale for mapping changes.

## Token -> Form -> Lemma Separation

- `Token` is immutable textual evidence at a location.
- `Form` groups orthographic/normalization variants across tokens.
- `Lemma` is lexeme abstraction and can later diverge from `Form` when true lemmatization is added.
- `MorphAnalysis` is an interpretation layer attached to tokens; multiple analyses can coexist for different analyzers.
- `MorphAnalysis.analyzer` is a quick lookup string kept on the analysis node for simple filtering.
- `Analyzer` is the metadata anchor for tool/project provenance (name, version, author, description).

## MorphAnalysis Evolution Rules

- `analysis_id` is deterministic: `<token_id>:<analyzer>`.
- `MorphAnalysis` is immutable evidence of interpretation output.
- Default conventions: `confidence=0.0`, `is_ambiguous=false`, `is_active=true`, `created_at=datetime()` on create.
- Do not update an existing `MorphAnalysis` record except `is_active=false` when it is superseded.
- New analyzer version creates a new `MorphAnalysis` node (new `analysis_id`) rather than overwriting old output.
- If replacing an analysis, set `supersedes=<old_analysis_id>` on the new node and set old node `is_active=false`.

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
