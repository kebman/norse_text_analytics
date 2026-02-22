# Norse Text Analytics

Norse Text Analytics is a graph-first Neo4j system for tracking word attestations through sources over time. The core model separates `Token -> Form -> Lemma`, preserving textual evidence while layering interpretation (morphology, claims, lineage). Neo4j is canonical; JSON is used as import/export input. The goal is provenance-rich, date-aware traceability of words across historical sources and into modern branches such as Bokmål and Nynorsk.

The project follows a "serious play" approach: exploratory ingest and iterative modeling are encouraged, but every step should remain traceable and upgradeable to publish-grade scholarship. See [Serious Play](docs/vision/serious-play.md).

## What You Can Do

- Ingest a source into the graph (currently `data/Hávamál1.json`).
- Query attestations for a form/lemma across dated sources.
- Inspect orthographic variants and placeholder morphology analysis structure.
- Run canonical Cypher workflows from the docs query guides.

## Architecture Overview

- Canonical store: Neo4j property graph.
- Evidence layer: `Edition`, `Segment`, `Token`.
- Interpretation layer: `Form`, `Lemma`, `MorphAnalysis`, `Claim`, `Source`.
- Non-destructive evolution: token evidence is immutable; analyses and claims are layered over evidence.

## Quickstart (macOS / zsh)

Run from repo root.

```bash
docker compose up -d
cp .env.example .env
# edit .env and set NEO4J_PASSWORD before running scripts

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

python3 scripts/apply_schema.py
python3 scripts/ingest_havamal_json.py
```

Sanity check in Neo4j Browser (`http://localhost:7474`) or `cypher-shell`:

```cypher
MATCH (e:Edition {edition_id: 'havamal_gudni_jonsson_print'})-[:HAS_SEGMENT]->(s:Segment)
RETURN count(s) AS segments;
```

## Quick Ingest Plaintext

```bash
python3 scripts/ingest_plaintext.py \
  --path data/sample.txt \
  --work-id sample_work \
  --edition-id sample_plaintext_v1 \
  --source-label "Sample Plaintext" \
  --language-stage on \
  --segment line
```

```cypher
MATCH (:Edition {edition_id: "sample_plaintext_v1"})-[:HAS_SEGMENT]->(:Segment)-[:HAS_TOKEN]->(t:Token)
RETURN t.surface AS surface, count(*) AS freq
ORDER BY freq DESC, surface ASC
LIMIT 20;
```

## Repo Layout

- `nta/`: internal library code (model types/ids, graph DB/repository utilities).
- `scripts/`: operational scripts (apply schema, ingest, demos, reporting).
- `docs/`: schema, invariants, ingest contract, query cookbooks, dev logs.
- `data/`: sample source files, including `Hávamál1.json`.

## Documentation

- [Docs Index](docs/index.md)
- [Schema](docs/schema.md)
- [Word Lineage Queries](docs/queries/word-lineage.md)
- [Ingest Adapter Contract](docs/ingest/adapter-contract.md)
- [Commit Conventions](docs/contributing/commit-conventions.md)

## Status and Roadmap

Current:
- Hávamál ingest is implemented and rerunnable.
- Morphology framework exists with placeholder analyzer outputs.
- Graph supports dating, claims, and alignment primitives.

Next:
- Add more source adapters and source datasets.
- Integrate real morphology analyzers.
- Expand branching examples (including Norway lineage scenarios).
- Extend translation alignment from segment-level to token-level workflows.

## Legacy Scripts

`bin/` scripts are retained for legacy/experimental use. The current workflow is `scripts/` + `docs/`.
