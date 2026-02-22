# Graph Schema Reference

This document defines the intended property-graph model for Norse text analytics in Neo4j.
It is a development reference: node/edge semantics, invariants, and ID conventions.

## 1) Node Types

### `Work`
- Meaning: conceptual text work (for example, Havamal as a work).
- Core properties:
  - `work_id` (stable unique id)
  - `title`

### `Witness`
- Meaning: concrete textual witness/manuscript/attestation context.
- Core properties:
  - `witness_id`
  - `siglum` (optional short label)
  - `description` (optional)

### `Edition`
- Meaning: specific edited/transcribed dataset used for ingestion.
- Core properties:
  - `edition_id`
  - `label` (optional)
  - `version` (optional)

### `Segment`
- Meaning: textual span in an edition (line/strophe/verse depending on source structure).
- Core properties:
  - `segment_id`
  - `text`
  - `position` (ordinal inside parent edition/witness)
  - `level` (optional: `line`, `strophe`, `verse`)

### `Token`
- Meaning: one word occurrence in a specific segment position.
- Core properties:
  - `token_id`
  - `surface`
  - `position` (ordinal inside segment)

### `Form`
- Meaning: normalized surface form type (orthographic bucket), language-scoped.
- Core properties:
  - `form_id`
  - `orthography`
  - `language`

### `Lemma`
- Meaning: dictionary-style lexical entry (headword + language + optional POS).
- Core properties:
  - `lemma_id`
  - `headword`
  - `language`
  - `pos` (optional in MVP, can be `"unknown"`)

### `Sense` (optional)
- Meaning: sense-level meaning distinction for a lemma.
- Core properties:
  - `sense_id`
  - `gloss` (optional)
  - `definition` (optional)

### `MorphAnalysis`
- Meaning: analysis result describing morphological parse/tagging for a token or form.
- Core properties:
  - `analysis_id`
  - `tagset`
  - `features` (map or serialized structure)
  - `analyzer` (tool/model/source id)

### `Etymon`
- Meaning: etymological source item (proto-form, donor form, etc.).
- Core properties:
  - `etymon_id`
  - `form`
  - `language`
  - `period` (optional)

### `CognateSet`
- Meaning: grouping of forms/lemmas believed cognate.
- Core properties:
  - `cognate_set_id`
  - `label` (optional)

### `Claim`
- Meaning: explicit, citable assertion (especially for uncertain/competing analyses).
- Core properties:
  - `claim_id`
  - `type` (for example: `etymology`, `sense-assignment`, `morph-analysis`)
  - `statement`
  - `confidence` (optional numeric)
  - `status` (for example: `PROPOSED`, `CONTESTED`, `ACCEPTED`, `REJECTED`)

### `Source`
- Meaning: bibliographic/source record supporting claims.
- Core properties:
  - `source_id`
  - `citekey`
  - `title`
  - `year` (optional)
  - `authors` (optional list)
  - `url` (optional)

## 2) Relationship Types (Direction Is Intentional)

- `(:Work)-[:HAS_EDITION]->(:Edition)`
- `(:Edition)-[:TRANSLATES]->(:Edition)` (translation edition points to source edition)
- `(:Work)-[:HAS_WITNESS]->(:Witness)`
- `(:Witness)-[:ATTESTS_WORK]->(:Work)` (optional inverse if needed)
- `(:Edition)-[:HAS_SEGMENT]->(:Segment)`
- `(:Witness)-[:HAS_SEGMENT]->(:Segment)` (optional when segments are witness-specific)
- `(:Segment)-[:ALIGNED_TO {method, confidence}]->(:Segment)` (usually translation segment -> source segment)
- `(:Segment)-[:HAS_TOKEN]->(:Token)`
- `(:Token)-[:INSTANCE_OF_FORM]->(:Form)`
- `(:Form)-[:REALIZES]->(:Lemma)`
- `(:Lemma)-[:HAS_SENSE]->(:Sense)` (optional)
- `(:Token)-[:HAS_MORPH_ANALYSIS]->(:MorphAnalysis)` (optional)
- `(:Form)-[:HAS_MORPH_ANALYSIS]->(:MorphAnalysis)` (optional)
- `(:Lemma)-[:DERIVES_FROM]->(:Etymon)` (only for asserted/accepted direct modeling)
- `(:Lemma)-[:IN_COGNATE_SET]->(:CognateSet)` (optional)
- `(:Claim)-[:ASSERTS]->(:Lemma)` (generic assertion target)
- `(:Claim)-[:ASSERTS]->(:Etymon)` (generic assertion target)
- `(:Claim)-[:SUPPORTED_BY]->(:Source)`
- `(:Claim)-[:CONTRADICTS]->(:Claim)` (optional)
- `(:Claim)-[:REFINES]->(:Claim)` (optional)

Preferred traversal flow for text evidence:
`Work -> Edition -> Segment -> Token -> Form -> Lemma -> Sense`

## 3) Cardinalities and Invariants

### Text structure
- Every `Edition` can have many `Segment`.
- Every `Segment` must have zero or more `Token`.
- Every `Token` must belong to exactly one `Segment` in ingestion pipelines.

