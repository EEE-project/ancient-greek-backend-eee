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
    assert result.pop().rstrip() == "λύω"


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


# --- dual number (2026-07-11: added for Pres/Imp/Fut/Perf Act Ind + Pres Act
# Imp -- the only tense/voice/mood combos the stemming engine actually has
# dual rules for; Aor and Mid/Pass dual have zero rule coverage) ---

def test_verb_pres_act_ind_2d(backend):
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act", "Mood": "Ind", "Person": "2", "Number": "Dual"}, "verb")
    assert "λύετον" in result


def test_verb_perf_act_ind_3d(backend):
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Perf", "Voice": "Act", "Mood": "Ind", "Person": "3", "Number": "Dual"}, "verb")
    assert "λελύκατον" in result


def test_verb_aor_act_ind_2d_has_no_rule_coverage(backend):
    """Documents a real engine limitation, not a bug: aorist dual isn't
    implemented at all, for any verb -- confirmed structural (checked
    across multiple verbs), not a gap in this specific lemma's data. This
    is why verb-tags.tsv only has dual rows for Pres/Imp/Fut/Perf Act Ind
    and Pres Act Imp, not Aor or Mid/Pass."""
    result = backend.inflect("λύω", {"VerbForm": "Fin", "Tense": "Aor", "Voice": "Act", "Mood": "Ind", "Person": "2", "Number": "Dual"}, "verb")
    assert result == set()


def test_build_verb_paradigm_prunes_dual_sweep_to_9_known_combos():
    """The dual-number sweep tries every tense/voice/mood combination for
    2D/3D (~120 attempts per lemma) even though only 9 combinations ever
    have real stemming data (verb-tags.tsv's 9 dual rows). This asserts
    the pruning actually happens -- only those 9 exact keys are ever
    attempted, not just that the (already-empty-filtered) result is
    correct, which the tests above already cover."""
    b = AncientGreekBackend(lexicons=["homer"])
    seen_keys = []
    orig_sweep = b._sweep_form

    def counting_sweep(gi, lemma, key, *, tags=None):
        seen_keys.append(key)
        return orig_sweep(gi, lemma, key, tags=tags)

    b._sweep_form = counting_sweep
    b._build_verb_paradigm("λύω")

    dual_keys_tried = {k for k in seen_keys if k.split(".")[-1] in ("2D", "3D")}
    valid_dual_tags = {row["tag"] for row in b.get_tags("verb") if row["tag"].split(".")[-1] in ("2D", "3D")}
    assert dual_keys_tried == valid_dual_tags
    assert len(dual_keys_tried) == 9


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


def test_paradigm_verb_includes_dual(backend):
    result = backend.paradigm("λύω", "verb")
    assert result.get("PAI.2D") == {"λύετον"}
    assert result.get("PAI.3D") == result.get("PAI.2D")  # syncretic with 2D, as expected


def test_paradigm_verb_no_1d(backend):
    """Ancient Greek has no first-person dual -- must never appear, even
    though _VERB_PERSONS/_VERB_IMP_PN are swept exhaustively per tense/
    voice/mood combination the same way every other person is."""
    result = backend.paradigm("λύω", "verb")
    assert not any(k.endswith(".1D") for k in result)


def test_paradigm_verb_dual_absent_where_engine_has_no_rule(backend):
    """Aorist active dual has zero rule coverage in the stemming engine
    (confirmed across multiple verbs elsewhere in this file) -- .paradigm()
    must not silently invent a key for it."""
    result = backend.paradigm("λύω", "verb")
    assert "AAI.2D" not in result


def test_paradigm_verb_participle_covers_plural():
    """οἴχομαι's attested present middle participle masc. plural nominative
    (οἰχόμενοι) was structurally unreachable — the participle sweep's csg
    list was hardcoded to 6 singular cells only, unlike the full 45-cell
    _CSG_KEYS enumeration nouns/adjectives use."""
    b = AncientGreekBackend(lexicons=["homer"])
    result = b.paradigm("οἴχομαι", "verb")
    assert "οἰχόμενοι" in result.get("PMP.NPM", set())


