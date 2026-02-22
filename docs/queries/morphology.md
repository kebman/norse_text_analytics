# Morphology Queries

Related docs: [Schema](../schema.md), [Invariants](../invariants.md), [Word Lineage](word-lineage.md)

Note: current ingest creates placeholder `MorphAnalysis` nodes with zero features. Feature-based queries are acceptance scaffolding and will return sparse/empty results until real features are populated.

## 1) Counts by case/number/gender for a lemma in a date range

```cypher
MATCH (m:MorphAnalysis)-[:ANALYZES_AS]->(l:Lemma {lemma_id: $lemma_id})
MATCH (t:Token)-[:HAS_ANALYSIS]->(m)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($date_start IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $date_start)
  AND ($date_end IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $date_end)
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_case:Feature {key: 'case'})
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_number:Feature {key: 'number'})
OPTIONAL MATCH (m)-[:HAS_FEATURE]->(f_gender:Feature {key: 'gender'})
RETURN COALESCE(f_case.value, 'NA') AS case,
       COALESCE(f_number.value, 'NA') AS number,
       COALESCE(f_gender.value, 'NA') AS gender,
       count(*) AS token_count
ORDER BY token_count DESC, case, number, gender;
```

## 2) Example attestations for a form or lemma

```cypher
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f:Form)
OPTIONAL MATCH (f)-[:REALIZES]->(l:Lemma)
OPTIONAL MATCH (t)-[:HAS_ANALYSIS]->(m:MorphAnalysis)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE ($form_id IS NULL OR f.form_id = $form_id)
  AND ($lemma_id IS NULL OR l.lemma_id = $lemma_id)
RETURN e.source_label,
       e.date_start,
       e.date_end,
       s.ref,
       t.surface,
       t.normalized,
       f.orthography AS form,
       l.lemma_id AS lemma_id,
       m.analyzer AS analyzer,
       m.pos AS pos
ORDER BY COALESCE(e.date_start, 999999), e.source_label, s.ref, t.position
LIMIT 100;
```

## 3) Distinct feature values for a lemma in a period

```cypher
MATCH (m:MorphAnalysis)-[:ANALYZES_AS]->(l:Lemma {lemma_id: $lemma_id})
MATCH (t:Token)-[:HAS_ANALYSIS]->(m)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
MATCH (m)-[:HAS_FEATURE]->(f:Feature)
WHERE ($date_start IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $date_start)
  AND ($date_end IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $date_end)
RETURN f.key, collect(DISTINCT f.value) AS values
ORDER BY f.key;
```
