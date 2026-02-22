# Analysis Versioning Queries

Related docs: [Morphology Queries](morphology.md), [Schema](../schema.md), [Invariants](../invariants.md)

Canonical patterns for retrieving current vs historical `MorphAnalysis` safely.

## A) Active analysis for a token

```cypher
MATCH (t:Token {token_id:$token_id})-[:HAS_ANALYSIS]->(a:MorphAnalysis)
WHERE a.is_active = true
RETURN a;
```

## B) Full analysis history for a token

```cypher
MATCH (t:Token {token_id:$token_id})-[:HAS_ANALYSIS]->(a:MorphAnalysis)
RETURN a
ORDER BY a.created_at ASC;
```

## C) Prefer active, fallback if none flagged

```cypher
MATCH (t:Token {token_id:$token_id})-[:HAS_ANALYSIS]->(a:MorphAnalysis)
WITH a
ORDER BY a.is_active DESC, a.created_at DESC
LIMIT 1
RETURN a;
```
