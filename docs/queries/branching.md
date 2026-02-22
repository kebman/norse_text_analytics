# Branching Queries

Related docs: [Schema](../schema.md), [Word Lineage](word-lineage.md), [Query Cookbook](query-cookbook.md)

Canonical queries for traversing lemma-to-lemma branching from Old Norse toward modern Norwegian varieties.

## 1) Derivation tree from an ancestor lemma to descendants

Example filter to Bokmål/Nynorsk descendants:

```cypher
MATCH path=(desc:Lemma)-[:DERIVES_FROM*1..6]->(root:Lemma {lemma_id: $root_lemma_id})
WHERE desc.language IN ['Bokmål', 'Nynorsk']
RETURN desc.lemma_id,
       desc.language,
       desc.headword,
       length(path) AS depth,
       path
ORDER BY depth ASC, desc.language, desc.headword;
```

## 2) Siblings sharing the same immediate ancestor

```cypher
MATCH (child:Lemma {lemma_id: $lemma_id})-[:DERIVES_FROM]->(ancestor:Lemma)
MATCH (sibling:Lemma)-[:DERIVES_FROM]->(ancestor)
WHERE sibling.lemma_id <> child.lemma_id
RETURN ancestor.lemma_id AS ancestor_id,
       ancestor.headword AS ancestor_headword,
       sibling.lemma_id AS sibling_id,
       sibling.language AS sibling_language,
       sibling.headword AS sibling_headword
ORDER BY sibling.language, sibling.headword;
```

## 3) Earliest attestation per descendant lemma

Uses `Edition.date_start` with source fallback visibility:

```cypher
MATCH (desc:Lemma)-[:DERIVES_FROM*1..6]->(:Lemma {lemma_id: $root_lemma_id})
WHERE desc.language IN ['Bokmål', 'Nynorsk']
MATCH (f:Form)-[:REALIZES]->(desc)
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f)
MATCH (s:Segment)-[:HAS_TOKEN]->(t)
MATCH (e:Edition)-[:HAS_SEGMENT]->(s)
WITH desc,
     e,
     s,
     COALESCE(e.date_start, 999999) AS order_date
ORDER BY desc.lemma_id, order_date, s.ref
WITH desc, collect({
  edition_id: e.edition_id,
  source_label: e.source_label,
  date_start: e.date_start,
  date_end: e.date_end,
  segment_ref: s.ref
})[0] AS earliest
RETURN desc.lemma_id,
       desc.language,
       desc.headword,
       earliest.edition_id AS earliest_edition_id,
       earliest.source_label AS earliest_source_label,
       earliest.date_start AS earliest_date_start,
       earliest.date_end AS earliest_date_end,
       earliest.segment_ref AS earliest_segment_ref
ORDER BY desc.language, desc.headword;
```

Notes:
- If `date_start` is missing, ordering falls back to `999999` so undated editions appear last.
- `source_label` is still returned to keep provenance visible for undated sources.
