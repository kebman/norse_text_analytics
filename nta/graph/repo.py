from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from neo4j import Driver

from nta.graph.db import apply_schema as apply_schema_statements
from nta.model.types import Claim
from nta.model.types import Edition
from nta.model.types import Feature
from nta.model.types import Form
from nta.model.types import Lemma
from nta.model.types import MorphAnalysis
from nta.model.types import Segment
from nta.model.types import Source
from nta.model.types import Token
from nta.model.types import Work


_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


class Neo4jRepository:
    """Thin persistence layer for graph upserts and links."""

    def __init__(self, driver: Driver, schema_path: str | Path | None = None) -> None:
        self._driver = driver
        self._schema_path = schema_path

    def apply_schema(self) -> None:
        apply_schema_statements(self._driver, self._schema_path)

    def upsert_work(self, work: Work) -> None:
        self._execute(
            """
            MERGE (w:Work {work_id: $work_id})
            SET w.title = $title
            """,
            work_id=work.work_id,
            title=work.title,
        )

    def upsert_edition(self, edition: Edition) -> None:
        self._execute(
            """
            MERGE (e:Edition {edition_id: $edition_id})
            SET e.label = $label, e.version = $version
            """,
            edition_id=edition.edition_id,
            label=edition.label,
            version=edition.version,
        )

    def upsert_segment(self, segment: Segment) -> None:
        self._execute(
            """
            MERGE (s:Segment {segment_id: $segment_id})
            SET s.text = $text, s.position = $position, s.ref = $ref
            """,
            segment_id=segment.segment_id,
            text=segment.text,
            position=segment.position,
            ref=segment.ref,
        )

    def upsert_form(self, form: Form) -> None:
        self._execute(
            """
            MERGE (f:Form {form_id: $form_id})
            SET f.orthography = $orthography, f.language = $language
            """,
            form_id=form.form_id,
            orthography=form.orthography,
            language=form.language,
        )

    def upsert_token_and_form(self, token: Token, form: Form) -> None:
        self._execute(
            """
            MERGE (t:Token {token_id: $token_id})
            SET t.surface = $surface, t.position = $position, t.normalized = $normalized
            MERGE (f:Form {form_id: $form_id})
            SET f.orthography = $orthography, f.language = $language
            MERGE (t)-[:INSTANCE_OF_FORM]->(f)
            """,
            token_id=token.token_id,
            surface=token.surface,
            position=token.position,
            normalized=token.normalized,
            form_id=form.form_id,
            orthography=form.orthography,
            language=form.language,
        )

    def upsert_lemma(self, lemma: Lemma) -> None:
        self._execute(
            """
            MERGE (l:Lemma {lemma_id: $lemma_id})
            SET l.headword = $headword, l.language = $language, l.pos = $pos
            """,
            lemma_id=lemma.lemma_id,
            headword=lemma.headword,
            language=lemma.language,
            pos=lemma.pos,
        )

    def upsert_morph_analysis(self, analysis: MorphAnalysis) -> None:
        self._execute(
            """
            MERGE (m:MorphAnalysis {analysis_id: $analysis_id})
            SET m.analyzer = $analyzer,
                m.confidence = $confidence,
                m.pos = $pos,
                m.is_ambiguous = $is_ambiguous
            """,
            analysis_id=analysis.analysis_id,
            analyzer=analysis.analyzer,
            confidence=analysis.confidence,
            pos=analysis.pos,
            is_ambiguous=analysis.is_ambiguous,
        )

    def upsert_feature(self, feature: Feature) -> None:
        self._execute(
            """
            MERGE (f:Feature {key: $key, value: $value})
            SET f.lemma_guess = $lemma_guess
            """,
            key=feature.key,
            value=feature.value,
            lemma_guess=feature.lemma_guess,
        )

    def upsert_claim(self, claim: Claim) -> None:
        self._execute(
            """
            MERGE (c:Claim {claim_id: $claim_id})
            SET c.type = $type,
                c.statement = $statement,
                c.confidence = $confidence,
                c.status = $status
            """,
            claim_id=claim.claim_id,
            type=claim.type,
            statement=claim.statement,
            confidence=claim.confidence,
            status=claim.status,
        )

    def upsert_source(self, source: Source) -> None:
        self._execute(
            """
            MERGE (s:Source {source_id: $source_id})
            SET s.citekey = $citekey,
                s.title = $title,
                s.year = $year,
                s.authors = $authors,
                s.url = $url
            """,
            source_id=source.source_id,
            citekey=source.citekey,
            title=source.title,
            year=source.year,
            authors=list(source.authors) if source.authors is not None else None,
            url=source.url,
        )

    def link_work_edition(self, work_id: str, edition_id: str) -> None:
        self._execute(
            """
            MERGE (w:Work {work_id: $work_id})
            MERGE (e:Edition {edition_id: $edition_id})
            MERGE (w)-[:HAS_EDITION]->(e)
            """,
            work_id=work_id,
            edition_id=edition_id,
        )

    def link_edition_translates(
        self, translation_edition_id: str, source_edition_id: str
    ) -> None:
        self._execute(
            """
            MERGE (translation:Edition {edition_id: $translation_edition_id})
            MERGE (source:Edition {edition_id: $source_edition_id})
            MERGE (translation)-[:TRANSLATES]->(source)
            """,
            translation_edition_id=translation_edition_id,
            source_edition_id=source_edition_id,
        )

    def link_edition_segment(self, edition_id: str, segment_id: str) -> None:
        self._execute(
            """
            MERGE (e:Edition {edition_id: $edition_id})
            MERGE (s:Segment {segment_id: $segment_id})
            MERGE (e)-[:HAS_SEGMENT]->(s)
            """,
            edition_id=edition_id,
            segment_id=segment_id,
        )

    def link_segment_token(self, segment_id: str, token_id: str) -> None:
        self._execute(
            """
            MERGE (s:Segment {segment_id: $segment_id})
            MERGE (t:Token {token_id: $token_id})
            MERGE (s)-[:HAS_TOKEN]->(t)
            """,
            segment_id=segment_id,
            token_id=token_id,
        )

    def link_segment_aligned_to(
        self,
        segment_id: str,
        aligned_segment_id: str,
        method: str,
        confidence: float,
    ) -> None:
        self._execute(
            """
            MERGE (a:Segment {segment_id: $segment_id})
            MERGE (b:Segment {segment_id: $aligned_segment_id})
            MERGE (a)-[r:ALIGNED_TO]->(b)
            SET r.method = $method, r.confidence = $confidence
            """,
            segment_id=segment_id,
            aligned_segment_id=aligned_segment_id,
            method=method,
            confidence=confidence,
        )

    def link_token_form(self, token_id: str, form_id: str) -> None:
        self._execute(
            """
            MERGE (t:Token {token_id: $token_id})
            MERGE (f:Form {form_id: $form_id})
            MERGE (t)-[:INSTANCE_OF_FORM]->(f)
            """,
            token_id=token_id,
            form_id=form_id,
        )

    def link_token_analysis(self, token_id: str, analysis_id: str) -> None:
        self._execute(
            """
            MERGE (t:Token {token_id: $token_id})
            MERGE (m:MorphAnalysis {analysis_id: $analysis_id})
            MERGE (t)-[:HAS_ANALYSIS]->(m)
            """,
            token_id=token_id,
            analysis_id=analysis_id,
        )

    def link_analysis_feature(self, analysis_id: str, key: str, value: str) -> None:
        self._execute(
            """
            MERGE (m:MorphAnalysis {analysis_id: $analysis_id})
            MERGE (f:Feature {key: $key, value: $value})
            MERGE (m)-[:HAS_FEATURE]->(f)
            """,
            analysis_id=analysis_id,
            key=key,
            value=value,
        )

    def link_analysis_lemma(self, analysis_id: str, lemma_id: str) -> None:
        self._execute(
            """
            MERGE (m:MorphAnalysis {analysis_id: $analysis_id})
            MERGE (l:Lemma {lemma_id: $lemma_id})
            MERGE (m)-[:ANALYZES_AS]->(l)
            """,
            analysis_id=analysis_id,
            lemma_id=lemma_id,
        )

    def link_form_lemma(self, form_id: str, lemma_id: str) -> None:
        self._execute(
            """
            MERGE (f:Form {form_id: $form_id})
            MERGE (l:Lemma {lemma_id: $lemma_id})
            MERGE (f)-[:REALIZES]->(l)
            """,
            form_id=form_id,
            lemma_id=lemma_id,
        )

    def link_form_orthographic_variant(
        self, form_id: str, normalized_form_id: str, variant_type: str
    ) -> None:
        self._execute(
            """
            MERGE (surface:Form {form_id: $form_id})
            MERGE (normalized:Form {form_id: $normalized_form_id})
            MERGE (surface)-[r:ORTHOGRAPHIC_VARIANT_OF]->(normalized)
            SET r.type = $variant_type
            """,
            form_id=form_id,
            normalized_form_id=normalized_form_id,
            variant_type=variant_type,
        )

    def link_token_normalized_to(self, token_id: str, form_id: str, policy: str) -> None:
        self._execute(
            """
            MERGE (t:Token {token_id: $token_id})
            MERGE (f:Form {form_id: $form_id})
            MERGE (t)-[r:NORMALIZED_TO]->(f)
            SET r.policy = $policy
            """,
            token_id=token_id,
            form_id=form_id,
            policy=policy,
        )

    def link_claim_supported_by(self, claim_id: str, source_id: str) -> None:
        self._execute(
            """
            MERGE (c:Claim {claim_id: $claim_id})
            MERGE (s:Source {source_id: $source_id})
            MERGE (c)-[:SUPPORTED_BY]->(s)
            """,
            claim_id=claim_id,
            source_id=source_id,
        )

    def link_claim_asserts(
        self,
        claim_id: str,
        target_label: str,
        target_id_field: str,
        target_id: str,
    ) -> None:
        self._validate_identifier(target_label)
        self._validate_identifier(target_id_field)

        query = f"""
        MERGE (c:Claim {{claim_id: $claim_id}})
        MERGE (n:{target_label} {{{target_id_field}: $target_id}})
        MERGE (c)-[:ASSERTS]->(n)
        """
        self._execute(query, claim_id=claim_id, target_id=target_id)

    def link_claim_asserts_lemma(self, claim_id: str, lemma_id: str) -> None:
        self.link_claim_asserts(
            claim_id=claim_id,
            target_label="Lemma",
            target_id_field="lemma_id",
            target_id=lemma_id,
        )

    def link_claim_asserts_etymon(self, claim_id: str, etymon_id: str) -> None:
        self.link_claim_asserts(
            claim_id=claim_id,
            target_label="Etymon",
            target_id_field="etymon_id",
            target_id=etymon_id,
        )

    def link_claim_contradicts(self, claim_id: str, other_claim_id: str) -> None:
        self._execute(
            """
            MERGE (c1:Claim {claim_id: $claim_id})
            MERGE (c2:Claim {claim_id: $other_claim_id})
            MERGE (c1)-[:CONTRADICTS]->(c2)
            """,
            claim_id=claim_id,
            other_claim_id=other_claim_id,
        )

    # Backward-compatible aliases.
    def link_claim_source(self, claim_id: str, source_id: str) -> None:
        self.link_claim_supported_by(claim_id=claim_id, source_id=source_id)

    def link_claim_about(
        self,
        claim_id: str,
        target_label: str,
        target_id_field: str,
        target_id: str,
    ) -> None:
        self.link_claim_asserts(
            claim_id=claim_id,
            target_label=target_label,
            target_id_field=target_id_field,
            target_id=target_id,
        )

    def _execute(self, query: str, **params: Any) -> None:
        with self._driver.session() as session:
            session.run(query, **params).consume()

    @staticmethod
    def _validate_identifier(value: str) -> None:
        if not _IDENTIFIER_RE.match(value):
            raise ValueError(f"Unsafe identifier: {value}")
