# Plaintext Adapter

Related docs: [Ingest Overview](ingest-overview.md), [Raw Sources and Adapters](raw-source-and-adapters.md), [Adapter Contract](adapter-contract.md), [Query Acceptance Tests](../query-acceptance-tests.md)

## Purpose

Ingest UTF-8 plain text files with minimal structure into the graph using deterministic IDs and MERGE-based upserts.

## Script

`scripts/ingest_plaintext.py`

## Usage

```bash
python3 scripts/ingest_plaintext.py \
  --path data/sample.txt \
  --work-id sample_work \
  --edition-id sample_plaintext_v1 \
  --source-label "Sample Plaintext" \
  --language-stage on \
  --segment line \
  --date-start 900 \
  --date-end 1100
```

Required inputs:
- `--path`
- `--work-id`
- `--edition-id`
- `--source-label`
- `--language-stage`

Optional:
- `--date-start`
- `--date-end`
- `--segment` (`line` default, `paragraph` optional)

## Behavior

- Reads input as UTF-8.
- Segments input by mode:
  - `line`: each non-empty line is a segment.
  - `paragraph`: split on blank-line runs.
- Creates one `Segment` per segment unit with:
  - `ref = "<line_ordinal>"`
  - `segment_id = "<edition_id>:seg<ordinal>"`
- Tokenizes each segment by whitespace and strips surrounding punctuation.
- Creates tokens with:
  - `token_id = "<segment_id>:t<token_index>"`
  - `normalized` using v0 normalization (`strip punctuation + collapse whitespace`, diacritics preserved)
- Creates forms with:
  - `form_id = "<language_stage>:<surface>"`
- Creates lemma nodes as temporary 1:1 mapping with forms:
  - `lemma_id = form_id`
  - `(Form)-[:REALIZES]->(Lemma)`

All writes are MERGE-based and idempotent.

## Acceptance Example

Ingest a small plaintext file and verify token frequency:

```bash
python3 scripts/ingest_plaintext.py \
  --path data/sample.txt \
  --work-id sample_work \
  --edition-id sample_plaintext_v1 \
  --source-label "Sample Plaintext" \
  --language-stage on \
  --segment paragraph
```

```cypher
MATCH (:Edition {edition_id: "sample_plaintext_v1"})-[:HAS_SEGMENT]->(:Segment)-[:HAS_TOKEN]->(t:Token)
RETURN t.surface AS surface, count(*) AS freq
ORDER BY freq DESC, surface ASC
LIMIT 20;
```

## Current Limitations

- No structural parsing beyond line/paragraph segmentation.
- No TEI/HTML markup interpretation.
- No morphology inference beyond existing placeholder layers.
- `Form` IDs are surface-based and case-sensitive under the provided `language_stage`.
