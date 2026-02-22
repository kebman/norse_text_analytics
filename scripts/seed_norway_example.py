from __future__ import annotations

import sys
from pathlib import Path

# Allow direct script execution from repo root without package installation.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from nta.graph.db import Neo4jConfig
from nta.graph.db import get_driver
from nta.graph.repo import Neo4jRepository
from nta.model import ids as model_ids
from nta.model.types import Claim
from nta.model.types import Form
from nta.model.types import Lemma
from nta.model.types import Source


def lemma_id(language: str, headword: str) -> str:
    # Keep lemma IDs simple and deterministic for documentation/testing.
    return f"{language}:{headword}"


def merge_lemma_link(
    driver: object,
    from_lemma_id: str,
    rel_type: str,
    to_lemma_id: str,
) -> None:
    # Relationship type is fixed in this script (no user input).
    if rel_type not in {"DERIVES_FROM", "BORROWED_FROM"}:
        raise ValueError(f"Unsupported relationship type: {rel_type}")

    query = f"""
    MERGE (a:Lemma {{lemma_id: $from_lemma_id}})
    MERGE (b:Lemma {{lemma_id: $to_lemma_id}})
    MERGE (a)-[:{rel_type}]->(b)
    """
    with driver.session() as session:
        session.run(query, from_lemma_id=from_lemma_id, to_lemma_id=to_lemma_id).consume()


def main() -> None:
    config = Neo4jConfig.from_env()
    driver = get_driver(config)
    repo = Neo4jRepository(driver)

    try:
        # Lemmas.
        lemmas = [
            Lemma(lemma_id=lemma_id("non", "Nóregr"), headword="Nóregr", language="non", pos="UNKNOWN"),
            Lemma(lemma_id=lemma_id("nn", "Noreg"), headword="Noreg", language="nn", pos="UNKNOWN"),
            Lemma(lemma_id=lemma_id("nb", "Norge"), headword="Norge", language="nb", pos="UNKNOWN"),
            Lemma(lemma_id=lemma_id("da", "Norge"), headword="Norge", language="da", pos="UNKNOWN"),
            Lemma(lemma_id=lemma_id("en", "Norway"), headword="Norway", language="en", pos="UNKNOWN"),
        ]
        for lemma in lemmas:
            repo.upsert_lemma(lemma)

        # Forms (at least one per primary lemma).
        forms = [
            Form(form_id=model_ids.form_id("non", "Nóregr"), orthography="Nóregr", language="non"),
            Form(form_id=model_ids.form_id("nn", "Noreg"), orthography="Noreg", language="nn"),
            Form(form_id=model_ids.form_id("nb", "Norge"), orthography="Norge", language="nb"),
            Form(form_id=model_ids.form_id("en", "Norway"), orthography="Norway", language="en"),
        ]
        for form in forms:
            repo.upsert_form(form)

        repo.link_form_lemma(model_ids.form_id("non", "Nóregr"), lemma_id("non", "Nóregr"))
        repo.link_form_lemma(model_ids.form_id("nn", "Noreg"), lemma_id("nn", "Noreg"))
        repo.link_form_lemma(model_ids.form_id("nb", "Norge"), lemma_id("nb", "Norge"))
        repo.link_form_lemma(model_ids.form_id("en", "Norway"), lemma_id("en", "Norway"))

        # Historical links.
        merge_lemma_link(driver, lemma_id("nn", "Noreg"), "DERIVES_FROM", lemma_id("non", "Nóregr"))
        merge_lemma_link(driver, lemma_id("nb", "Norge"), "DERIVES_FROM", lemma_id("da", "Norge"))
        merge_lemma_link(driver, lemma_id("da", "Norge"), "DERIVES_FROM", lemma_id("non", "Nóregr"))
        merge_lemma_link(driver, lemma_id("en", "Norway"), "BORROWED_FROM", lemma_id("non", "Nóregr"))

        # Competing etymology claims for Old Norse Nóregr.
        source_a = Source(
            source_id=model_ids.source_id("placeholder_nord_vegr"),
            citekey="placeholder_nord_vegr",
            title="Placeholder source for norð + vegr hypothesis",
            year=None,
            authors=None,
            url=None,
        )
        source_b = Source(
            source_id=model_ids.source_id("placeholder_nor_vegr"),
            citekey="placeholder_nor_vegr",
            title="Placeholder source for nór + vegr hypothesis",
            year=None,
            authors=None,
            url=None,
        )
        repo.upsert_source(source_a)
        repo.upsert_source(source_b)

        claim_a = Claim(
            claim_id=model_ids.claim_id(
                "etymology",
                lemma_id("non", "Nóregr"),
                "Nóregr derives from norð + vegr",
                source_a.source_id,
            ),
            type="etymology",
            statement="Nóregr derives from norð + vegr",
            confidence=0.5,
            status="PROPOSED",
        )
        claim_b = Claim(
            claim_id=model_ids.claim_id(
                "etymology",
                lemma_id("non", "Nóregr"),
                "Nóregr derives from nór + vegr",
                source_b.source_id,
            ),
            type="etymology",
            statement="Nóregr derives from nór + vegr",
            confidence=0.5,
            status="PROPOSED",
        )
        repo.upsert_claim(claim_a)
        repo.upsert_claim(claim_b)
        repo.link_claim_asserts_lemma(claim_a.claim_id, lemma_id("non", "Nóregr"))
        repo.link_claim_asserts_lemma(claim_b.claim_id, lemma_id("non", "Nóregr"))
        repo.link_claim_supported_by(claim_a.claim_id, source_a.source_id)
        repo.link_claim_supported_by(claim_b.claim_id, source_b.source_id)
        repo.link_claim_contradicts(claim_a.claim_id, claim_b.claim_id)
        repo.link_claim_contradicts(claim_b.claim_id, claim_a.claim_id)

        print("Seeded Norway example graph data.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
