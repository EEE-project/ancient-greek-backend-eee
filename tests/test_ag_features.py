"""Tests for _ag_features.py — UD FEATS → TVM key mapping."""
import sys
import pytest
from ancient_greek_backend_eee._ag_features import (
    ag_verb_key, ag_noun_key, ag_adj_key, ag_pron_key,
    T_PRES, T_IMP, T_AOR, T_FUT, T_PERF, T_PLUP,
    V_ACT, V_MID, V_PASS,
    M_IND, M_SUB, M_OPT, M_IMP, M_INF, M_PART,
)


def test_constants_importable():
    assert all(len(c) == 1 for c in [T_PRES, T_IMP, T_AOR, T_FUT, T_PERF, T_PLUP])
    assert all(len(c) == 1 for c in [V_ACT, V_MID, V_PASS])
    assert all(len(c) == 1 for c in [M_IND, M_SUB, M_OPT, M_IMP, M_INF, M_PART])


def test_no_library_dep():
    assert "greek_inflexion_eee" not in sys.modules


# --- ag_verb_key: present active indicative ---

def test_verb_pres_act_ind_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}) == "PAI.1S"

def test_verb_pres_act_ind_2s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "2", "Number": "Sing"}) == "PAI.2S"

def test_verb_pres_act_ind_3s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "3", "Number": "Sing"}) == "PAI.3S"

def test_verb_pres_act_ind_1p():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Plur"}) == "PAI.1P"


# --- ag_verb_key: other tenses ---

def test_verb_imp_act_ind_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Imp", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}) == "IAI.1S"

def test_verb_aor_act_ind_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Aor", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}) == "AAI.1S"

def test_verb_aor_pass_ind_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Aor", "Voice": "Pass", "Mood": "Ind", "Person": "1", "Number": "Sing"}) == "API.1S"

def test_verb_perf_act_ind_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Perf", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}) == "XAI.1S"

def test_verb_fut_act_ind_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Fut", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}) == "FAI.1S"


# --- ag_verb_key: moods ---

def test_verb_pres_act_sub_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Sub", "Person": "1", "Number": "Sing"}) == "PAS.1S"

def test_verb_pres_act_opt_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Opt", "Person": "1", "Number": "Sing"}) == "PAO.1S"

def test_verb_pres_act_imp_2s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Imp", "Person": "2", "Number": "Sing"}) == "PAD.2S"


# --- ag_verb_key: infinitive and participle ---

def test_verb_pres_act_inf():
    assert ag_verb_key({"VerbForm": "Inf", "Tense": "Pres", "Voice": "Act"}) == "PAN"

def test_verb_pres_act_part_nsm():
    assert ag_verb_key({"VerbForm": "Part", "Tense": "Pres", "Voice": "Act", "Case": "Nom", "Number": "Sing", "Gender": "Masc"}) == "PAP.NSM"

def test_verb_aor_pass_part_gpf():
    assert ag_verb_key({"VerbForm": "Part", "Tense": "Aor", "Voice": "Pass", "Case": "Gen", "Number": "Plur", "Gender": "Fem"}) == "APP.GPF"


# --- ag_verb_key: middle and Mid,Pass ---

def test_verb_pres_mid_ind_1s():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Mid", "Mood": "Ind", "Person": "1", "Number": "Sing"}) == "PMI.1S"

def test_verb_midpass_returns_none_pres():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Mid,Pass", "Mood": "Ind", "Person": "1", "Number": "Sing"}) is None

def test_verb_midpass_returns_none_aor():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Aor", "Voice": "Mid,Pass", "Mood": "Ind", "Person": "1", "Number": "Sing"}) is None


# --- ag_verb_key: dual ---

def test_verb_pres_act_ind_2d():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "2", "Number": "Dual"}) == "PAI.2D"

def test_verb_pres_act_ind_3d():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "3", "Number": "Dual"}) == "PAI.3D"


# --- ag_verb_key: edge cases ---

def test_verb_unknown_feature_ignored():
    assert ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing", "Polarity": "Neg"}) == "PAI.1S"

def test_verb_missing_verbform_raises():
    with pytest.raises(KeyError):
        ag_verb_key({"Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"})

