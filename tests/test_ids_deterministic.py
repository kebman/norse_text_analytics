from __future__ import annotations

from nta.model import ids


def test_work_id_is_case_and_whitespace_insensitive() -> None:
    a = ids.work_id("  My Work  ")
    b = ids.work_id("my work")
    assert a == b
    assert " " not in a


def test_edition_id_is_deterministic_for_normalized_input() -> None:
    a = ids.edition_id(" Havamal ", " Gudni  Jonsson ", " V1 ")
    b = ids.edition_id("havamal", "gudni jonsson", "v1")
    assert a == b
    assert a.startswith("edition:")


def test_form_and_lemma_ids_have_expected_prefixes() -> None:
    form = ids.form_id("Old Norse", "Nóregr")
    lemma = ids.lemma_id("Old Norse", "Nóregr")
    assert form.startswith("form:")
    assert lemma.startswith("lemma:")


def test_morph_analysis_id_normalizes_analyzer_name() -> None:
    a = ids.morph_analysis_id("seg1:t0", " Placeholder ")
    b = ids.morph_analysis_id("seg1:t0", "placeholder")
    assert a == b
    assert a.endswith(":placeholder")


def test_claim_id_is_deterministic_and_changes_with_statement() -> None:
    a = ids.claim_id("ETYMOLOGY", "lemma:1", "same statement", "source:1")
    b = ids.claim_id("etymology", " lemma:1 ", " same  statement ", " source:1 ")
    c = ids.claim_id("etymology", "lemma:1", "different statement", "source:1")
    assert a == b
    assert a != c
    assert a.startswith("claim:")

