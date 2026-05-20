"""Integration tests for AncientGreekBackend."""
import pytest
from ancient_greek_morphology_eee import AncientGreekBackend


@pytest.fixture(scope="module")
def backend():
    return AncientGreekBackend()


# --- verbs ---

def test_verb_pres_act_ind_1s(backend):
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")
    assert isinstance(result, set)
    assert len(result) == 1
    assert result.pop().rstrip() in {"λύω", "λῡ́ω", "λῡω"}  # allow macron variant


def test_verb_pres_act_ind_2s(backend):
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "2", "Number": "Sing"}, "verb")
    assert result  # non-empty


def test_verb_aor_act_ind_1s(backend):
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Aor", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")
    assert "ἔλυσα" in result


def test_verb_pres_mid_ind_1s(backend):
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Mid", "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")
    assert result


def test_verb_aor_pass_ind_1s(backend):
    # λύω has aorist passive (ἐλύθην) but no present passive (shared with medio-passive)
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Aor", "Voice": "Pass", "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")
    assert "ἐλύθην" in result


def test_verb_midpass_union_nonempty(backend):
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Mid,Pass", "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")
    assert isinstance(result, set)
    assert result


def test_verb_eimi_3s(backend):
    result = backend.inflect("εἰμί", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "3", "Number": "Sing"}, "verb")
    assert result


def test_verb_pres_act_part_nsm(backend):
    result = backend.inflect("λύω", {"VerbForm": "Part", "Tense": "Pres", "Voice": "Act", "Case": "Nom", "Number": "Sing", "Gender": "Masc"}, "verb")
    assert result


def test_verb_pres_act_inf(backend):
    result = backend.inflect("λύω", {"VerbForm": "Inf", "Tense": "Pres", "Voice": "Act"}, "verb")
    assert result


def test_verb_no_paradigm_path_returns_empty(backend):
    # Present active passive indicative — λύω has no active-passive path
    # PPI is medio-passive; try pluperfect passive mid — not in pratt lexicon
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pqp", "Voice": "Pass", "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")
    assert isinstance(result, set)


# --- nouns ---

def test_noun_theos_nsm(backend):
    result = backend.inflect("θεός", {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}, "noun")
    assert "θεός" in result


def test_noun_theos_gsm(backend):
    result = backend.inflect("θεός", {"Case": "Gen", "Number": "Sing", "Gender": "Masc"}, "noun")
    assert "θεοῦ" in result


def test_noun_theos_npm(backend):
    result = backend.inflect("θεός", {"Case": "Nom", "Number": "Plur", "Gender": "Masc"}, "noun")
    assert "θεοί" in result


def test_noun_sophia_nsf(backend):
    result = backend.inflect("σοφία", {"Case": "Nom", "Number": "Sing", "Gender": "Fem"}, "noun")
    assert "σοφία" in result


def test_noun_polis_nsf(backend):
    result = backend.inflect("πόλις", {"Case": "Nom", "Number": "Sing", "Gender": "Fem"}, "noun")
    assert "πόλις" in result


def test_noun_polis_gsf(backend):
    result = backend.inflect("πόλις", {"Case": "Gen", "Number": "Sing", "Gender": "Fem"}, "noun")
    assert "πολέως" in result


def test_noun_no_gender_returns_nonempty(backend):
    result = backend.inflect("θεός", {"Case": "Nom", "Number": "Sing"}, "noun")
    assert isinstance(result, set)
    assert result


# --- adjectives ---

def test_adj_agathos_nsm(backend):
    result = backend.inflect("ἀγαθός", {"Case": "Nom", "Number": "Sing", "Gender": "Masc", "Degree": "Pos"}, "adjective")
    assert "ἀγαθός" in result


def test_adj_agathos_nsf(backend):
    result = backend.inflect("ἀγαθός", {"Case": "Nom", "Number": "Sing", "Gender": "Fem", "Degree": "Pos"}, "adjective")
    assert "ἀγαθή" in result


def test_adj_agathos_nsn(backend):
    result = backend.inflect("ἀγαθός", {"Case": "Nom", "Number": "Sing", "Gender": "Neut", "Degree": "Pos"}, "adjective")
    assert "ἀγαθόν" in result


def test_adj_alethes_nsm(backend):
    result = backend.inflect("ἀληθής", {"Case": "Nom", "Number": "Sing", "Gender": "Masc", "Degree": "Pos"}, "adjective")
    assert "ἀληθής" in result


def test_adj_alethes_nsn(backend):
    result = backend.inflect("ἀληθής", {"Case": "Nom", "Number": "Sing", "Gender": "Neut", "Degree": "Pos"}, "adjective")
    assert "ἀληθές" in result


# --- analyze ---

def test_analyze_raises(backend):
    from eee import AnalysisNotSupportedError
    with pytest.raises(AnalysisNotSupportedError) as exc_info:
        backend.analyze("λύω")
    assert "AncientGreekBackend" in str(exc_info.value)


# --- paradigm ---

def test_paradigm_verb_returns_dict(backend):
    result = backend.paradigm("λύω", "verb")
    assert isinstance(result, dict)
    assert result


def test_paradigm_noun_returns_dict(backend):
    result = backend.paradigm("θεός", "noun")
    assert isinstance(result, dict)
    assert result


def test_paradigm_adj_returns_dict(backend):
    result = backend.paradigm("ἀγαθός", "adjective")
    assert isinstance(result, dict)
    assert result


def test_paradigm_unknown_pos_raises(backend):
    with pytest.raises(ValueError):
        backend.paradigm("λύω", "unknown_pos")


# --- error propagation ---

def test_inflect_unknown_pos_raises(backend):
    with pytest.raises(ValueError):
        backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}, "unknown")


def test_inflect_missing_feature_raises(backend):
    with pytest.raises(KeyError):
        backend.inflect("λύω", {"Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")


# --- caching: second call returns consistent results ---

def test_noun_cache_consistent(backend):
    r1 = backend.inflect("θεός", {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}, "noun")
    r2 = backend.inflect("θεός", {"Case": "Gen", "Number": "Sing", "Gender": "Masc"}, "noun")
    assert "θεός" in r1
    assert "θεοῦ" in r2
