# Dev Log: Sprint 1 - Graph Spine and First Ingest

Date: 2026-02-22  
Branch: `graph-core`

## Summary

### What we set out to do
- Establish a minimal but extensible Neo4j graph spine for Norse text analytics.
- Ingest `data/Hávamál1.json` into graph primitives (`Work`, `Edition`, `Segment`, `Token`, `Form`).
- Make ingestion idempotent and operationally repeatable.
- Add scaffolding for next layers (Lemma, Claims/Sources, alignment, repo abstractions).

### What we achieved
- Implemented Neo4j schema file with constraints and indexes for core + extended model labels.
- Added environment-driven DB configuration and removed hardcoded secrets.
- Added first ingest pipeline script for Hávamál JSON with deterministic IDs and MERGE-based writes.
- Added typed internal model/repository layer (`nta/model`, `nta/graph/repo.py`).
- Added experimental layers (Lemma mapping, claim/source framework, alignment demo, Norway seed data).
- Added packaging scaffold (`pyproject.toml`) so `import nta` is package-managed.

## Repo Changes

### New directories/files
- `nta/graph/schema.cypher`
- `nta/graph/db.py`
- `nta/graph/repo.py`
- `nta/model/ids.py`
- `nta/model/types.py`
- `nta/__init__.py`
- `nta/graph/__init__.py`
- `nta/model/__init__.py`
- `scripts/apply_schema.py`
- `scripts/ingest_havamal_json.py`
- `scripts/seed_norway_example.py`
- `scripts/align_demo.py`
- `docs/schema.md`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `pyproject.toml`

### Notable modifications
- `docker-compose.yml`: Neo4j auth moved to env interpolation (`NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}`).
- `bin/numWordsHávamál.py`: graph-backed token frequency path added.
- `docs/prompts/2026-02-22.md`: sprint prompt log updated (no secret literals).
- `README.md`: setup instructions updated (venv + editable install path).

## Neo4j Setup

### Environment
- Use local `.env` (not tracked) with:
  - `NEO4J_PASSWORD=<your_password>`
  - `NEO4J_URI=bolt://localhost:7687`
  - `NEO4J_USER=neo4j`

Reference template: `.env.example`

### Start / stop Neo4j
- Start:
```bash
docker compose up -d neo4j
```
- Stop:
```bash
docker compose stop neo4j
```
- Remove container/network (keep named volumes unless `-v` added):
```bash
docker compose down
```

### Apply schema
```bash
python3 scripts/apply_schema.py
```

## Python Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Run key scripts:
```bash
python3 scripts/apply_schema.py
python3 scripts/ingest_havamal_json.py
python3 scripts/seed_norway_example.py
python3 scripts/align_demo.py
```

## Schema Applied

`nta/graph/schema.cypher` includes (at minimum):

### Uniqueness constraints
- `Work.work_id`
- `Witness.witness_id`
- `Edition.edition_id`
- `Segment.segment_id`
- `Token.token_id`
- `Form.form_id`
- `Lemma.lemma_id`
- `Sense.sense_id`
- `MorphAnalysis.analysis_id`
- `Etymon.etymon_id`
- `CognateSet.set_id`
- `Claim.claim_id`
- `Source.source_id`

### Indexes
- `Token.surface`
- `Token.normalized`
- `Form.orthography`
- `Lemma.headword`
- `Segment.ref`
- `Segment.segment_ref`
- `Source.citekey`
- `Claim.type`
- `ALIGNED_TO.method` (relationship property)
- `ALIGNED_TO.confidence` (relationship property)

## Ingestion Result

From first full ingest run on `data/Hávamál1.json`:
- Segments: `1086`
- Tokens: `4045`
- Total nodes: `6654`

## Verify in Neo4j (Cypher)

### Core counts
```cypher
MATCH (w:Work) RETURN count(w) AS works;
MATCH (e:Edition) RETURN count(e) AS editions;
MATCH (s:Segment) RETURN count(s) AS segments;
MATCH (t:Token) RETURN count(t) AS tokens;
MATCH (f:Form) RETURN count(f) AS forms;
MATCH (n) RETURN count(n) AS total_nodes;
```

### Hávamál edition linkage
```cypher
MATCH (:Work {work_id:'havamal'})-[:HAS_EDITION]->(e:Edition)
RETURN e.edition_id, e.title;
```

### Segment/token relation sanity
```cypher
MATCH (e:Edition {edition_id:'havamal_gudni_jonsson_print'})-[:HAS_SEGMENT]->(s:Segment)
RETURN count(s) AS segment_count;

MATCH (s:Segment)-[:HAS_TOKEN]->(t:Token)
RETURN count(t) AS token_edge_count;
```

### Idempotency quick check
Run ingest twice, then verify no duplicate IDs:
```cypher
MATCH (s:Segment)
WITH s.segment_id AS id, count(*) AS c
WHERE c > 1
RETURN id, c;

MATCH (t:Token)
WITH t.token_id AS id, count(*) AS c
WHERE c > 1
RETURN id, c;
```

## Known Issues / Footguns

- `PYTHONPATH=.` workaround was used earlier for direct script runs. Packaging now exists; prefer editable install (`pip install -e .`).
- Headless/SSH environments may fail `pip install -e .` if offline and build isolation tries to fetch build requirements.
- `NEO4J_PASSWORD` is now mandatory in env; missing value raises runtime `ValueError` in `Neo4jConfig.from_env()`.
- Filenames with diacritics (`Hávamál`) can be shell-locale sensitive in some environments; use tab completion or quoted paths.
- Current lemma mapping is placeholder (normalized form -> lemma 1:1), not linguistic lemmatization.

## Next Steps (Sprint 1 backlog aligned)

1. Stabilize ingest around repository API only (remove residual direct Cypher in scripts where possible).
2. Add automated smoke tests for schema application + idempotent ingest counts.
3. Tighten claim/source examples into reproducible fixtures with deterministic assertions.
4. Expand alignment demo from first stanza to controlled multi-stanza subset.
5. Prepare Sprint 2 handoff notes: true lemmatization strategy + token-level alignment design.