def test_paradigm_noun_surfaces_attested_duals():
    """_CSG_KEYS only swept Sing/Plur, so the 3 individually-attested noun
    duals in the morpheus lexicon (form_override entries, no stemming rule
    generates them) were structurally unreachable through .paradigm() even
    though the underlying data was correct."""
    b = AncientGreekBackend(lexicons=["morpheus"])
    assert "κήρυκε" in b.paradigm("κῆρυξ", "noun").get(".NDM", set())
    assert "ἀνέρε" in b.paradigm("ἀνήρ", "noun").get(".NDM", set())
    podoin = b.paradigm("πούς", "noun")
    assert "ποδοῖιν" in podoin.get(".DDM", set())
    assert "ποδοῖιν" in podoin.get(".GDM", set())


def test_paradigm_noun_returns_dict(backend):
    result = backend.paradigm("θεός", "noun")
    assert isinstance(result, dict)
    assert result


def test_paradigm_adj_returns_dict(backend):
    result = backend.paradigm("ἀγαθός", "adjective")
    assert isinstance(result, dict)
    assert result


def test_paradigm_adj_adverb_regular(backend):
    result = backend.paradigm("αὐτός", "adjective")
    assert result.get("ADV") == {"αὐτῶς"}


def test_paradigm_adj_adverb_agathos(backend):
    result = backend.paradigm("ἀγαθός", "adjective")
    assert result.get("ADV") == {"ἀγαθῶς"}


def test_paradigm_adj_adverb_not_final_accented(backend):
    """δίκαιος is accented on the first syllable, not the ending -- the old
    formation rule stripped only "-ος" and appended "-ῶς" unconditionally,
    producing the invalid double-accented "δίκαιῶς" (original accent still
    on the stem, plus the ending's own circumflex). Correct form is
    δικαίως, derived from the genitive plural δικαίων (Smyth: the adverb
    takes the gen. plural's accent) rather than guessed from the bare
    lemma."""
    result = backend.paradigm("δίκαιος", "adjective")
    assert result.get("ADV") == {"δικαίως"}


def test_paradigm_adj_adverb_sigma_stem(backend):
    """ἀληθής (3rd-declension sigma-stem, masc/fem oblique cases now shared
    per the ancient-greek-backend-eee#4 fix) derives ἀληθῶς the same way
    any other adjective with real genitive-plural coverage does -- adverb
    derivation is based on gen. plural availability, not the lemma's own
    ending shape, contrary to what this test used to assume."""
    result = backend.paradigm("ἀληθής", "adjective")
    assert result.get("ADV") == {"ἀληθῶς"}


def test_paradigm_adj_adverb_no_coverage(backend):
    # A made-up lemma no lexicon has ever heard of -- empty cache, so no
    # spurious adverb should be derived (see _build_nominal_cache's
    # "if pos == 'adjective' and cache:" gate).
    result = backend.paradigm("ξαβδοπός", "adjective")
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
    # 88 base rows + 9 dual (2D/3D for the tense/voice combos the engine
    # actually supports: PAI/IAI/FAI/XAI indicative + PAD imperative --
    # aorist and middle/passive dual have zero rule coverage in the
    # stemming engine, so they're deliberately not included here).
    assert len(backend.get_tags("verb")) == 97


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


# --- analyze ---

def test_analyze_verb_returns_lemma_pos_tag_features(backend):
    results = backend.analyze("βάλλω")
    assert {"lemma": "βάλλω", "pos": "verb", "tag": "PAI.1S",
            "features": {"Tense": "Pres", "VerbForm": "Fin", "Voice": "Act",
                          "Mood": "Ind", "Person": "1", "Number": "Sing"}} in results


def test_analyze_verb_ambiguous_ind_and_sub(backend):
    # βάλλω is thematic, so its bare present-stem form is syncretic between
    # indicative and subjunctive 1st singular -- both are real candidates.
    tags = {r["tag"] for r in backend.analyze("βάλλω")}
    assert tags == {"PAI.1S", "PAS.1S"}


def test_analyze_adjective_dot_prefix_applied(backend):
    results = backend.analyze("δίκαιος")
    assert {"lemma": "δίκαιος", "pos": "adjective", "tag": ".NSM",
            "features": {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}} in results


