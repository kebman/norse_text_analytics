# Auto-Structuring Messy Text

Related docs: [Adapter Contract](adapter-contract.md), [IDs and References](../ids-and-references.md), [Ingest Overview](ingest-overview.md)

## What "Structuring" Means

Structuring is the step that turns messy raw text into deterministic ingest units:

- segment boundaries (`Segment`)
- segment references (`ref`, and optional `verse`/`strophe`/line fields)
- stable anchors used to derive deterministic IDs
- source metadata needed to interpret boundaries and provenance

Goal: produce repeatable structure from imperfect sources without bespoke JSON requirements.

## Structuring Levels

### L0: Ordinal Structure (always possible)

- Use line or paragraph ordinals.
- Examples:
  - `segment_id = <edition_id>:seg<ordinal>`
  - `ref = <ordinal>`
- Use when no stable source markers exist.

### L1: Regex-Derived Structure

- Detect explicit markers via deterministic regex rules.
- Typical targets:
  - verse numbering (`I.`, `II.`)
  - strophe numbering (`1.`, `2.`)
  - chapter/section headings
- Emit extracted markers into segment fields and refs.

### L2: Markup-Derived Structure

- Use structured markup boundaries from TEI/XML/HTML.
- Typical anchors:
  - TEI `<lg>`, `<l>`, `<div>`
  - HTML heading hierarchy and list blocks
- Keep extraction rules documented and deterministic.

### L3: Learned Structure (future; out of scope now)

- Model-assisted segmentation/classification.
- Must still emit deterministic adapter output for ingest.
- Not part of current Sprint-1 implementation.

## Determinism Rule

- Prefer deterministic, explainable methods.
- Heuristics must not silently change IDs across reruns.
- If a structuring rule changes, document it and version the edition/adapter configuration.
- Never mutate previously ingested evidence IDs in place.

## Structure Detection as Interpretation Layer

Recommended architecture:

- Keep evidence ingest stable at current anchor level.
- Run structure detection as a separate analyzer stage.
- Let that stage propose structure as `Claim` records (for example "segment X likely belongs to strophe Y"), instead of rewriting evidence.

This preserves serious-play flexibility while keeping history auditable.

## Practical Guidance

- Start at the lowest reliable level (L0/L1).
- Promote to richer levels only when rules are deterministic and testable.
- Prefer explicit fallback paths over brittle automatic inference.
