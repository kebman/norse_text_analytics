# Morphology Queries

Related docs: [Schema](../schema.md), [Invariants](../invariants.md), [Word Lineage](word-lineage.md)

This page documents the canonical Cypher used by `scripts/report_inflections.py`.

Current Sprint-1 caveat: ingest creates placeholder `MorphAnalysis` nodes with zero features. Feature queries are still valid but may return empty/`NA`-only rows until real features are attached.

## Script-backed query A: top observed surfaces for a lemma

With date filters (`--from-year` and/or `--to-year` provided):

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})<-[:REALIZES]-(f:Form)<-[:INSTANCE_OF_FORM]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($from_year IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $from_year)
  AND ($to_year IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $to_year)
  AND ($source_like IS NULL OR toLower(COALESCE(e.source_label, "")) CONTAINS toLower($source_like))
RETURN t.surface AS surface,
       count(*) AS freq
ORDER BY freq DESC, surface ASC
LIMIT $limit
```

Date fallback behavior (when neither `--from-year` nor `--to-year` is set):

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})<-[:REALIZES]-(f:Form)<-[:INSTANCE_OF_FORM]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($source_like IS NULL OR toLower(COALESCE(e.source_label, "")) CONTAINS toLower($source_like))
RETURN COALESCE(e.source_label, "(unknown source)") AS source_label,
       e.date_start AS date_start,
       e.date_end AS date_end,
       t.surface AS surface,
       count(*) AS freq
ORDER BY source_label ASC, freq DESC, surface ASC
LIMIT $limit
```

## Script-backed query B: counts by morphology features

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})<-[:ANALYZES_AS]-(m:MorphAnalysis)<-[:HAS_ANALYSIS]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($from_year IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $from_year)
  AND ($to_year IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $to_year)
  AND ($source_like IS NULL OR toLower(COALESCE(e.source_label, "")) CONTAINS toLower($source_like))
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_case:Feature {key: "case"})
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_number:Feature {key: "number"})
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_gender:Feature {key: "gender"})
RETURN COALESCE(f_case.value, "NA") AS case,
       COALESCE(f_number.value, "NA") AS number,
       COALESCE(f_gender.value, "NA") AS gender,
       count(*) AS freq
ORDER BY freq DESC, case, number, gender
LIMIT $limit
```

## Script-backed query C: example attestations

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})<-[:REALIZES]-(f:Form)<-[:INSTANCE_OF_FORM]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($from_year IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $from_year)
  AND ($to_year IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $to_year)
  AND ($source_like IS NULL OR toLower(COALESCE(e.source_label, "")) CONTAINS toLower($source_like))
RETURN COALESCE(e.source_label, "(unknown source)") AS source_label,
       e.date_start AS date_start,
       e.date_end AS date_end,
       s.ref AS segment_ref,
       t.surface AS surface,
       s.text AS segment_text
ORDER BY COALESCE(e.date_start, 999999), source_label, segment_ref, t.position
LIMIT $limit
```

## Script usage

```bash
python3 scripts/report_inflections.py --lemma-id non:Nóregr
python3 scripts/report_inflections.py --lemma-id non:Nóregr --from-year 900 --to-year 1200
python3 scripts/report_inflections.py --lemma-id non:Nóregr --source-like Hávamál --limit 10
```
