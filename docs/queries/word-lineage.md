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
MATCH (f:Form)-[:REALIZES]->(l:Lemma)
OPTIONAL MATCH (l)-[:DERIVES_FROM]->(origin)
RETURN l.lemma_id, l.headword, collect(DISTINCT f.orthography) AS variants, collect(DISTINCT origin) AS origins
ORDER BY l.headword;
```

Use date fields from `Edition` or `Source.year` when available. If dates are missing, treat results as undated and do not infer chronology.

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
