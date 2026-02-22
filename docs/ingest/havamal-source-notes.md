# Hávamál Source Notes

Related docs: [Ingest Overview](ingest-overview.md), [Adapter Contract](adapter-contract.md), [IDs and References](../ids-and-references.md)

## Source File

- `data/Hávamál1.json`

## Observed JSON Shape

- `information.cover[]` (strings)
- `information.writer[]` (strings)
- `poem.title` (string)
- `poem.verses[]`
  - `verse` (example `"I."`)
  - `strophes[]`
    - `strophe` (example `"1."`)
    - `lines[]` (strings)

## Current Mapping to Graph

- `Work`
  - `work_id = "havamal"`
- `Edition`
  - `edition_id = "havamal_gudni_jonsson_print"`
  - properties include: `title`, `cover`, `writer`, `language="Old Norse"`
  - dating/source metadata currently set as placeholders:
    - `source_label = "Sæmundar-Edda: Hávamál"`
    - `date_start = 900`, `date_end = 1100`, `date_approx = true`
    - `date_note = "placeholder; revise later"`
    - `provenance = "Guðni Jónsson print"`
- `Segment`
  - one node per line
  - `segment_id = <edition_id>:v<verse>:s<strophe>:l<line_index>`
  - properties: `verse`, `strophe`, `line_index`, `ref`, `text`
- `Token`
  - tokenized from segment text
  - `token_id = <segment_id>:t<token_index>`
  - properties: `surface`, `normalized`, `position`
- `Form`
  - one per `(language + surface)` in current ingest
  - `form_id = non:<surface>`

## Tokenization / Normalization (v0)

- Split on whitespace.
- Strip punctuation from token boundaries.
- Skip empty tokens.
- Normalize by stripping surrounding punctuation and collapsing whitespace.
- Preserve diacritics.
