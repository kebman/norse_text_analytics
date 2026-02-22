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

## Controlled Vocabulary (v1)

Use these values for `language_stage`:

| code | label | approximate dates | notes |
|---|---|---|---|
| `on` | Old Norse (ON) | c. 700-1350 | Umbrella historical stage for Norse vernaculars. |
| `own` | Old West Norse (OWN) | c. 750-1350 | West branch umbrella; includes Icelandic/Norwegian traditions. |
| `oen` | Old East Norse (OEN) | c. 800-1350 | East branch umbrella; includes Danish/Swedish traditions. |
| `ois` | Old Icelandic | c. 1100-1350 | Literary variety in Icelandic manuscripts. |
| `onr` | Old Norwegian | c. 1100-1350 | Norwegian medieval Old Norse variety. |
| `oda` | Old Danish | c. 1100-1500 | Early Danish stage. |
| `osw` | Old Swedish | c. 1225-1526 | Early Swedish stage. |
| `mnr` | Middle Norwegian | c. 1350-1537 | Transitional Norwegian period. |
| `mda` | Middle Danish | c. 1500-1700 | Transitional Danish period. |
| `msw` | Middle Swedish | c. 1526-1732 | Transitional Swedish period. |
| `isl` | Modern Icelandic | c. 1550-present | Modern standard Icelandic. |
| `nb` | Norwegian Bokmål | c. 1907-present | Modern Norwegian written standard. |
| `nn` | Norwegian Nynorsk | c. 1853-present | Modern Norwegian written standard. |
| `sv` | Swedish | c. 1732-present | Modern standard Swedish. |
| `da` | Danish | c. 1700-present | Modern standard Danish. |
| `fo` | Faroese | c. 1900-present | Modern standard Faroese. |

Dates are approximate guidance for query grouping, not strict boundaries.

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