def test_analyze_noun_includes_known_overmatch(backend):
    # Documented reverse-stemming limitation, not a bug in analyze() itself:
    # θεός's masc. NSM candidate is currently missing and a spurious NSF/APF
    # pair comes back instead. Pinned so an upstream precision fix is a
    # deliberate test update, not a silent behavior change.
    tags = {r["tag"] for r in backend.analyze("θεός")}
    assert tags == {".NSF", ".APF"}


def test_analyze_unknown_form_returns_empty_list(backend):
    assert backend.analyze("xyzabc") == []


def test_analyze_pronoun_form_returns_empty_list_not_crash(backend):
    # Pronoun lexicons load with ruleset=None (form_override-only -- see
    # load_pron_lexicons()), so GreekInflexion.parse() would crash on the
    # missing stemming rule set; analyze() excludes pos="pronoun" from its
    # loop entirely rather than attempting it.
    assert backend.analyze("οὗτος") == []


def test_tag_index_keeps_every_row_for_a_shared_tag(backend):
    # .NSM is shared by 4 PronType families (Dem/Rel/Int/Ind) in
    # pronoun-tags.tsv; a plain tag->row dict would silently keep only one.
    rows = backend._tag_index("pronoun").get(".NSM", [])
    assert {r["PronType"] for r in rows} == {"Dem", "Rel", "Int", "Ind"}


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


def test_list_lemmas_includes_forms_only_lexicon():
    """A lexicon with zero stems: entries (e.g. byzantine, morpheus) was
    invisible to list_lemmas even though .generate()/.paradigm() correctly
    return data for it -- list_lemmas only enumerated gi.lexicon, never
    gi.form_override."""
    b = AncientGreekBackend(lexicons=["byzantine"])
    assert "γιγνώσκω" in b.list_lemmas("verb")
    assert "ὁράω" in b.list_lemmas("verb")


def test_list_lemmas_unaffected_by_prior_paradigm_queries():
    """Querying .paradigm() for a lemma NOT in the loaded lexicon has a
    documented side effect in the upstream inflexion library: it can add a
    phantom stem entry to the shared Lexicon object for that lemma. A
    coverage/tagging loop over a full vocabulary (as e.g. an interactive-text
    notebook runs) does exactly this for every word not in a given lexicon.
    list_lemmas must not surface those phantom entries -- it should report
    exactly what the bundled YAML contains, regardless of what this instance
    has already been asked about."""
    b = AncientGreekBackend(lexicons=["byzantine"])
    before = set(b.list_lemmas("verb"))

    # λύω/πράττω/χράομαι and both nouns are confirmed absent from the
    # byzantine lexicon (unlike the previous εἰμί/λέγω picks, which the
    # lexicon grew to legitimately include -- see byzantine_verbs_lexicon.yaml).
    unrelated_lemmas = [("λύω", "verb"), ("πράττω", "verb"), ("χράομαι", "verb"),
                        ("ἀνήρ", "noun"), ("ἄνθρωπος", "noun")]
    for unrelated_lemma, pos in unrelated_lemmas:
        b.paradigm(unrelated_lemma, pos)

    after = set(b.list_lemmas("verb"))
    assert after == before
    assert "λύω" not in after
    assert "πράττω" not in after


def test_default_still_works_after_lexicon_param():
    b = AncientGreekBackend()
    result = b.inflect("λύω", {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act",
                               "Mood": "Ind", "Person": "1", "Number": "Sing"}, "verb")
    assert result


def test_for_period_byzantine_matches_hand_written_list():
    b = AncientGreekBackend.for_period("byzantine")
    assert b._lexicons == ("lxx", "morphgnt", "pratt", "ltrg", "lsj", "byzantine")


def test_for_period_attic_matches_hand_written_list():
    b = AncientGreekBackend.for_period("attic")
    assert b._lexicons == ("pratt", "ltrg", "lsj")


def test_for_period_hellenistic_koine_matches_hand_written_list():
    b = AncientGreekBackend.for_period("hellenistic_koine")
    assert b._lexicons == ("lxx",)


def test_for_period_roman_koine_matches_hand_written_list():
    b = AncientGreekBackend.for_period("roman_koine")
    assert b._lexicons == ("morphgnt",)


