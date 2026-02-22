# Branching Queries

Related docs: [Schema](../schema.md), [Word Lineage](word-lineage.md), [Query Cookbook](query-cookbook.md)

Canonical queries for traversing lemma-to-lemma branching from Old Norse toward modern standards.

## 1) Descendants from Old Norse to modern target standards

Target stages covered explicitly: Icelandic, Faroese, Swedish, Danish, Bokmål, Nynorsk.

```cypher
MATCH path=(desc:Lemma)-[:DERIVES_FROM*1..6]->(root:Lemma {lemma_id: $root_lemma_id})
WHERE desc.language_stage IN ['isl', 'fo', 'sv', 'da', 'nb', 'nn']
RETURN desc.lemma_id,
       desc.language_stage,
       desc.language,
       desc.headword,
       length(path) AS depth,
       path
ORDER BY depth ASC, desc.language_stage, desc.headword;
```

## 2) Earliest attestation per descendant (date fallback included)

Uses `Edition.date_start` as primary chronology. If missing, ordering falls back to `source_label`.

```cypher
MATCH (desc:Lemma)-[:DERIVES_FROM*1..6]->(:Lemma {lemma_id: $root_lemma_id})
WHERE desc.language_stage IN ['isl', 'fo', 'sv', 'da', 'nb', 'nn']
MATCH (f:Form)-[r:REALIZES]->(desc)
WHERE COALESCE(r.is_active, true) = true
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WITH desc,
     e,
     s,
     COALESCE(e.date_start, 999999) AS order_date,
     COALESCE(e.source_label, "(unknown source)") AS order_source
ORDER BY desc.lemma_id, order_date, order_source, s.ref
WITH desc, collect({
  edition_id: e.edition_id,
  source_label: e.source_label,
  date_start: e.date_start,
  date_end: e.date_end,
  segment_ref: s.ref
})[0] AS earliest
RETURN desc.lemma_id,
       desc.language_stage,
       desc.headword,
       earliest.edition_id AS earliest_edition_id,
       earliest.source_label AS earliest_source_label,
       earliest.date_start AS earliest_date_start,
       earliest.date_end AS earliest_date_end,
       earliest.segment_ref AS earliest_segment_ref
ORDER BY desc.language_stage, desc.headword;
```

## 3) Parallel branches (siblings) sharing the same ancestor

```cypher
MATCH (child:Lemma {lemma_id: $lemma_id})-[:DERIVES_FROM]->(ancestor:Lemma)
MATCH (sibling:Lemma)-[:DERIVES_FROM]->(ancestor)
WHERE sibling.lemma_id <> child.lemma_id
  AND sibling.language_stage IN ['isl', 'fo', 'sv', 'da', 'nb', 'nn']
RETURN ancestor.lemma_id AS ancestor_id,
       ancestor.headword AS ancestor_headword,
       sibling.lemma_id AS sibling_id,
       sibling.language_stage AS sibling_language_stage,
       sibling.language AS sibling_language,
       sibling.headword AS sibling_headword
ORDER BY sibling.language_stage, sibling.headword;
```

Notes:
- `language_stage` is the canonical filter for modern standards.
- Date fallback behavior uses `COALESCE(e.date_start, 999999)` and then `source_label`.
