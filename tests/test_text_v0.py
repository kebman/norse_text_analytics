from __future__ import annotations

from nta.ingest.text import NORMALIZATION_POLICY_V0
from nta.ingest.text import SURROUNDING_PUNCT
from nta.ingest.text import normalize_v0
from nta.ingest.text import tokenize_v0


def test_policy_string_is_stable() -> None:
    assert NORMALIZATION_POLICY_V0 == "punct_strip_whitespace_collapse_v0"


def test_surrounding_punct_contains_unicode_quotes() -> None:
    assert "“" in SURROUNDING_PUNCT
    assert "”" in SURROUNDING_PUNCT
    assert "‘" in SURROUNDING_PUNCT
    assert "’" in SURROUNDING_PUNCT


def test_normalize_v0_strips_surrounding_punctuation_and_collapses_whitespace() -> None:
    assert normalize_v0('  "Hávamál"...  ') == "Hávamál"
    assert normalize_v0(" \t halló   \n  heimur \r ") == "halló heimur"


def test_normalize_v0_handles_unicode_quotes() -> None:
    assert normalize_v0("“Nóregr”") == "Nóregr"


def test_tokenize_v0_splits_whitespace_and_skips_empty_tokens() -> None:
    line = "  “Nóregr”,  ok -- Ísland!  "
    assert tokenize_v0(line) == ["Nóregr", "ok", "Ísland"]


def test_tokenize_v0_preserves_internal_punctuation() -> None:
    assert tokenize_v0("foo-bar -- baz") == ["foo-bar", "baz"]