### Lexical linkage
- Every `Token` must point to exactly one `Form` via `INSTANCE_OF_FORM`.
- Every `Form` should point to at least one `Lemma` via `REALIZES`.
- In current MVP ingestion, `Form` and `Lemma` are temporary 1:1.
- Future target allows `Form -> multiple Lemma` (ambiguity) via `Claim` mediation or additional disambiguation logic.

### Claim/source discipline
- Any uncertain/contestable statement should be represented by `Claim`, not as an unconditional edge/property.
- Every `Claim` must have at least one `SUPPORTED_BY` edge to `Source`.
- Competing analyses are allowed as parallel `Claim` nodes.

### Uniqueness constraints (expected)
- `Work.work_id` unique
- `Witness.witness_id` unique
- `Edition.edition_id` unique
- `Segment.segment_id` unique
- `Token.token_id` unique
- `Form.form_id` unique
- `Lemma.lemma_id` unique
- `Sense.sense_id` unique
- `MorphAnalysis.analysis_id` unique
- `Etymon.etymon_id` unique
- `CognateSet.cognate_set_id` unique
- `Claim.claim_id` unique
- `Source.source_id` unique

## 4) Why `Token`, `Form`, and `Lemma` Are Distinct

- `Token`: concrete text evidence at a specific location.
  - Example: the 5th token in a specific line.
- `Form`: normalized spelling bucket for grouping occurrences.
  - Example: orthographic string + language.
- `Lemma`: lexeme/dictionary entry independent of a single written occurrence.
  - Example: canonical headword and POS.

This separation prevents category errors:
- frequency and collocation belong to `Token`
- orthographic normalization belongs to `Form`
- lexicographic/semantic/etymological assertions belong to `Lemma` (and `Sense`)

## 5) Why `Claim` Nodes Exist

Scholarship is uncertain and often contested. Modeling uncertainty directly on `Lemma` or `Etymon` properties loses provenance and prevents parallel hypotheses.
Use `Claim` nodes so competing positions can coexist.

Typical reasons:
- Multiple etymologies are proposed for the same lemma.
- Sources disagree on segmentation, sense, or origin.
- New scholarship updates prior positions without deleting history.

## 6) Representing Uncertainty With `Claim`

Do not force uncertain etymology into a single hard edge. Instead:
- Create one `Claim` per hypothesis.
- Connect each claim to its target (`ASSERTS`), support (`SUPPORTED_BY`), and optional contradictory/refining claims.
- Keep confidence/status on claim nodes.

Pattern for competing etymologies:
- `Claim A (etymology)` `ASSERTS -> Lemma X`, `SUPPORTED_BY -> Source 1`
- `Claim B (etymology)` `ASSERTS -> Lemma X`, `SUPPORTED_BY -> Source 2`
- Optionally `Claim A -[:CONTRADICTS]-> Claim B`

## 7) ID Conventions (Stable, Deterministic, Rerunnable)

All IDs should be deterministic from stable source inputs and namespace prefixes.

- `work_id`: semantic slug, for example `havamal`
- `witness_id`: siglum/source-derived slug, for example `gks-2365-4to`
- `edition_id`: ingest source + version, for example `havamal_json_v1`
- `segment_id`: `{edition_id}:segment:{ordinal}` or path-based equivalent
- `token_id`: `{segment_id}:token:{ordinal}`
- `form_id`: hash of `{language}\t{orthography}` with prefix `form:{language}:{hash}`
- `lemma_id`: hash of `{language}\t{headword}` with prefix `lemma:{language}:{hash}`
- `sense_id`: hash of `{lemma_id}\t{sense_key}` with prefix `sense:{hash}`
- `analysis_id`: hash of `{token_or_form_id}\t{analyzer}\t{features}` with prefix `morph:{hash}`
- `etymon_id`: hash of `{language}\t{form}\t{period}` with prefix `etymon:{hash}`
- `cognate_set_id`: curated or hash-based stable group id, prefix `cset:`
- `claim_id`: hash of `{type}\t{asserts_target_id}\t{statement}\t{source_id}` with prefix `claim:{hash}`
- `source_id`: bibliographic key/slug/DOI-derived stable id

Rules:
- IDs must not include run timestamps or random UUIDs in normal ingestion.
- Re-running ingestion on unchanged source should produce identical IDs.

## 8) MVP Subset vs Full Model

### MVP (current/near-term)
- Nodes: `Work`, `Edition`, `Segment`, `Token`, `Form`, `Lemma`
- Edges:
  - `HAS_EDITION`
  - `HAS_SEGMENT`
  - `HAS_TOKEN`
  - `INSTANCE_OF_FORM`
  - `REALIZES`
- Temporary rule: `Form` and `Lemma` are 1:1.

### Full target model
- Adds: `Witness`, `Sense`, `MorphAnalysis`, `Etymon`, `CognateSet`, `Claim`, `Source`
- Adds claim-centric uncertainty modeling and competing hypotheses
- Adds richer witness-aware segmentation and morphological/semantic layers

## 9) Translation Alignment Roadmap

- Current alignment primitive is segment-level:
  - `Edition -[:TRANSLATES]-> Edition`
  - `Segment -[:ALIGNED_TO {method, confidence}]-> Segment`
- Intended future:
  - derive token-level translation links from aligned segment pairs
  - keep segment alignment as the parent evidence layer for token alignment decisions