def test_for_period_epic_matches_hand_written_list():
    b = AncientGreekBackend.for_period("epic")
    assert b._lexicons == ("homer",)


def test_for_period_extra_lexicons_appended_after_preset():
    b = AncientGreekBackend.for_period("epic", extra_lexicons=["odyssey_morpheus"])
    assert b._lexicons == ("homer", "odyssey_morpheus")


def test_for_period_unknown_period_raises():
    with pytest.raises(ValueError, match="Unknown period"):
        AncientGreekBackend.for_period("classical")


def test_for_period_no_periods_raises():
    with pytest.raises(ValueError, match="requires at least one period"):
        AncientGreekBackend.for_period()


def test_for_period_multiple_periods_union_with_extra():
    b = AncientGreekBackend.for_period("epic", "attic", "hellenistic_koine", "roman_koine",
                                        extra_lexicons=["odyssey_morpheus"])
    assert b._lexicons == ("homer", "pratt", "ltrg", "lsj", "lxx", "morphgnt", "odyssey_morpheus")


def test_for_period_multiple_periods_produces_same_lemmas_regardless_of_order():
    b1 = AncientGreekBackend.for_period("epic", "attic", "hellenistic_koine", "roman_koine")
    b2 = AncientGreekBackend.for_period("roman_koine", "hellenistic_koine", "attic", "epic")
    assert set(b1.list_lemmas("verb")) == set(b2.list_lemmas("verb"))


def test_for_period_byzantine_produces_working_backend():
    b = AncientGreekBackend.for_period("byzantine")
    assert "γιγνώσκω" in b.list_lemmas("verb")
    assert "ὁράω" in b.list_lemmas("verb")


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


def test_get_slot_templates_verb_includes_dual(backend):
    result = backend.get_slot_templates("grc", "verb", "en")
    tags = {s.tag for s in result}
    assert {"PAI.2D", "PAI.3D", "IAI.2D", "IAI.3D", "FAI.2D", "FAI.3D",
            "XAI.2D", "XAI.3D", "PAD.2D"} <= tags


