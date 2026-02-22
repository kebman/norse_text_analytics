# Language Stages

Related docs: [Schema](../schema.md), [Invariants](../invariants.md), [Data Model Philosophy](philosophy.md), [Glossary](../glossary.md)

## Purpose

Define a consistent way to represent historical language/stage/standard across `Edition` and `Lemma` so temporal and lineage queries stay comparable.

## Terms

- `language`: broad language family label (for example `Norwegian`, `Old Norse`).
- `stage`: historical phase within a language continuum (for example `Old`, `Middle`, `Modern`).
- `standard`: sociolinguistic or orthographic standard inside a stage (for example `Bokmål`, `Nynorsk`).

## Representation Strategy

- v1 (current, recommended): store `language_stage` as a controlled string on `Edition` and `Lemma`.
- Compatibility note: keep existing `language` property; `language_stage` refines it.
- Planned extension: add `(:LanguageStage)` nodes later and link from `Edition`/`Lemma` without changing existing IDs.
- Codes such as `on`, `own`, `oen`, `ois`, `onr`, `oda`, `osw`, `mnr`, `mda`, `msw` are project codes (not ISO 639 codes).

## Controlled Vocabulary (v1)

Use these values for `language_stage`:

| code | label | approximate dates | notes |
|---|---|---|---|
| `on` | Old Norse (ON) | c. 700-1350 | Umbrella historical stage for Norse vernaculars. |
| `own` | Old West Norse (OWN) | c. 800-1350 | West branch umbrella; includes Icelandic/Norwegian traditions. |
| `oen` | Old East Norse (OEN) | c. 800-1350 | East branch umbrella; includes Danish/Swedish traditions. |
| `ois` | Old Icelandic | c. 900-1350 | Literary/language stage; manuscript attestation mainly c. 1150-1350. |
| `onr` | Old Norwegian | c. 1100-1350 | Norwegian medieval Old Norse variety. |
| `oda` | Old Danish | c. 1100-1525 | Early Danish stage; pre-Reformation translation boundary. |
| `osw` | Old Swedish | c. 1225-1526 | Early Swedish stage. |
| `mnr` | Middle Norwegian | c. 1350-1537 | Transitional period; Black Death c. 1350 to Reformation 1536/37. |
| `mda` | Middle Danish | c. 1525-1700 | Transitional Danish period after old-stage boundary c. 1525. |
| `msw` | Middle Swedish | c. 1526-1732 | Transitional period anchored by 1526 NT and Dalin 1732 boundary. |
| `isl` | Modern Icelandic | c. 1550-present | Modern standard Icelandic. |
| `nb` | Norwegian Bokmål | c. 1907-present | Modern Norwegian written standard. |
| `nn` | Norwegian Nynorsk | c. 1853-present | Modern Norwegian written standard. |
| `sv` | Swedish | c. 1732-present | Modern standard Swedish (Dalin 1732 anchor). |
| `da` | Danish | c. 1700-present | Modern standard Danish. |
| `fo` | Faroese | c. 1850-present | Modern standard Faroese; Hammershaimb orthography 1846 anchor. |

Dates are approximate guidance for query grouping, not strict boundaries.

## Interoperability / Mapping

- `on`, `own`, `oen`, `ois`, `onr`, `oda`, `osw`, `mnr`, `mda`, `msw` are project codes for stage resolution and are not ISO 639 codes.
- ISO 639-3 `non` covers Old Norse broadly; ISO 639-3 does not provide distinct codes for Old West Norse, Old East Norse, Old Icelandic, or Old Norwegian.
- Modern identifiers `nb`, `nn`, `sv`, `da`, `fo`, `isl` are standard language identifiers and can be used directly in this project.

| project code | interoperability mapping |
|---|---|
| `on`, `own`, `oen`, `ois`, `onr`, `oda`, `osw`, `mnr`, `mda`, `msw` | ISO 639-3 `non` |
| `nb`, `nn`, `sv`, `da`, `fo`, `isl` | map to same code |

## Boundary Criteria

- Boundaries are approximate and intentionally pragmatic for query grouping.
- The table mixes criteria where appropriate: linguistic stage shifts, manuscript/literary attestation windows, orthographic standardization, and political/official recognition.
- Date anchors are used as operational cut points (for example 1525, 1526, 1536/37, 1732, 1846), not absolute linguistic breaks.
- When criteria conflict, prefer stable, documented boundaries and record uncertainty in notes/claims.

## Rules

- `Edition` must have `language_stage`.
- `Lemma` must have `language_stage` (or, during migration, at minimum `language` + explicit `stage` fields).
- Cross-stage and cross-language development is represented with `Lemma` lineage edges:
  - `(:Lemma)-[:DERIVES_FROM]->(:Lemma)`
  - `(:Lemma)-[:BORROWED_FROM]->(:Lemma)`
- Do not encode historical development solely in `language_stage` strings; use lineage edges for explicit causality.
- If uncertain, choose the broadest valid code (for example `on` instead of `own`) and document uncertainty in notes/claims.

## Migration Path to `LanguageStage` Nodes (Planned)

- Introduce `(:LanguageStage {code, label, date_start, date_end})`.
- Link with:
  - `(:Edition)-[:IN_STAGE]->(:LanguageStage)`
  - `(:Lemma)-[:IN_STAGE]->(:LanguageStage)`
- Keep `language_stage` property for backward compatibility during transition.
- Existing IDs remain stable; stage modeling can evolve without rekeying `Edition` or `Lemma`.
