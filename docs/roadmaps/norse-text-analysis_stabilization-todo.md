# Norse Text Analysis – Stabilization & Hygiene To-Do

_Status: Shelved temporarily (focus: Event Pass).  
Goal when resuming: Stabilize docs + schema, reduce drift, prepare for future scaling._

---

## Phase 0 — Re-entry (Low Cognitive Load)

- [ ] Skim `/docs/data-model/` to refresh schema mental model.
- [ ] Re-read `/docs/data-model/language-stages.md` after ISO + boundary fixes.
- [ ] Re-read `/docs/vision/serious-play.md` to re-anchor philosophy.
- [ ] Confirm no active schema renames pending.

**Outcome:** Mental context restored before touching anything structural.

---

## Phase 1 — Repo-Wide Docs Audit (Mechanical, Low Risk)

### Objective:
Eliminate drift, broken links, naming inconsistencies.

- [ ] Run Codex prompt: recursive `/docs` hygiene audit.
- [ ] Fix:
  - Broken relative links
  - Anchor mismatches
  - Typos
  - Code fence language tags
- [ ] Generate `/docs/reports/docs-audit.md`.

If changes are mechanical → auto-apply.  
If semantic → review manually.

**Outcome:** Clean, internally consistent documentation base.

---

## Phase 2 — Cypher Validation & Preconditions

### Objective:
Make every Cypher example deterministic and explicit.

- [ ] Have Codex extract all ```cypher blocks.
- [ ] Add precondition header to each:
  - Required sources
  - Required labels
  - Required indexes/constraints
  - Expected result shape
- [ ] Identify queries requiring ≥2 ingested sources.
- [ ] Flag queries referencing undefined labels/properties.
- [ ] Verify date fallback logic behaves as documented.

If trivial fixes → apply.  
If structural mismatch → pause and decide.

**Outcome:** Documentation-safe queries with declared dependencies.

---

## Phase 3 — Fixture Strategy (Optional but High ROI)

### Objective:
Prevent examples from silently breaking.

- [ ] Design minimal Neo4j fixture dataset plan.
- [ ] Define:
  - 2–3 sources
  - Overlapping lexemes
  - At least one messy/plaintext or HTML-ingested source
  - Multiple language stages
- [ ] Document fixture load procedure.

Do not implement full dataset yet — just define structure.

**Outcome:** Future-proof example reproducibility.

---

## Phase 4 — Language & Attestation Semantics Lock-In

### Objective:
Prevent long-term schema ambiguity.

Questions to explicitly resolve:

- [ ] Is language attached to:
  - Lexeme?
  - Attestation?
  - Form?
- [ ] Can a Lexeme exist independently of language?
- [ ] What distinguishes:
  - `attested_in`
  - `normalized_to`
  - `inferred_stage`
- [ ] Merge rules for lexemes across sources:
  - Exact normalized form?
  - Lemma authority?
  - Cross-language equivalence policy?
  - Manual alignment?

Create doc:
`/docs/data-model/attestation-and-language-semantics.md`

**Outcome:** No future identity drift.

---

## Phase 5 — Canonical Schema Enforcement

### Objective:
Single source of truth.

- [ ] Identify canonical schema doc.
- [ ] Ensure all other docs link to it.
- [ ] Remove duplicated schema definitions elsewhere.
- [ ] Verify:
  - Labels
  - Relationship types
  - Versioned/append-only semantics for interpretations
  - Property names
  - Index/constraint definitions

If schema renames are needed → stop and decide before applying.

**Outcome:** Drift-resistant architecture.

---

## Phase 5.5 — Ingestion & Idempotency Validation

### Objective:
Ensure real-world robustness beyond Hávamál JSON.

- [ ] Ingest at least one non-JSON source (plaintext or Heimskringla HTML).
- [ ] Re-run ingestion twice → confirm no duplication.
- [ ] Verify:
  - Stable segment IDs
  - Stable token IDs
  - No duplicate Forms/Lemmas
- [ ] Confirm queries work across ≥2 Editions.

**Outcome:** Multi-source stability proven.

---

## Phase 5.6 — Migration & Versioning Policy

### Objective:
Prevent silent breaking changes.

- [ ] Define schema versioning strategy (doc only for now).
- [ ] Decide migration approach (manual vs scripted).
- [ ] Document “breaking change” protocol.
- [ ] Tag a “schema-stable” milestone once complete.

**Outcome:** Future refactors are intentional, not accidental.

---

## Phase 6 — Strategic Pause

At this point, ask:

- Is architecture stable enough for institutional outreach?
- Are example queries compelling?
- Is ingestion reproducible?
- Are ≥2 heterogeneous sources ingested successfully?
- Is idempotency confirmed?
- Are indexes actually used (PROFILE critical queries)?
- Can the DB be exported and re-imported reproducibly?

If yes → consider outreach.  
If no → iterate quietly.

---

# Priority Order (When Returning)

1. Phase 1 (Docs audit) — easiest win
2. Phase 2 (Cypher preconditions)
3. Phase 4 (Language semantics decision)
4. Phase 5 (Schema consolidation)
5. Phase 3 (Fixtures)

---

# Constraint Reminder

- Only auto-fix mechanical inconsistencies.
- Anything semantic → ask before modifying.
- Avoid large renames without version bump.

---

# Meta

This project is promising.  
Do not let it drift because of parallel work.

When returning:
- Pick ONE phase.
- Finish it fully.
- Commit cleanly.
