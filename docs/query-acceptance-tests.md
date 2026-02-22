# Query Acceptance Tests

Related docs: [Schema](schema.md), [Invariants](invariants.md), [Word Lineage Queries](queries/word-lineage.md), [Query Cookbook](queries/query-cookbook.md)

Purpose: define a small canonical Cypher suite that should keep working as the model evolves.

Date fallback rule used throughout: when chronology is partial, order with `COALESCE(e.date_start, 999999)` and then `source_label`.

## 1) Sanity counts

### 1.1 Count nodes by label
Purpose: verify baseline graph shape and detect accidental label regressions.

Parameters: none.

Expected output shape: rows of `(label, n)` where `label` is `STRING` and `n` is `INTEGER`.

```cypher
CALL db.labels() YIELD label
CALL {
  WITH label
  MATCH (n)
  WHERE label IN labels(n)
  RETURN count(n) AS n
}
RETURN label, n
ORDER BY label;
```

### 1.2 Count core entities
Purpose: verify core ingest entities exist and are queryable.

Parameters: none.

Expected output shape: single row with integer fields `tokens`, `segments`, `forms`, `lemmas`.

```cypher
MATCH (t:Token)
WITH count(t) AS tokens
MATCH (s:Segment)
WITH tokens, count(s) AS segments
MATCH (f:Form)
WITH tokens, segments, count(f) AS forms
MATCH (l:Lemma)
RETURN tokens, segments, forms, count(l) AS lemmas;
```

## 2) Word lineage

### 2.1 Attestations across editions with date fallback ordering
Purpose: trace lemma/form attestations through editions in temporal order, with stable fallback when dates are missing.

Parameters:
- `$lemma_id` (`STRING`, optional)
- `$orthography` (`STRING`, optional)

Expected output shape: rows with `edition_id`, `source_label`, `date_start`, `date_end`, `segment_ref`, `surface`, `normalized`, `position`, `segment_text`.

```cypher
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f:Form)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
OPTIONAL MATCH (f)-[r:REALIZES]->(l:Lemma)
WHERE (COALESCE(r.is_active, true) = true OR r IS NULL)
  AND ($lemma_id IS NULL OR l.lemma_id = $lemma_id)
  AND ($orthography IS NULL OR f.orthography = $orthography OR t.normalized = $orthography)
RETURN e.edition_id AS edition_id,
       COALESCE(e.source_label, "(unknown source)") AS source_label,
       e.date_start AS date_start,
       e.date_end AS date_end,
       s.ref AS segment_ref,
       t.surface AS surface,
       t.normalized AS normalized,
       t.position AS position,
       s.text AS segment_text
ORDER BY COALESCE(e.date_start, 999999), source_label, segment_ref, position
LIMIT 200;
```

## 3) Branching to modern standards

### 3.1 Derivation paths to modern target standards
Purpose: verify historical branching queries from an ancestor lemma into modern standards.

Parameters:
- `$root_lemma_id` (`STRING`, required)

Expected output shape: rows with `descendant_lemma_id`, `descendant_language`, `descendant_headword`, `path_length`.

```cypher
MATCH (root:Lemma {lemma_id: $root_lemma_id})
MATCH path=(desc:Lemma)-[:DERIVES_FROM*1..8]->(root)
WHERE desc.language IN ["Bokmål", "Nynorsk", "Swedish", "Icelandic"]
RETURN desc.lemma_id AS descendant_lemma_id,
       desc.language AS descendant_language,
       desc.headword AS descendant_headword,
       length(path) AS path_length
ORDER BY descendant_language, path_length, descendant_lemma_id;
```

## 4) Morphology (structure only)

### 4.1 Tokens and active analyses for a lemma in a date range
Purpose: confirm morphology structure is connected even when feature inventory is empty.

Parameters:
- `$lemma_id` (`STRING`, required)
- `$from_year` (`INTEGER`, optional)
- `$to_year` (`INTEGER`, optional)

Expected output shape: rows with `analysis_id`, `analyzer`, `analyzer_version`, `source_label`, `date_start`, `segment_ref`, `surface`, `normalized`.

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})<-[r:REALIZES]-(f:Form)<-[:INSTANCE_OF_FORM]-(t:Token)-[:HAS_ANALYSIS]->(a:MorphAnalysis)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE COALESCE(r.is_active, true) = true
  AND a.is_active = true
  AND ($from_year IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $from_year)
  AND ($to_year IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $to_year)
RETURN a.analysis_id AS analysis_id,
       a.analyzer AS analyzer,
       a.analyzer_version AS analyzer_version,
       COALESCE(e.source_label, "(unknown source)") AS source_label,
       e.date_start AS date_start,
       s.ref AS segment_ref,
       t.surface AS surface,
       t.normalized AS normalized
ORDER BY COALESCE(e.date_start, 999999), source_label, segment_ref, t.position
LIMIT 200;
```

## 5) Provenance

### 5.1 Claims for a lemma with sources and confidence
Purpose: verify claim provenance, confidence tracking, and source linkage.

Parameters:
- `$lemma_id` (`STRING`, required)

Expected output shape: rows with `claim_id`, `claim_type`, `status`, `confidence`, `created_at`, `sources` (list of source maps), `source_count`.

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})
MATCH (c:Claim)-[:ASSERTS]->(l)
OPTIONAL MATCH (c)-[:SUPPORTED_BY]->(s:Source)
RETURN c.claim_id AS claim_id,
       c.type AS claim_type,
       c.status AS status,
       c.confidence AS confidence,
       c.created_at AS created_at,
       collect(DISTINCT {
         source_id: s.source_id,
         citekey: s.citekey,
         title: s.title,
         year: s.year
       }) AS sources,
       count(DISTINCT s) AS source_count
ORDER BY c.status, c.confidence DESC, c.created_at;
```
