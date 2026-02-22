# Word Lineage Acceptance Queries

Related docs: [Vision](../vision.md), [Schema](../schema.md), [Query Cookbook](query-cookbook.md)

Goal: verify the core feature of tracing Norse words through attestations and into modern branches.

## A. Attestations over source text

Given a normalized form or surface, show where it appears:

```cypher
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f:Form)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE f.orthography = $orthography OR t.normalized = $orthography
RETURN e.edition_id, e.source_label, e.date_start, e.date_end, s.ref, s.text, t.surface, t.position
ORDER BY COALESCE(e.date_start, 999999), e.source_label, s.ref, t.position;
```

## B. Variant grouping by period (claim-based / future-ready)

```cypher
MATCH (f:Form)-[r:REALIZES]->(l:Lemma)
WHERE COALESCE(r.is_active, true) = true
OPTIONAL MATCH (l)-[:DERIVES_FROM]->(origin)
RETURN l.lemma_id, l.headword, collect(DISTINCT f.orthography) AS variants, collect(DISTINCT origin) AS origins
ORDER BY l.headword;
```

Use date fields from `Edition` or `Source.year` when available. If dates are missing, treat results as undated and do not infer chronology.

## B1. Historiography variant (include inactive mappings)

```cypher
MATCH (f:Form)-[r:REALIZES]->(l:Lemma)
OPTIONAL MATCH (l)-[:DERIVES_FROM]->(origin)
RETURN l.lemma_id,
       l.headword,
       f.orthography,
       COALESCE(r.is_active, true) AS is_active,
       r.assigned_by AS assigned_by,
       r.confidence AS confidence,
       r.created_at AS created_at,
       collect(DISTINCT origin) AS origins
ORDER BY l.headword, is_active DESC, created_at ASC;
```

## B2. Date fallback variant for undated editions

When dates are null, filter by `source_label` to keep a stable grouping:

```cypher
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f:Form)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE (f.orthography = $orthography OR t.normalized = $orthography)
  AND e.date_start IS NULL
  AND e.source_label CONTAINS $source_label
RETURN e.edition_id, e.source_label, s.ref, s.text, t.surface, t.position
ORDER BY e.source_label, s.ref, t.position;
```

## B3. Temporal profile for a lemma (forms, counts, features, source)

Given `lemma_id` and date range, return form frequencies, feature buckets (`case`/`number`/`gender` when present), and edition source, ordered by `date_start`:

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})<-[r:REALIZES]-(f:Form)
WHERE COALESCE(r.is_active, true) = true
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
OPTIONAL MATCH (t)-[:HAS_ANALYSIS]->(a:MorphAnalysis)
WHERE a.is_active = true
OPTIONAL MATCH (a)-[:HAS_FEATURE]->(f_case:Feature {key:"case"})
OPTIONAL MATCH (a)-[:HAS_FEATURE]->(f_number:Feature {key:"number"})
OPTIONAL MATCH (a)-[:HAS_FEATURE]->(f_gender:Feature {key:"gender"})
WITH e, f, t,
     COALESCE(f_case.value, "NA") AS m_case,
     COALESCE(f_number.value, "NA") AS m_number,
     COALESCE(f_gender.value, "NA") AS m_gender
WHERE ($from_year IS NULL OR COALESCE(e.date_end, e.date_start, 999999) >= $from_year)
  AND ($to_year IS NULL OR COALESCE(e.date_start, e.date_end, -999999) <= $to_year)
RETURN e.source_label AS source_label,
       e.date_start AS date_start,
       e.date_end AS date_end,
       f.orthography AS form,
       m_case AS case,
       m_number AS number,
       m_gender AS gender,
       count(t) AS freq
ORDER BY COALESCE(date_start, 999999), source_label, freq DESC, form;
```

Fallback behavior when `date_start`/`date_end` are missing: do not infer chronology, order by `source_label` and retain date fields as nullable.

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})<-[r:REALIZES]-(f:Form)
WHERE COALESCE(r.is_active, true) = true
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
OPTIONAL MATCH (t)-[:HAS_ANALYSIS]->(a:MorphAnalysis)
WHERE a.is_active = true
OPTIONAL MATCH (a)-[:HAS_FEATURE]->(f_case:Feature {key:"case"})
OPTIONAL MATCH (a)-[:HAS_FEATURE]->(f_number:Feature {key:"number"})
OPTIONAL MATCH (a)-[:HAS_FEATURE]->(f_gender:Feature {key:"gender"})
RETURN COALESCE(e.source_label, "(unknown source)") AS source_label,
       e.date_start AS date_start,
       e.date_end AS date_end,
       f.orthography AS form,
       COALESCE(f_case.value, "NA") AS case,
       COALESCE(f_number.value, "NA") AS number,
       COALESCE(f_gender.value, "NA") AS gender,
       count(t) AS freq
ORDER BY source_label, freq DESC, form;
```

## B4. Century grouping

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})<-[r:REALIZES]-(f:Form)
WHERE COALESCE(r.is_active, true) = true
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE e.date_start IS NOT NULL
WITH floor(e.date_start / 100) * 100 AS century
RETURN century, count(*) AS attestations
ORDER BY century;
```

## B5. Compare target languages

```cypher
MATCH (l:Lemma)<-[r:REALIZES]-(f:Form)<-[:INSTANCE_OF_FORM]-(t:Token)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WHERE COALESCE(r.is_active, true) = true
  AND l.language IN ["Old Norse","Bokmål","Nynorsk"]
  AND ($lemma_id IS NULL OR l.lemma_id = $lemma_id)
RETURN l.language AS language,
       l.lemma_id AS lemma_id,
       f.orthography AS form,
       COALESCE(e.source_label, "(unknown source)") AS source_label,
       e.date_start AS date_start,
       count(*) AS freq
ORDER BY language, COALESCE(date_start, 999999), freq DESC, form;
```

## C. Branching to Bokmål / Nynorsk

```cypher
MATCH (root:Lemma {lemma_id:'non:Nóregr'})
OPTIONAL MATCH path=(desc:Lemma)-[:DERIVES_FROM*1..3]->(root)
RETURN desc.lemma_id, desc.language, desc.headword, path;
```

Expected in seed demo: branches include `nn:Noreg` and `nb:Norge`.

## D. Competing scholarly claims

```cypher
MATCH (c:Claim)-[:ASSERTS]->(l:Lemma {lemma_id:'non:Nóregr'})
OPTIONAL MATCH (c)-[:SUPPORTED_BY]->(src:Source)
OPTIONAL MATCH (c)-[:CONTRADICTS]->(other:Claim)
RETURN c.claim_id, c.type, c.statement, c.confidence, c.status,
       collect(DISTINCT src.citekey) AS sources,
       collect(DISTINCT other.claim_id) AS contradicts;
```

Acceptance condition: multiple conflicting claims can coexist with distinct sources.

## E. Translation alignment usage (segment-level)

```cypher
MATCH (te:Edition)-[:TRANSLATES]->(se:Edition)
MATCH (te)-[:HAS_SEGMENT]->(ts:Segment)-[a:ALIGNED_TO]->(ss:Segment)<-[:HAS_SEGMENT]-(se)
RETURN te.edition_id, se.edition_id, ts.ref, ts.text, ss.text, a.method, a.confidence
ORDER BY ts.ref
LIMIT 50;
```

Future: token-level alignment should be derived from accepted segment alignment pairs.