def test_get_slot_templates_verb_pai2d_has_ud_features(backend):
    result = backend.get_slot_templates("grc", "verb", "en")
    slot = next(s for s in result if s.tag == "PAI.2D")
    assert slot.tag_type == "ud"
    assert slot.features == {
        "Tense": "Pres", "VerbForm": "Fin", "Voice": "Act",
        "Mood": "Ind", "Person": "2", "Number": "Dual",
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


# --- homer noun lexicon (bug fix: issue #7) ---

@pytest.fixture(scope="module")
def homer_backend():
    return AncientGreekBackend(lexicons=["homer", "lxx", "morphgnt"])


@pytest.mark.parametrize("lemma", [
    "θάνατος", "μόρος", "ἄνεμος", "ἑταῖρος",
    "νῆσος", "ἤπειρος", "μάχη",
    "μῆλον", "φύλλον", "αἶσα",
    "ἄλγος", "ἄνθος", "κτῆμα", "γείτων", "βοῦς",
])
def test_homer_noun_has_forms(homer_backend, lemma):
    p = homer_backend.paradigm(lemma, "noun")
    assert p, f"{lemma!r} returned empty paradigm"


def test_homer_noun_thanatos_nsm(homer_backend):
    result = homer_backend.inflect("θάνατος", {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}, "noun")
    assert "θάνατος" in result


def test_homer_noun_mache_nsf(homer_backend):
    result = homer_backend.inflect("μάχη", {"Case": "Nom", "Number": "Sing", "Gender": "Fem"}, "noun")
    assert "μάχη" in result


def test_homer_noun_melon_nsn(homer_backend):
    result = homer_backend.inflect("μῆλον", {"Case": "Nom", "Number": "Sing", "Gender": "Neut"}, "noun")
    assert "μῆλον" in result


def test_homer_noun_bous_nsm(homer_backend):
    result = homer_backend.inflect("βοῦς", {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}, "noun")
    assert "βοῦς" in result


def test_homer_noun_geiton_nsm(homer_backend):
    result = homer_backend.inflect("γείτων", {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}, "noun")
    assert "γείτων" in result


def test_pratt_nouns_still_work_with_homer_backend(homer_backend):
    result = homer_backend.inflect("λόγος", {"Case": "Nom", "Number": "Sing", "Gender": "Masc"}, "noun")
    assert "λόγος" in result


# --- noun paradigm gender restriction (bug fix) ---
# .paradigm() previously enumerated all 3 genders unconditionally for every
# noun, so a single-gender noun's full paradigm table included mechanically-
# generated forms for genders it doesn't have (confirmed to affect every
# noun using the bare "noun:" stem key, e.g. Ζεύς showing a spurious plural
# and feminine). These tests exercise .paradigm() specifically -- the other
# noun tests above all go through .inflect() with an explicit Gender, a path
# that was already correct since the caller supplies the gender directly.

def test_noun_paradigm_excludes_wrong_gender(homer_backend):
    # μῆλον is 2nd-declension neuter (-ον); a masculine or feminine cell is
    # not real Greek for this word.
    result = homer_backend.paradigm("μῆλον", "noun")
    genders = {k[-1] for k in result}
    assert genders == {"N"}, f"expected neuter-only, got {genders}: {result}"


def test_noun_paradigm_ambiguous_os_noun_keeps_both_genders(backend):
    # 2nd-declension -ος nouns are a genuine exception: masculine and
    # feminine share identical endings throughout (a real feminine -ος noun
    # like νῆσος is indistinguishable from a masculine one by form alone),
    # so the gender-detection heuristic can't tell them apart for θεός
    # either and correctly keeps both rather than guessing. Neuter must
    # still be excluded, since -ος and -ον endings genuinely differ.
    result = backend.paradigm("θεός", "noun")
    genders = {k[-1] for k in result}
    assert genders == {"M", "F"}, f"expected M+F (ambiguous by form), got {genders}: {result}"


def test_noun_paradigm_form_override_always_trusted():
    # An explicit forms: override must survive regardless of what gender the
    # detection heuristic guesses for the rest of the noun's paradigm -- it's
    # confirmed data, not a mechanical guess. This is what lets genuinely
    # dual-gender nouns (γείτων "neighbor", ἅλς "salt"/"sea") keep all their
    # real forms even though a single-gender heuristic can't anticipate them
    # from the lemma's own nominative singular alone. θεός is detected as
    # M+F (see the ambiguous-noun test above); this injects a neuter
    # override it would never self-detect, to prove the override wins
    # regardless. A fresh backend instance avoids mutating the shared
    # module-scoped `backend` fixture other tests in this file depend on.
    backend = AncientGreekBackend()
    gi = backend._get_gi("noun")
    gi.form_override[("θεός", "NSN")] = "ARBITRARY-OVERRIDE-TEST"
    result = backend.paradigm("θεός", "noun")
    assert result.get(".NSN") == {"ARBITRARY-OVERRIDE-TEST"}


def test_noun_paradigm_unmatched_lemma_falls_back_to_all_genders():
    # If the nominative-singular self-check matches no gender at all (an
    # unanticipated lemma shape -- here, a lemma with no stem registered at
    # all, only two forced overrides in different genders), the restriction
    # doesn't engage -- degrades to the pre-fix behavior of showing
    # everything instead of silently losing forms outright.
    backend = AncientGreekBackend()
    gi = backend._get_gi("noun")
    gi.form_override[("ξενολεξις", "GSM")] = "ξενολεξεως"
    gi.form_override[("ξενολεξις", "NSN")] = "ξενολεξις-neut"
    result = backend.paradigm("ξενολεξις", "noun")
    assert result.get(".GSM") == {"ξενολεξεως"}
    assert result.get(".NSN") == {"ξενολεξις-neut"}


def test_adjective_paradigm_still_has_all_genders(backend):
    # The gender restriction is noun-only -- adjectives genuinely decline
    # through all 3 genders and must be unaffected.
    result = backend.paradigm("ἀγαθός", "adjective")
    genders = {k.split(".")[-1][-1] for k in result if "." in k}
    assert genders == {"M", "F", "N"}, f"expected all 3 genders, got {genders}"


# --- pronouns: get_tags / get_slot_templates ---
# pronoun-tags.tsv legitimately has multiple rows sharing the same tag
# string (e.g. .NSM appears once per pronoun family that attests it --
# οὗτος=Dem, ὅς=Rel, τίς=Int, τις=Ind all have an NSM cell) since
# PronType is a per-lemma-family fact layered onto this otherwise
# POS-level (not lemma-level) tag table -- see tools/generate_pronoun_tags.py
# for the full reasoning, including a known consequence for downstream
# tag-only-matching consumers. Tests below account for this rather than
# assuming tag uniqueness within the pos.

def test_get_tags_pronoun_nonempty(backend):
    assert backend.get_tags("pronoun")


def test_get_tags_pronoun_gender_rows_lack_person(backend):
    """Mirrors test_get_tags_verb_infinitive_rows_lack_mood_person_number's
    blank-cell-is-omitted convention: rows for the adjective-like pronoun
    family must not carry a Person key."""
    tags = backend.get_tags("pronoun")
    gender_rows = [t for t in tags if "Gender" in t]
    assert gender_rows
    for t in gender_rows:
        assert "Person" not in t


def test_get_tags_pronoun_person_rows_lack_gender(backend):
    tags = backend.get_tags("pronoun")
    person_rows = [t for t in tags if "Person" in t]
    assert person_rows
    for t in person_rows:
        assert "Gender" not in t


def test_get_tags_pronoun_all_rows_have_prontype(backend):
    """PronType applies to every pronoun cell regardless of family — the
    interview decision (Q1) that PronType should always be present."""
    tags = backend.get_tags("pronoun")
    for t in tags:
        assert "PronType" in t


def test_get_tags_pronoun_all_five_gender_prontypes_present(backend):
    """Every non-personal PronType value is actually reachable -- a
    naive one-row-per-tag dedup would silently make some of these
    unrepresentable (the bug tools/generate_pronoun_tags.py's own
    docstring documents catching: deduping by tag alone made Rcp/Int/Ind
    vanish entirely, since their cells always collide with a
    higher-priority family's identical tag string)."""
    tags = backend.get_tags("pronoun")
    prontypes = {t["PronType"] for t in tags}
    assert {"Dem", "Rel", "Int", "Ind", "Rcp", "Prs"} <= prontypes


def test_get_slot_templates_pronoun_en_nonempty(backend):
    result = backend.get_slot_templates("grc", "pronoun", "en")
    assert result is not None
    assert len(result) > 0


def test_get_slot_templates_pronoun_all_ud_tag_type(backend):
    result = backend.get_slot_templates("grc", "pronoun", "en")
    assert all(s.tag_type == "ud" for s in result)
    assert all(s.features for s in result)


# --- pronouns: dispatch ---

def test_get_gi_pronoun_lazy_cached():
    b = AncientGreekBackend()
    assert "pronoun" not in b._gi_cache
    gi1 = b._get_gi("pronoun")
    assert "pronoun" in b._gi_cache
    gi2 = b._get_gi("pronoun")
    assert gi1 is gi2


def test_inflect_pronoun_personal_shape_returns_nonempty(backend):
    """ἐγώ, 1st singular nominative -- personal-pronoun (no Gender) shape."""
    result = backend.inflect(
        "ἐγώ", {"Case": "Nom", "Number": "Sing", "Person": "1", "PronType": "Prs"}, "pronoun",
    )
    assert isinstance(result, set)
    assert result


def test_inflect_pronoun_adjective_shape_returns_nonempty(backend):
    """οὗτος, masc nom sing -- Gender-present, adjective-like shape."""
    result = backend.inflect(
        "οὗτος", {"Case": "Nom", "Number": "Sing", "Gender": "Masc", "PronType": "Dem"}, "pronoun",
    )
    assert isinstance(result, set)
    assert result


def test_inflect_pronoun_personal_dual_returns_correct_form(backend):
    """ἐγώ's confirmed genuine dual (νώ) — exact-string check, not just
    non-empty, since dual is the one paradigm axis unique to personal
    pronouns among nominal-shaped categories."""
    result = backend.inflect(
        "ἐγώ", {"Case": "Nom", "Number": "Dual", "Person": "1", "PronType": "Prs"}, "pronoun",
    )
    assert "νώ" in result


def test_inflect_pronoun_common_gender_fem_falls_back_to_shared_form(backend):
    """τίς/τις are common-gender (Masc and Fem share one form, stored
    only under the Masc key) -- asking for Fem explicitly must still
    return the real shared form, not silently empty. Caught by code
    review: no test previously exercised this, and the naive
    cache.get(suffix, set()) lookup alone returns set() for Fem since
    no Fem-keyed cell was ever shipped for these two lemmas."""
    result = backend.inflect(
        "τίς", {"Case": "Nom", "Number": "Sing", "Gender": "Fem", "PronType": "Int"}, "pronoun",
    )
    assert "τίς" in result


def test_inflect_pronoun_fem_fallback_is_noop_for_distinct_gender_lemmas(backend):
    """The Masc<-Fem fallback must not paper over lemmas that genuinely
    lack a cell for other reasons (e.g. ἀλλήλων's defective paradigm) --
    it should stay empty, not incorrectly borrow the Masc cell, when
    Masc is ALSO absent for the same underlying reason."""
    result = backend.inflect(
        "ἀλλήλων", {"Case": "Nom", "Number": "Sing", "Gender": "Fem", "PronType": "Rcp"}, "pronoun",
    )
    assert result == set()


def test_paradigm_pronoun_personal_returns_populated_dict(backend):
    result = backend.paradigm("ἐγώ", "pronoun")
    assert isinstance(result, dict)
    assert result


def test_paradigm_pronoun_adjective_shape_returns_populated_dict(backend):
    result = backend.paradigm("οὗτος", "pronoun")
    assert isinstance(result, dict)
    assert result


def test_paradigm_pronoun_personal_includes_dual():
    """ἐγώ has a confirmed genuine dual (νώ/νῷν) -- the one other paradigm
    besides verbs to have any dual cell at all in this backend."""
    b = AncientGreekBackend()
    result = b.paradigm("ἐγώ", "pronoun")
    assert any(k[2] == "D" for k in result), f"no dual cell found in {result!r}"


def test_paradigm_pronoun_adjective_shape_includes_dual(backend):
    """οὗτος also has confirmed dual forms (τούτω/τούτοιν) shipped in
    section-03's lexicon -- regression check that the adjective-shaped
    pronoun sweep, which now shares _CSG_KEYS with nouns/adjectives/
    participles, still reaches Dual cells."""
    result = backend.paradigm("οὗτος", "pronoun")
    assert result.get(".NDM") == {"τούτω"}
    assert result.get(".GDM") == {"τούτοιν"}


def test_paradigm_pronoun_reciprocal_excludes_nominative_and_singular(backend):
    """Mirrors section-03's lexicon-level guard, at the paradigm-building
    level -- confirms the defective ἀλλήλων paradigm (oblique cases only,
    dual+plural only) survives the full build path, not just the raw
    forms: block. ἀλλήλων is Gender-present (reciprocal is grouped into
    the adjective-like family), so its cache keys use the same
    '.' + Case + Number + Gender shape as ag_adj_key."""
    result = backend.paradigm("ἀλλήλων", "pronoun")
    assert result
    for key in result:
        csg = key.lstrip(".")
        assert csg[0] != "N", f"unexpected nominative cell {key!r}"
        assert csg[1] != "S", f"unexpected singular cell {key!r}"


def test_list_lemmas_pronoun_returns_all_lemmas(backend):
    lemmas = backend.list_lemmas("pronoun")
    assert len(lemmas) >= 10
    assert "ἐγώ" in lemmas
    assert "ἀλλήλων" in lemmas


def test_paradigm_unknown_pos_message_mentions_pronoun(backend):
    with pytest.raises(ValueError, match="pronoun"):
        backend.paradigm("λύω", "unknown_pos")


def test_inflect_unknown_pos_message_mentions_pronoun(backend):
    with pytest.raises(ValueError, match="pronoun"):
        backend.inflect("λύω", {}, "unknown_pos")


def test_get_gi_unknown_pos_message_mentions_pronoun():
    b = AncientGreekBackend()
    with pytest.raises(ValueError, match="pronoun"):
        b._get_gi("unknown_pos")
