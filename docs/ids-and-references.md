# IDs and References

Related docs: [Invariants](invariants.md), [Schema](schema.md), [Hávamál Source Notes](ingest/havamal-source-notes.md)

## Deterministic ID Conventions

- `work_id`: stable slug, example `havamal`
- `edition_id`: source/version slug, example `havamal_gudni_jonsson_print`
- `segment_id`: source-structured deterministic id
- `token_id`: deterministic id derived from segment + token index
- `form_id`: deterministic language+orthography id, currently example `non:<surface>` in Sprint 1 ingest
- `lemma_id`: deterministic language+headword id (placeholder strategy currently)
- `claim_id`: deterministic hash/key over claim type + target + statement + source
- `source_id`: deterministic key from citekey/reference identity

## Hávamál Segment Reference Format

Current ingest target format:

- Segment ID: `<edition_id>:v<verse>:s<strophe>:l<line_index>`
- Segment ref property: `<verse><strophe><line_index>`
  Example: `I.1.0`

## Token ID Format

- `<segment_id>:t<index>`
- Example: `havamal_gudni_jonsson_print:vI.:s1.:l0:t0`

## Guidelines for Messy Sources

- Preserve raw source identifiers whenever possible.
- If source identifiers are inconsistent, normalize deterministically and document the transform.
- Never use random UUIDs in ingest IDs.
- Prefer explicit source position fields (`verse`, `strophe`, `line_index`) over opaque IDs.
- If fallback IDs are unavoidable, make fallback rule deterministic and adapter-local.
