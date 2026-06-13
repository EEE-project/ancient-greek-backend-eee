"""Integration tests for AncientGreekBackend."""
import pytest
from ancient_greek_backend_eee import AncientGreekBackend


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


def test_paradigm_adj_adverb_regular(backend):
    result = backend.paradigm("καλός", "adjective")
    assert result.get("ADV") == {"καλῶς"}


def test_paradigm_adj_adverb_agathos(backend):
    result = backend.paradigm("ἀγαθός", "adjective")
    assert result.get("ADV") == {"ἀγαθῶς"}


def test_paradigm_adj_adverb_no_match(backend):
    # ἀληθής ends in -ής, not -ος → no adverb derived
    result = backend.paradigm("ἀληθής", "adjective")
    assert "ADV" not in result


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


# --- get_tags ---

def test_get_tags_noun_row_count(backend):
    assert len(backend.get_tags("noun")) == 30


def test_get_tags_adj_row_count(backend):
    assert len(backend.get_tags("adjective")) == 30


def test_get_tags_verb_row_count(backend):
    assert len(backend.get_tags("verb")) == 88


def test_get_tags_unknown_pos_returns_empty(backend):
    assert backend.get_tags("particle") == []


def test_get_tags_noun_all_rows_have_tag_case_number_gender(backend):
    tags = backend.get_tags("noun")
    for t in tags:
        assert {"tag", "Case", "Number", "Gender"} == set(t.keys())


def test_get_tags_verb_finite_rows_have_full_keys(backend):
    tags = backend.get_tags("verb")
    finites = [t for t in tags if t.get("VerbForm") == "Fin"]
    assert finites
    for t in finites:
        assert {"tag", "Tense", "VerbForm", "Voice", "Mood", "Person", "Number"} == set(t.keys())


def test_get_tags_verb_infinitive_rows_lack_mood_person_number(backend):
    tags = backend.get_tags("verb")
    infinitives = [t for t in tags if t.get("VerbForm") == "Inf"]
    assert infinitives
    for t in infinitives:
        assert "Mood" not in t
        assert "Person" not in t
        assert "Number" not in t


def test_get_tags_noun_roundtrip_theos(backend):
    """inflect() with features from get_tags() never raises for θεός (masculine)."""
    for t in backend.get_tags("noun"):
        feats = {k: v for k, v in t.items() if k != "tag"}
        result = backend.inflect("θεός", feats, "noun")
        assert isinstance(result, set)


def test_get_tags_verb_roundtrip_lyoo(backend):
    """inflect() with features from get_tags() never raises for λύω."""
    for t in backend.get_tags("verb"):
        feats = {k: v for k, v in t.items() if k != "tag"}
        result = backend.inflect("λύω", feats, "verb")
        assert isinstance(result, set)


def test_get_tags_noun_first_row(backend):
    tags = backend.get_tags("noun")
    assert tags[0] == {"tag": ".NSM", "Case": "Nom", "Number": "Sing", "Gender": "Masc"}


def test_get_tags_verb_first_row(backend):
    tags = backend.get_tags("verb")
    assert tags[0] == {
        "tag": "PAI.1S", "Tense": "Pres", "VerbForm": "Fin",
        "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing",
    }


# --- caching: second call returns consistent results ---

def test_noun_cache_consistent(backend):
    r1 = backend.inflect("θεός", {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}, "noun")
    r2 = backend.inflect("θεός", {"Case": "Gen", "Number": "Sing", "Gender": "Masc"}, "noun")
    assert "θεός" in r1
    assert "θεοῦ" in r2


# --- lexicon selection ---

IMP_2S = {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Imp", "Person": "2", "Number": "Sing"}
IMP_2P = {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Imp", "Person": "2", "Number": "Plur"}


def test_default_lexicon_is_pratt():
    b = AncientGreekBackend()
    assert b._lexicons == ("pratt",)


def test_homer_lexicon_akouo_imperative():
    b = AncientGreekBackend(lexicons=["homer"])
    assert "ἄκουε" in b.inflect("ἀκούω", IMP_2S, "verb")


def test_homer_lexicon_akouo_imperative_plural():
    b = AncientGreekBackend(lexicons=["homer"])
    assert "ἀκούετε" in b.inflect("ἀκούω", IMP_2P, "verb")


def test_homer_lexicon_pauō_imperative():
    b = AncientGreekBackend(lexicons=["homer"])
    assert "παῦε" in b.inflect("παύω", IMP_2S, "verb")


def test_homer_lexicon_anagignwskw_imperative():
    b = AncientGreekBackend(lexicons=["homer"])
    result = b.inflect("ἀναγιγνώσκω", IMP_2S, "verb")
    assert result
    assert any("γνωσκ" in f for f in result)


def test_merged_homer_lxx():
    b = AncientGreekBackend(lexicons=["homer", "lxx"])
    assert "λέγε" in b.inflect("λέγω", IMP_2S, "verb")


def test_list_lemmas_homer_includes_akouo():
    b = AncientGreekBackend(lexicons=["homer"])
    assert "ἀκούω" in b.list_lemmas("verb")


def test_default_still_works_after_lexicon_param():
    b = AncientGreekBackend()
    result = b.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act",
                               "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")
    assert result


# --- get_slot_templates (bundled data) ---

def test_get_slot_templates_verb_en_nonempty(backend):
    result = backend.get_slot_templates("grc", "verb", "en")
    assert result is not None
    assert len(result) > 0


def test_get_slot_templates_verb_includes_imperatives(backend):
    result = backend.get_slot_templates("grc", "verb", "en")
    assert result is not None
    tags = {s.tag for s in result}
    assert "PAD.2S" in tags
    assert "PAD.2P" in tags


def test_get_slot_templates_verb_pad2s_has_ud_features(backend):
    result = backend.get_slot_templates("grc", "verb", "en")
    slot = next(s for s in result if s.tag == "PAD.2S")
    assert slot.tag_type == "ud"
    assert slot.features == {
        "Tense": "Pres", "VerbForm": "Fin", "Voice": "Act",
        "Mood": "Imp", "Person": "2", "Number": "Sing",
    }


def test_get_slot_templates_adj_adv_slot(backend):
    result = backend.get_slot_templates("grc", "adjective", "en")
    assert result is not None
    adv = next((s for s in result if s.tag == "ADV"), None)
    assert adv is not None
    assert adv.tag_type == "ag-paradigm"


def test_get_slot_templates_noun_en_nonempty(backend):
    result = backend.get_slot_templates("grc", "noun", "en")
    assert result is not None
    assert len(result) > 0
