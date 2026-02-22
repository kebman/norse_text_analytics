# Query Cookbook

Related docs: [Schema](../schema.md), [Word Lineage](word-lineage.md), [Morphology Queries](morphology.md), [Invariants](../invariants.md)

## Graph counts

```cypher
MATCH (w:Work) RETURN count(w) AS works;
MATCH (e:Edition) RETURN count(e) AS editions;
MATCH (s:Segment) RETURN count(s) AS segments;
MATCH (t:Token) RETURN count(t) AS tokens;
MATCH (f:Form) RETURN count(f) AS forms;
MATCH (n) RETURN count(n) AS total_nodes;
```

## Segments for Hávamál edition

```cypher
MATCH (:Edition {edition_id:'havamal_gudni_jonsson_print'})-[:HAS_SEGMENT]->(s:Segment)
RETURN s.segment_id, s.ref, s.text
ORDER BY s.verse, s.strophe, s.line_index
LIMIT 25;
```

## Top token surfaces

```cypher
MATCH (t:Token)
WHERE t.surface IS NOT NULL AND t.surface <> ''
RETURN t.surface AS surface, count(*) AS freq
ORDER BY freq DESC, surface ASC
LIMIT 20;
```

## Top normalized tokens

```cypher
MATCH (t:Token)
WHERE t.normalized IS NOT NULL AND t.normalized <> ''
RETURN t.normalized AS normalized, count(*) AS freq
ORDER BY freq DESC, normalized ASC
LIMIT 20;
```

## Token -> Form examples

```cypher
MATCH (t:Token)-[:INSTANCE_OF_FORM]->(f:Form)
RETURN t.surface, t.normalized, f.form_id, f.orthography
LIMIT 25;
```

## Idempotency check (duplicate IDs)

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
