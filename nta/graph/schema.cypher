// Translation/alignment primitives:
// (Edition)-[:TRANSLATES]->(Edition)
// (Segment)-[:ALIGNED_TO {method, confidence}]->(Segment)

CREATE CONSTRAINT work_work_id_unique IF NOT EXISTS
FOR (w:Work)
REQUIRE w.work_id IS UNIQUE;

CREATE CONSTRAINT edition_edition_id_unique IF NOT EXISTS
FOR (e:Edition)
REQUIRE e.edition_id IS UNIQUE;

CREATE CONSTRAINT segment_segment_id_unique IF NOT EXISTS
FOR (s:Segment)
REQUIRE s.segment_id IS UNIQUE;

CREATE CONSTRAINT token_token_id_unique IF NOT EXISTS
FOR (t:Token)
REQUIRE t.token_id IS UNIQUE;

CREATE CONSTRAINT form_form_id_unique IF NOT EXISTS
FOR (f:Form)
REQUIRE f.form_id IS UNIQUE;

CREATE CONSTRAINT lemma_lemma_id_unique IF NOT EXISTS
FOR (l:Lemma)
REQUIRE l.lemma_id IS UNIQUE;

CREATE CONSTRAINT witness_witness_id_unique IF NOT EXISTS
FOR (w:Witness)
REQUIRE w.witness_id IS UNIQUE;

CREATE CONSTRAINT sense_sense_id_unique IF NOT EXISTS
FOR (s:Sense)
REQUIRE s.sense_id IS UNIQUE;

CREATE CONSTRAINT morph_analysis_id_unique IF NOT EXISTS
FOR (m:MorphAnalysis)
REQUIRE m.analysis_id IS UNIQUE;

CREATE CONSTRAINT feature_key_value_unique IF NOT EXISTS
FOR (f:Feature)
REQUIRE (f.key, f.value) IS UNIQUE;

CREATE CONSTRAINT etymon_etymon_id_unique IF NOT EXISTS
FOR (e:Etymon)
REQUIRE e.etymon_id IS UNIQUE;

CREATE CONSTRAINT cognate_set_set_id_unique IF NOT EXISTS
FOR (c:CognateSet)
REQUIRE c.set_id IS UNIQUE;

CREATE CONSTRAINT claim_claim_id_unique IF NOT EXISTS
FOR (c:Claim)
REQUIRE c.claim_id IS UNIQUE;

CREATE CONSTRAINT source_source_id_unique IF NOT EXISTS
FOR (s:Source)
REQUIRE s.source_id IS UNIQUE;

CREATE INDEX token_surface_idx IF NOT EXISTS
FOR (t:Token)
ON (t.surface);

CREATE INDEX token_normalized_idx IF NOT EXISTS
FOR (t:Token)
ON (t.normalized);

CREATE INDEX form_orthography_idx IF NOT EXISTS
FOR (f:Form)
ON (f.orthography);

CREATE INDEX lemma_headword_idx IF NOT EXISTS
FOR (l:Lemma)
ON (l.headword);

CREATE INDEX segment_ref_idx IF NOT EXISTS
FOR (s:Segment)
ON (s.ref);

CREATE INDEX segment_segment_ref_idx IF NOT EXISTS
FOR (s:Segment)
ON (s.segment_ref);

CREATE INDEX source_citekey_idx IF NOT EXISTS
FOR (s:Source)
ON (s.citekey);

CREATE INDEX claim_type_idx IF NOT EXISTS
FOR (c:Claim)
ON (c.type);

CREATE INDEX morph_analysis_pos_idx IF NOT EXISTS
FOR (m:MorphAnalysis)
ON (m.pos);

CREATE INDEX feature_key_idx IF NOT EXISTS
FOR (f:Feature)
ON (f.key);

CREATE INDEX feature_value_idx IF NOT EXISTS
FOR (f:Feature)
ON (f.value);

CREATE INDEX edition_language_idx IF NOT EXISTS
FOR (e:Edition)
ON (e.language);

CREATE INDEX edition_date_start_idx IF NOT EXISTS
FOR (e:Edition)
ON (e.date_start);

CREATE INDEX edition_date_end_idx IF NOT EXISTS
FOR (e:Edition)
ON (e.date_end);

CREATE INDEX edition_source_label_idx IF NOT EXISTS
FOR (e:Edition)
ON (e.source_label);

CREATE INDEX aligned_to_method_idx IF NOT EXISTS
FOR ()-[r:ALIGNED_TO]-()
ON (r.method);

CREATE INDEX aligned_to_confidence_idx IF NOT EXISTS
FOR ()-[r:ALIGNED_TO]-()
ON (r.confidence);