def test_verb_missing_tense_raises():
    with pytest.raises(KeyError):
        ag_verb_key({"VerbForm": "Fin", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"})

def test_verb_missing_person_raises():
    with pytest.raises(KeyError):
        ag_verb_key({"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Number": "Sing"})


# --- ag_noun_key ---

def test_noun_nsm():
    assert ag_noun_key({"Case": "Nom", "Number": "Sing", "Gender": "Masc"}) == ".NSM"

def test_noun_apf():
    assert ag_noun_key({"Case": "Acc", "Number": "Plur", "Gender": "Fem"}) == ".APF"

def test_noun_gsn():
    assert ag_noun_key({"Case": "Gen", "Number": "Sing", "Gender": "Neut"}) == ".GSN"

def test_noun_dpm():
    assert ag_noun_key({"Case": "Dat", "Number": "Plur", "Gender": "Masc"}) == ".DPM"

def test_noun_vsm():
    assert ag_noun_key({"Case": "Voc", "Number": "Sing", "Gender": "Masc"}) == ".VSM"

def test_noun_no_gender_returns_none():
    assert ag_noun_key({"Case": "Nom", "Number": "Sing"}) is None

def test_noun_missing_case_raises():
    with pytest.raises(KeyError):
        ag_noun_key({"Number": "Sing", "Gender": "Masc"})

def test_noun_missing_number_raises():
    with pytest.raises(KeyError):
        ag_noun_key({"Case": "Nom", "Gender": "Masc"})

def test_noun_unknown_feature_ignored():
    assert ag_noun_key({"Case": "Nom", "Number": "Sing", "Gender": "Masc", "Animacy": "Anim"}) == ".NSM"


# --- ag_adj_key ---

def test_adj_pos_nsm():
    assert ag_adj_key({"Case": "Nom", "Number": "Sing", "Gender": "Masc", "Degree": "Pos"}) == ".NSM"

def test_adj_cmp_nsf():
    assert ag_adj_key({"Case": "Nom", "Number": "Sing", "Gender": "Fem", "Degree": "Cmp"}) == ".NSF"

def test_adj_sup_apn():
    assert ag_adj_key({"Case": "Acc", "Number": "Plur", "Gender": "Neut", "Degree": "Sup"}) == ".APN"

def test_adj_no_gender_returns_none():
    assert ag_adj_key({"Case": "Nom", "Number": "Sing", "Degree": "Pos"}) is None

def test_adj_missing_case_raises():
    with pytest.raises(KeyError):
        ag_adj_key({"Number": "Sing", "Gender": "Masc", "Degree": "Pos"})

def test_adj_missing_number_raises():
    with pytest.raises(KeyError):
        ag_adj_key({"Case": "Nom", "Gender": "Masc", "Degree": "Pos"})


# --- ag_pron_key: Gender-present family (demonstrative/relative/
# interrogative/indefinite/reciprocal) — same shape as ag_adj_key ---

def test_pron_key_gender_shape_matches_adj_key_composition():
    """Gender-bearing features produce the identical .CSG string ag_adj_key
    would produce for the same Case/Number/Gender (PronType ignored for
    this composition per Phase 4a's Gender-presence branch)."""
    features = {"Case": "Nom", "Number": "Sing", "Gender": "Masc", "PronType": "Dem"}
    adj_features = {"Case": "Nom", "Number": "Sing", "Gender": "Masc", "Degree": "Pos"}
    assert ag_pron_key(features) == ag_adj_key(adj_features) == ".NSM"


@pytest.mark.parametrize("prontype", ["Dem", "Rel", "Int", "Ind", "Rcp"])
def test_pron_key_gender_shape_covers_every_non_personal_prontype(prontype):
    """All five non-personal PronType values are grouped into the
    Gender-present / adjective-like branch per the plan's explicit design
    (demonstrative/relative/interrogative/indefinite/reciprocal all
    decline Case x Number x Gender)."""
    result = ag_pron_key({"Case": "Gen", "Number": "Plur", "Gender": "Fem", "PronType": prontype})
    assert result == ".GPF"


def test_pron_key_missing_case_raises():
    with pytest.raises(KeyError):
        ag_pron_key({"Number": "Sing", "Gender": "Masc", "PronType": "Dem"})


def test_pron_key_missing_number_raises():
    with pytest.raises(KeyError):
        ag_pron_key({"Case": "Nom", "Gender": "Masc", "PronType": "Dem"})


# --- ag_pron_key: Person-present family (personal pronouns, no Gender) ---

def test_pron_key_person_shape_no_gender_present():
    """Gender absent, Person present -> the new Case+Number+Person shape,
    NOT the None 'union across genders' sentinel ag_noun_key/ag_adj_key
    use for Gender-absence (that sentinel meaning doesn't transfer here —
    Gender's absence is the *normal* case for personal pronouns, not a
    caller omission)."""
    result = ag_pron_key({"Case": "Nom", "Number": "Sing", "Person": "1", "PronType": "Prs"})
    assert result is not None


def test_pron_key_person_shape_literal_string():
    """Concrete shape check, matching section-03's undotted forms: keys
    (NS1) with this file's own dot-prefixed cache/tag-string convention."""
    assert ag_pron_key({"Case": "Nom", "Number": "Sing", "Person": "1", "PronType": "Prs"}) == ".NS1"
    assert ag_pron_key({"Case": "Gen", "Number": "Dual", "Person": "2", "PronType": "Prs"}) == ".GD2"


def test_pron_key_person_shape_distinguishes_number():
    """Sing/Dual/Plur must each produce a distinct key for the same
    Case+Person -- this exercises the one paradigm axis (dual) that only
    verbs have had until now."""
    keys = {
        ag_pron_key({"Case": "Nom", "Number": n, "Person": "1", "PronType": "Prs"})
        for n in ("Sing", "Dual", "Plur")
    }
    assert len(keys) == 3


def test_pron_key_person_shape_distinguishes_person():
    key_1 = ag_pron_key({"Case": "Nom", "Number": "Sing", "Person": "1", "PronType": "Prs"})
    key_2 = ag_pron_key({"Case": "Nom", "Number": "Sing", "Person": "2", "PronType": "Prs"})
    assert key_1 != key_2


def test_pron_key_person_shape_missing_person_raises():
    with pytest.raises(KeyError):
        ag_pron_key({"Case": "Nom", "Number": "Sing", "PronType": "Prs"})
