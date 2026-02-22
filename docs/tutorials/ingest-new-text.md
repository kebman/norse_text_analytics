# Ingest New Text (Serious Play)

Related docs: [Serious Play](../vision/serious-play.md), [Raw Sources and Adapters](../ingest/raw-source-and-adapters.md), [IDs and References](../ids-and-references.md), [Word Lineage Queries](../queries/word-lineage.md)

Practical manual for repeatable exploratory ingest that can later be upgraded to publish-grade output.

## Preconditions

Run from repo root:

```bash
docker compose up -d
cp .env.example .env
# edit .env and set NEO4J_PASSWORD

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

python3 scripts/apply_schema.py
```

## Choose Ingestion Path by Source Format

### A) Plain text (fast path)

Use `scripts/ingest_plaintext.py`.
Recommended for quick serious-play onboarding.

### B) Markdown

Treat as plain text by default.
Headers/list markers may become tokens; acceptable in play mode.

### C) HTML

For now: extract/strip tags into text, then ingest as plain text.
Keep a provenance note that HTML cleanup was performed.
Future adapter should preserve richer structure.

### D) PDF

Discouraged as direct source.
Convert to UTF-8 text first, then ingest.
Expect OCR noise, broken line wraps, and uncertain segmentation.

## Required Metadata Checklist

- `work_id`
- `edition_id`
- `source_label`
- `language_stage`
- approximate `date_start`/`date_end` (optional but recommended)
- provenance note:
  - where source came from (URL/path/archive)
  - who edited/transcribed/cleaned it

## Segmentation Guidelines

- Best: stable source refs (verse/strophe/line).
- Acceptable: line ordinals.
- Fallback: paragraph ordinals.

Rule: choose the most stable deterministic boundary available; avoid heuristic IDs that drift across reruns.

## Deterministic ID Rules (Tutorial Version)

Preferred (structured sources):

- `segment_id = <edition_id>:v<verse>:s<strophe>:l<line>`
- `token_id = <segment_id>:t<index>`

Fallback (messy sources):

- `segment_id = <edition_id>:l<line_ordinal>` (or paragraph ordinal if line structure is unreliable)
- `token_id = <segment_id>:t<index>`

Current plaintext adapter convention:

- `form_id = <language_stage>:<surface>`

## Example Workflow: Plain Text Ingest

Example source file: `data/sample.txt`

```bash
python3 scripts/ingest_plaintext.py \
  --path data/sample.txt \
  --work-id sample_work \
  --edition-id sample_plaintext_v1 \
  --source-label "Sample Plaintext" \
  --language-stage on \
  --date-start 900 \
  --date-end 1100
```

### Verify counts

```cypher
MATCH (e:Edition {edition_id: "sample_plaintext_v1"})-[:HAS_SEGMENT]->(s:Segment)
OPTIONAL MATCH (s)-[:HAS_TOKEN]->(t:Token)
RETURN count(DISTINCT s) AS segments, count(t) AS tokens;
```

### Run a word-lineage style check for expected token

Use a token you expect in the text, for example `$orthography = "ok"`:

```cypher
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f:Form)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE e.edition_id = "sample_plaintext_v1"
  AND (f.orthography = $orthography OR t.normalized = $orthography)
RETURN e.source_label, e.date_start, e.date_end, s.ref, t.surface, s.text
ORDER BY COALESCE(e.date_start, 999999), e.source_label, s.ref, t.position
LIMIT 50;
```

## Upgrade to Publish Mode Checklist

- Add complete `Source` records for any claims.
- Verify and document edition date ranges and date notes.
- Replace placeholder analyses with analyzer-tagged analyses (version + timestamp).
- Model claim conflicts explicitly (`CONTRADICTS`) and set clear status/confidence.
- Re-run query acceptance checks: [Query Acceptance Tests](../query-acceptance-tests.md).

## Troubleshooting

- Encoding errors:
  - Ensure input is UTF-8.
  - Re-save problematic files with UTF-8 normalization.
- Diacritics in filenames:
  - Use quoted paths in shell commands.
  - Verify exact filename normalization on your filesystem.
- Neo4j auth failures:
  - Check `.env` has `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
  - Restart shell/session after env changes.
- Import errors (`import nta`):
  - Prefer editable install (`pip install -e .`) over `PYTHONPATH` hacks.
  - If needed temporarily, run from repo root where scripts add repo path.
