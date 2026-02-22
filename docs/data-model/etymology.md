# Etymology and Cognacy Model

Related docs: [Schema](../schema.md), [Invariants](../invariants.md), [Word Lineage Queries](../queries/word-lineage.md)

## Purpose

Represent etymology and cognacy as explicit, inspectable hypotheses without overwriting historical uncertainty or collapsing disagreement into a single "truth".

## Core Nodes

- `Claim`: reified scholarly assertion; carries confidence and status.
- `Source`: bibliographic support record (`citekey`, `title`, `year`, `authors`, `url`).
- `Etymon`: reconstructed or attested etymological source form.
- `CognateSet` (optional): grouping of historically related forms/lemmas.
- `Lemma`: lexeme-level anchor used in attestations and lineage.

## Core Edges

- `(Claim)-[:ASSERTS]->(Lemma|Etymon|CognateSet)`
Direction: from assertion to asserted target.
Key properties: none required on edge; certainty/status lives on `Claim`.

- `(Claim)-[:SUPPORTED_BY]->(Source)`
Direction: from assertion to evidence source.
Key properties: optional citation detail properties may be added later if needed (for example pages).

- `(Claim)-[:CONTRADICTS]->(Claim)`
Direction: from one claim to a competing claim.
Key properties: optional rationale/notes can be modeled later.

- `(Lemma)-[:DERIVES_FROM]->(Lemma)`
Direction: descendant lemma to historical source lemma.
Key properties: optional dating/provenance metadata can be added later.

- `(Lemma)-[:BORROWED_FROM]->(Lemma)`
Direction: borrower lemma to donor lemma.
Key properties: optional borrowing context metadata can be added later.

- `(Lemma)-[:IN_COGNATE_SET]->(CognateSet)`
Direction: lemma to grouping set.
Key properties: none required in v1.

## Claim Confidence and Status

Use these `Claim` properties:

- `confidence`: float in `[0.0, 1.0]`
- `status`: one of `proposed`, `accepted`, `disputed`, or `unpublished` (play-mode allowance)
- `created_at`: datetime when the claim record is created

Interpretation guidance:

- `accepted` does not mean absolute truth; it means currently preferred in-project interpretation.
- `disputed` should be used when explicit contradictions are modeled.
- Keep competing claims side-by-side; do not delete old claims when scholarly preference changes.

## Play Mode vs Source Requirements

- Preferred rule: every `Claim` is linked to at least one `Source`.
- Play mode allowance: a `Claim` may temporarily exist without `SUPPORTED_BY` edges if explicitly flagged as unpublished/manual:
  - `Claim.status = "unpublished"` or
  - equivalent manual provenance note in claim metadata.
- Publish mode expectation: claims should have explicit `SUPPORTED_BY` links and documented contradictions where relevant.

## Canonical Queries

### 1) Show competing etymologies for a lemma

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})
MATCH (c:Claim)-[:ASSERTS]->(l)
OPTIONAL MATCH (c)-[:ASSERTS]->(e:Etymon)
RETURN c.claim_id AS claim_id,
       c.type AS claim_type,
       c.statement AS statement,
       c.status AS status,
       c.confidence AS confidence,
       c.created_at AS created_at,
       collect(DISTINCT e.etymon_id) AS asserted_etymons
ORDER BY c.status, c.confidence DESC, c.created_at;
```

### 2) Show sources supporting each claim

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})
MATCH (c:Claim)-[:ASSERTS]->(l)
OPTIONAL MATCH (c)-[:SUPPORTED_BY]->(s:Source)
RETURN c.claim_id AS claim_id,
       c.status AS status,
       c.confidence AS confidence,
       collect(DISTINCT {
         source_id: s.source_id,
         citekey: s.citekey,
         title: s.title,
         year: s.year,
         url: s.url
       }) AS sources
ORDER BY c.confidence DESC, c.claim_id;
```

### 3) Show contradictions between claims

```cypher
MATCH (l:Lemma {lemma_id: $lemma_id})
MATCH (c1:Claim)-[:ASSERTS]->(l)
OPTIONAL MATCH (c1)-[:CONTRADICTS]->(c2:Claim)-[:ASSERTS]->(l)
RETURN c1.claim_id AS claim_id,
       c1.status AS claim_status,
       c2.claim_id AS contradicts_claim_id,
       c2.status AS contradicts_status
ORDER BY c1.claim_id, contradicts_claim_id;
```

## Modeling Rule of Thumb

- Put uncertainty in `Claim` nodes, not in destructive edits.
- Keep lineage edges (`DERIVES_FROM`, `BORROWED_FROM`) explicit and queryable.
- Keep source traceability first-class so later academic output is auditable.
