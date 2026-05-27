"""End-to-end smoke tests via eee public API.

Uses eee.register_backend() for local testing — no entry point install needed.
"""
import pytest
import eee
from eee import AnalysisNotSupportedError
from ancient_greek_backend_eee import AncientGreekBackend


@pytest.fixture(autouse=True, scope="module")
def register_grc():
    eee.register_backend("grc", AncientGreekBackend())


def test_inflect_verb():
    result = eee.inflect(
        "λύω",
        {"VerbForm": "Fin", "Tense": "Aor", "Voice": "Act",
         "Mood": "Ind", "Person": "1", "Number": "Sing"},
        "verb",
        language="grc",
    )
    assert "ἔλυσα" in result


def test_inflect_noun():
    result = eee.inflect(
        "θεός",
        {"Case": "Nom", "Number": "Sing", "Gender": "Masc"},
        "noun",
        language="grc",
    )
    assert "θεός" in result


def test_inflect_adjective():
    result = eee.inflect(
        "ἀγαθός",
        {"Case": "Nom", "Number": "Sing", "Gender": "Masc", "Degree": "Pos"},
        "adjective",
        language="grc",
    )
    assert "ἀγαθός" in result


def test_analyze_raises():
    with pytest.raises(AnalysisNotSupportedError):
        eee.analyze("λόγου", language="grc")


def test_grc_in_supported_languages():
    # registered via register_backend — appears in registry state
    from eee._registry import _registered
    assert "grc" in _registered
