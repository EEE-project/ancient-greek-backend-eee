import csv
import importlib.resources as _pkg_data

from ancient_greek_backend_eee._ag_features import ag_verb_key, ag_noun_key, ag_adj_key, ag_pron_key, CSG_TAG_PREFIX

_POS_TSV = {
    "noun": "noun-tags.tsv", "adjective": "adj-tags.tsv", "verb": "verb-tags.tsv",
    "pronoun": "pronoun-tags.tsv",
}

# pronoun-tags.tsv (unlike the other three) legitimately has multiple rows
# sharing the same tag string: PronType is a per-lemma-family fact (e.g.
# .NSM is used by οὗτος=Dem, ὅς=Rel, τίς=Int, τις=Ind, all with different
# PronType), but get_slot_templates()/get_tags() are POS-level, not
# lemma-level, APIs. Known consequence for callers: a caller that picks
# the FIRST slot matching a tag (rather than filtering by the lemma's
# own real PronType first) will always resolve to whichever PronType
# happens to sort first for a shared tag. See tools/generate_pronoun_tags.py
# for the full reasoning and regeneration instructions.

# All 45 case/number/gender combinations for noun, adjective, and verb-
# participle paradigms. Includes dual ("D") to surface the handful of
# individually-attested noun duals in the morpheus lexicon (e.g. κῆρυξ's
# NDM: κήρυκε) -- regular nouns/adjectives/participles have no dual
# stemming rules, so gi.generate() safely returns empty for the rest of
# the dual cells rather than raising (verified before adding this).
_CSG_KEYS = [
    c + n + g
    for c in "NGDAV"
    for n in "SPD"
    for g in "MFN"
]

# Personal pronouns (ἐγώ, σύ): Case x Number x Person, no Gender axis.
# No Vocative -- Ancient Greek personal pronouns have no distinct
# vocative case (confirmed against Smyth's Grammar during section-03).
_PRON_PERSONAL_CASES = "NGDA"
_PRON_PERSONAL_NUMBERS = "SPD"
_PRON_PERSONAL_PERSONS = "12"

# The two pronoun lemmas with no Gender axis (Case+Number+Person shape).
# Two other places have to agree on which lemmas are personal: section-03's
# lexicon file, and tools/generate_pronoun_tags.py's own _PERSONAL_LEMMAS
# (that script deliberately avoids importing this package -- it generates
# the data file this package ships -- so there's no clean shared-import fix;
# flagged here, not eliminated, so a future edit to either set gets a
# pointer to the other).
_PERSONAL_PRONOUN_LEMMAS = {"ἐγώ", "σύ"}

# Indicative tense/voice/mood combinations for verb paradigm
_VERB_TENSES  = list("PIAFXY")   # Pres, Imp, Aor, Fut, Perf, Pluperf
_VERB_VOICES  = list("AMP")
# No "1D": Ancient Greek has no first-person dual. 2D/3D are candidates for
# every tense/voice/mood combination here (same as every other person), but
# the stemming engine only actually has dual rules for a subset (Pres/Imp/
# Fut/Perf Act Ind, Pres Act Imp) -- the other ~111 of ~120 dual attempts per
# lemma are guaranteed-empty stemming-engine calls discovered by brute force
# every time; _build_verb_paradigm prunes these against get_tags("verb")'s
# own tag list (verb-tags.tsv's 9 real dual rows) before attempting them.
_VERB_PERSONS = ["1S", "2S", "3S", "2D", "3D", "1P", "2P", "3P"]
_VERB_IMP_PN  = ["2S", "3S", "2D", "3D", "2P", "3P"]
_VERB_DUAL_PERSONS = {"2D", "3D"}
_VERB_TAGS = {"final-nu-aai.3s"}

# Named historical-period presets for consumers that want a period by name
# instead of hand-copying its lexicon list (the lexicon names are an
# implementation detail behind the period, not the identifier callers use --
# matches eee-project's own diachronic-dropdown period labels,
# _GRC_LEX_PERIOD in notebook_utils.py, though that dict keys by lexicon
# name for a different purpose -- UI tab display -- and isn't imported here:
# eee-project is only a dev dependency of this package (used for its own
# test suite), not a runtime one, so core construction can't rely on it
# being installed). These lists were previously hand-copied identically
# across 8 call sites (7 Odyssey lesson notebooks + eee-project's example
# notebook) with no shared source of truth -- a typo or partial update in
# any one copy would silently drift from the rest.
# "byzantine" merges onto the Attic/Koine bases (see greek-inflexion-eee's
# README: byzantine is a sparse exceptions layer, not a standalone stemming
# engine) so it inherits their full lemma coverage.
_PERIOD_PRESETS: dict[str, tuple[str, ...]] = {
    "epic": ("homer",),
    "attic": ("pratt", "ltrg", "lsj"),
    "hellenistic_koine": ("lxx",),
    "roman_koine": ("morphgnt",),
}
# Derived, not hand-copied, so it can't silently drift from the 3 presets
# it merges onto -- the same drift risk this whole dict exists to prevent.
_PERIOD_PRESETS["byzantine"] = (
    _PERIOD_PRESETS["hellenistic_koine"] + _PERIOD_PRESETS["roman_koine"]
    + _PERIOD_PRESETS["attic"] + ("byzantine",)
)


class AncientGreekBackend:
    """MorphologyBackend implementation for Ancient Greek (ISO 639-2: grc).

    Wraps greek_inflexion_eee (Pratt lexicon) to generate inflected surface
    forms from Universal Dependencies FEATS dicts. Supports four parts of
    speech: "verb", "noun", "adjective", "pronoun".

    Lazy loading: greek_inflexion_eee is not imported at module load time.
    Paradigm results for nouns, adjectives, and pronouns are cached per
    lemma after the first call.

    Exception propagation: library exceptions for unknown lemmas propagate
    unwrapped from generate().

    Known tech debt: verb/noun/adjective/pronoun are still hardcoded as
    separate branches in inflect/paradigm (their per-pos logic genuinely
    differs) rather than routed through a dict of pos-name -> handler.
    _get_gi/list_lemmas/get_slot_templates/get_tags are pos-generic
    (dispatch via _loaders()/_POS_TSV), so a new pos only needs new
    branches in inflect/paradigm, not five separate edits.
    """

    language = "grc"

    def __init__(
        self, lexicons: "tuple[str, ...] | list[str]" = ("pratt",)
    ) -> None:
        self._lexicons = tuple(lexicons)
        self._gi_cache: dict[str, object] = {}
        self._paradigm_cache: dict[tuple[str, str], dict[str, set[str]]] = {}
        self._slot_cache: dict[tuple[str, str], list] = {}
        self._tag_cache: dict[str, list] = {}
        self._tag_index_cache: dict[str, dict[str, list]] = {}
        self._lemma_cache: dict[str, list[str]] = {}

    @classmethod
    def for_period(
        cls, *periods: str, extra_lexicons: "tuple[str, ...] | list[str]" = ()
    ) -> "AncientGreekBackend":
        """Construct a backend from one or more named historical periods.

        Lexicon merging is a set union (confirmed via greek_inflexion_eee's
        load_lexicons: "later entries add new stems without removing
        existing ones"), so the order periods are listed in doesn't affect
        the result -- multiple periods can be combined freely for a
        broader-coverage backend (e.g. a "recognize anything" union across
        several periods) without needing to reproduce a specific hand-tuned
        lexicon order.

        Args:
            *periods: one or more of _PERIOD_PRESETS' keys ("epic", "attic",
                "hellenistic_koine", "roman_koine", "byzantine")
            extra_lexicons: additional lexicon names to layer on top of the
                preset(s) (e.g. a course-specific lexicon added to "epic")

        Raises:
            ValueError: if no periods given, or a period is not a known preset name
        """
        if not periods:
            raise ValueError("for_period() requires at least one period name.")
        lexicons: list[str] = []
        for period in periods:
            if period not in _PERIOD_PRESETS:
                raise ValueError(f"Unknown period: {period!r}. Expected one of {sorted(_PERIOD_PRESETS)}.")
            lexicons.extend(_PERIOD_PRESETS[period])
        return cls(lexicons=lexicons + list(extra_lexicons))

    @staticmethod
    def _loaders():
        from greek_inflexion_eee import load_lexicons, load_noun_lexicons, load_adj_lexicons, load_pron_lexicons
        return {
            "verb": load_lexicons, "noun": load_noun_lexicons,
            "adjective": load_adj_lexicons, "pronoun": load_pron_lexicons,
        }

    def _get_gi(self, pos: str):
        loaders = self._loaders()
        if pos not in loaders:
            raise ValueError(f"Unknown pos: {pos!r}. Expected 'verb', 'noun', 'adjective', or 'pronoun'.")
        if pos not in self._gi_cache:
            self._gi_cache[pos] = loaders[pos](list(self._lexicons))
        return self._gi_cache[pos]

    def inflect(self, lemma: str, features: dict[str, str], pos: str, **_kw) -> set[str]:
        """Map UD FEATS + pos to a set of inflected surface forms.

        Args:
            lemma: polytonic Greek lemma (must match Pratt lexicon key exactly)
            features: UD FEATS dict (e.g., {"Tense": "Pres", "Voice": "Act", ...})
            pos: one of "verb", "noun", "adjective", "pronoun"

        Returns:
            set[str] of surface forms; empty set if the paradigm path has no forms.

        Raises:
            ValueError: if pos is not "verb", "noun", "adjective", or "pronoun"
            KeyError: if a required feature is absent (propagated from _ag_features)
        """
        if pos == "verb":
            return self._inflect_verb(lemma, features)
        if pos in ("noun", "adjective"):
            return self._inflect_nominal(lemma, features, pos)
        if pos == "pronoun":
            return self._inflect_pronoun(lemma, features)
        raise ValueError(f"Unknown pos: {pos!r}. Expected 'verb', 'noun', 'adjective', or 'pronoun'.")

    def _inflect_verb(self, lemma: str, features: dict[str, str]) -> set[str]:
        key = ag_verb_key(features)
        gi = self._get_gi("verb")
        if key is None:
            # Voice=Mid,Pass: union Mid and Pass
            key_mid  = ag_verb_key({**features, "Voice": "Mid"})
            key_pass = ag_verb_key({**features, "Voice": "Pass"})
            return (
                set(gi.generate(lemma, key_mid, tags=_VERB_TAGS).keys()) |
                set(gi.generate(lemma, key_pass, tags=_VERB_TAGS).keys())
            )
        return set(gi.generate(lemma, key, tags=_VERB_TAGS).keys())

    def _inflect_nominal(self, lemma: str, features: dict[str, str], pos: str) -> set[str]:
        cache_key = (lemma, pos)
        if cache_key not in self._paradigm_cache:
            self._paradigm_cache[cache_key] = self._build_nominal_cache(lemma, pos)
        cache = self._paradigm_cache[cache_key]
        suffix = (ag_noun_key if pos == "noun" else ag_adj_key)(features)
        if suffix is None:
            # No Gender — union across all genders for this case/number
            result: set[str] = set()
            for g in "MFN":
                s = (ag_noun_key if pos == "noun" else ag_adj_key)(
                    {**features, "Gender": ("Masc" if g == "M" else "Fem" if g == "F" else "Neut")}
                )
                if s and s in cache:
                    result |= cache[s]
            return result
        return cache.get(suffix, set())

    def _build_nominal_cache(self, lemma: str, pos: str) -> dict[str, set[str]]:
        gi = self._get_gi(pos)
        cache: dict[str, set[str]] = {}
        ns_forms = self._noun_genders(lemma, gi) if pos == "noun" else {}
        genders = {key[-1] for key in ns_forms}
        for csgsuffix in _CSG_KEYS:
            if (
                pos == "noun" and genders
                and csgsuffix[-1] not in genders
                and (lemma, csgsuffix) not in gi.form_override
            ):
                # Unlike adjectives, a noun has exactly one gender (a few
                # genuinely dual-gender/homograph nouns aside -- see below),
                # so skip mechanically over-generating forms for genders the
                # noun doesn't have (e.g. Ζεύς getting a spurious plural/
                # feminine from its 2nd-declension stem's endings applying
                # unconditionally to M/F/N alike). An explicit form_override
                # is trusted regardless of the gender guess: it's confirmed
                # data, not a mechanical guess, and some nouns are genuinely
                # dual-gender (γείτων "neighbor", ἅλς "salt"/"sea") in ways a
                # single-gender heuristic can't anticipate from the lemma's
                # own nominative singular alone.
                continue
            # _noun_genders() already generated the "NS*" cells while
            # detecting gender -- reuse that instead of asking gi.generate()
            # (real stemming + accentuation work, not a cheap lookup) for
            # the exact same (lemma, key) pair a second time.
            forms = ns_forms.get(csgsuffix) or set(gi.generate(lemma, csgsuffix).keys())
            if forms:
                # CSG_TAG_PREFIX to match ag_noun_key / ag_adj_key output
                cache[CSG_TAG_PREFIX + csgsuffix] = forms
        # cache must already have at least one real declension cell --
        # otherwise _derive_adverb's naive-ending fallback path (no gen.
        # plural to check against) can mechanically derive a spurious
        # adverb for an adjective the engine doesn't actually recognize
        # at all (e.g. καλός with none of these lexicons loaded).
        if pos == "adjective" and cache:
            adv = self._derive_adverb(lemma, cache.get(".GPM"))
            if adv:
                cache["ADV"] = adv
        return cache

    def _inflect_pronoun(self, lemma: str, features: dict[str, str]) -> set[str]:
        cache = self._get_pronoun_cache(lemma)
        suffix = ag_pron_key(features)
        result = cache.get(suffix, set())
        # Common-gender pronouns (τίς/τις): Masc and Fem share one form,
        # stored only under the Masc key in the lexicon (mirrors the
        # two-termination adjective Masc<-Fem fallback in
        # _inflect_nominal). A no-op for lemmas with a real, distinct
        # Fem cell (ὅς, οὗτος, ἀλλήλων, ...): cache.get(suffix, ...)
        # above already succeeds for those, so this branch never fires.
        # suffix.endswith("F") is safe against the personal-pronoun
        # family, whose keys always end in a Person digit ('1'/'2'),
        # never 'F'.
        if not result and suffix and suffix.endswith("F"):
            result = cache.get(suffix[:-1] + "M", set())
        return result

    def _get_pronoun_cache(self, lemma: str) -> dict[str, set[str]]:
        # Deliberately NOT routed through _inflect_nominal/_build_nominal_cache:
        # _inflect_nominal's suffix = (ag_noun_key if pos == "noun" else
        # ag_adj_key)(...) is a binary ternary that would silently call
        # ag_adj_key instead of ag_pron_key for pos == "pronoun", producing
        # the wrong cache-key shape. (_CSG_KEYS coverage is not the issue --
        # it now includes Dual, same as the sweep below.)
        cache_key = (lemma, "pronoun")
        if cache_key not in self._paradigm_cache:
            if lemma in _PERSONAL_PRONOUN_LEMMAS:
                self._paradigm_cache[cache_key] = self._build_pronoun_cache_personal(lemma)
            else:
                self._paradigm_cache[cache_key] = self._build_pronoun_cache_adjective_shaped(lemma)
        return self._paradigm_cache[cache_key]

    @staticmethod
    def _sweep_form(gi, lemma: str, key: str, *, tags: dict[str, str] | None = None) -> set[str]:
        """Generate one paradigm cell's forms. Empty set when nothing generates.

        Shared by every paradigm-cache sweep loop (pronoun, verb) -- each
        loop still does its own "if forms: store under my own key shape"
        afterward, since that part genuinely differs (dot-prefixed vs. bare
        keys, different target dicts).
        """
        if tags is not None:
            return set(gi.generate(lemma, key, tags=tags).keys())
        return set(gi.generate(lemma, key).keys())

    def _build_pronoun_cache_adjective_shaped(self, lemma: str) -> dict[str, set[str]]:
        gi = self._get_gi("pronoun")
        cache: dict[str, set[str]] = {}
        for csgsuffix in _CSG_KEYS:
            forms = self._sweep_form(gi, lemma, csgsuffix)
            if forms:
                cache[CSG_TAG_PREFIX + csgsuffix] = forms
        return cache

    def _build_pronoun_cache_personal(self, lemma: str) -> dict[str, set[str]]:
        gi = self._get_gi("pronoun")
        cache: dict[str, set[str]] = {}
        for c in _PRON_PERSONAL_CASES:
            for n in _PRON_PERSONAL_NUMBERS:
                for p in _PRON_PERSONAL_PERSONS:
                    key = f"{c}{n}{p}"
                    forms = self._sweep_form(gi, lemma, key)
                    if forms:
                        cache[CSG_TAG_PREFIX + key] = forms
        return cache

    @staticmethod
    def _noun_genders(lemma: str, gi) -> dict[str, set[str]]:
        """Detect which gender(s) a noun's own lemma form supports.

        A gender is "detected" when the mechanically-generated nominative
        singular for that gender matches the lemma itself (accent-
        insensitive, since generation and the lemma spelling can differ in
        exactly where an accent lands). Most nouns resolve to a single
        gender this way. 2nd-declension -ος nouns are a genuine exception:
        masculine and feminine share identical endings throughout, so a
        feminine -ος noun (νῆσος, ὁδός, ...) is indistinguishable from a
        masculine one by form alone -- both genders come back "detected",
        and both are kept, which is honest rather than silently guessing.
        Returns an empty dict (caller falls back to all three genders) when
        nothing matches, so an unanticipated lemma shape degrades to the
        old behavior instead of losing forms outright.

        Returns the generated "NS*" forms keyed by CSG suffix (not just the
        bare gender letters), so the caller can reuse them directly instead
        of re-generating the same (lemma, key) pair.
        """
        from greek_inflexion_eee.accent import strip_accents

        target = strip_accents(lemma)
        detected: dict[str, set[str]] = {}
        for g in "MFN":
            key = f"NS{g}"
            forms = set(gi.generate(lemma, key).keys())
            if any(strip_accents(f) == target for f in forms):
                detected[key] = forms
        return detected

    @staticmethod
    def _derive_adverb(lemma: str, gpm_forms: set[str] | None) -> set[str]:
        """Derive adverb from adjective lemma. Handles regular -ος/-ός → -ῶς.

        Prefers the genitive plural masculine cell already computed by the
        caller (*gpm_forms*, the paradigm cache's ``.GPM`` entry -- Smyth:
        the adverb takes the accent of the gen. plural) over re-deriving
        accent placement by hand -- reuses the stemming engine's own correct
        accentuation instead of guessing. Handles adjectives whose own lemma
        accent isn't on the final syllable correctly this way (δίκαιος ->
        δικαίως via gen. pl. δικαίων, not the old δίκαιος -> δίκαιῶς
        double-accent bug: stripping just "-ος" and appending "-ῶς" left the
        lemma's own antepenult accent in place). Falls back to the naive
        lemma-ending swap only when the lemma is itself final-accented
        (where the two approaches always coincide) and no gen. plural data
        exists; for a non-final-accented lemma with no gen. plural data,
        returns empty rather than risk the same double-accent bug.
        """
        import unicodedata
        from greek_inflexion_eee.accent import strip_accents

        if gpm_forms:
            return {f[:-1] + "ς" for f in gpm_forms if f.endswith("ν")}

        nfc = unicodedata.normalize("NFC", lemma)
        if nfc.endswith("ός") or nfc.endswith("ος"):
            stem = nfc[:-2]
            if strip_accents(stem) == stem:  # no accent left: lemma was final-accented
                return {stem + "ῶς"}
        return set()

    def get_slot_templates(
        self, lang: str, pos: str, terms_lang: str = "en"
    ) -> "list | None":
        """Return slot templates for pos, derived from the bundled TSV tag table.

        terms_lang is accepted for API compatibility but ignored — labels are
        the tag strings themselves. Results are cached per pos.
        """
        from eee_project._slot_template import SlotTemplate

        if pos in self._slot_cache:
            return self._slot_cache[pos]

        tags = self.get_tags(pos)
        if not tags:
            return None
        result = [
            SlotTemplate(label=r["tag"], tag_type="ud", tag=r["tag"],
                         features=self._row_features(r))
            for r in tags
        ]
        if pos == "adjective":
            result.append(SlotTemplate(label="ADV", tag_type="ag-paradigm", tag="ADV", features=None))
        self._slot_cache[pos] = result
        return result

    def get_tags(self, pos: str) -> list[dict[str, str]]:
        """Return tag→features rows for pos as a list of dicts.

        Each dict has a 'tag' key plus UD feature keys (Case, Number, Gender,
        Tense, VerbForm, Voice, Mood, Person, Number).  Empty cells are omitted.
        Returns [] for unknown pos. Results are cached per pos.
        """
        if pos in self._tag_cache:
            return self._tag_cache[pos]
        filename = _POS_TSV.get(pos)
        if filename is None:
            return []
        data_pkg = _pkg_data.files("ancient_greek_backend_eee.data")
        text = (data_pkg / filename).read_text(encoding="utf-8")
        reader = csv.DictReader(text.splitlines(), delimiter="\t")
        result = [{k: v for k, v in row.items() if v} for row in reader]
        self._tag_cache[pos] = result
        return result

    @staticmethod
    def _row_features(row: dict[str, str]) -> dict[str, str]:
        """A get_tags() row minus its 'tag' key -- shared by get_slot_templates() and analyze()."""
        return {k: v for k, v in row.items() if k != "tag"}

    def _tag_index(self, pos: str) -> dict[str, list[dict[str, str]]]:
        """tag -> rows sharing that tag, built from get_tags(pos) and cached per pos.

        A plain tag -> row dict would silently keep only the last row for a
        shared tag; pronoun tags legitimately repeat across PronType families
        (see the comment above _POS_TSV), so this keeps every row.
        """
        if pos not in self._tag_index_cache:
            index: dict[str, list[dict[str, str]]] = {}
            for row in self.get_tags(pos):
                index.setdefault(row["tag"], []).append(row)
            self._tag_index_cache[pos] = index
        return self._tag_index_cache[pos]

    def analyze(self, form: str) -> list[dict]:
        """Reverse lookup: candidate (lemma, pos, UD features) analyses for a surface form.

        Tries the reverse-stemming path (GreekInflexion.parse()) against every
        loaded pos in turn and maps each raw stemming-rule key to its UD FEATS
        row(s) via _tag_index(pos). Tag strings carry CSG_TAG_PREFIX
        (_ag_features.py) for noun/adjective but not verb; parse() returns the
        bare key regardless of pos, so the prefix is added back here before
        the lookup.

        Ambiguous by design, not just in the linguistic sense: the underlying
        reverse-stemming can over-match, e.g. a masc. 2nd-declension
        nominative singular currently comes back with a spurious NSF/APF
        candidate alongside the correct NSM one -- passed through as-is
        rather than filtered; disambiguation is explicitly out of scope here
        (see the TODO's own deferred "ambiguity model" item).

        Pronoun forms are override-only (no stemming ruleset -- see
        load_pron_lexicons()'s own docstring), so GreekInflexion.parse(),
        which walks the stemming rule set unconditionally, would crash for
        pos="pronoun" -- it is excluded from the pos loop entirely rather
        than loaded and discarded. A form that is only a pronoun (never also
        a verb/noun/adjective surface form) therefore yields [] -- pronoun
        reverse-lookup would need a separate form_override-scanning path,
        not attempted here.

        Returns [] for a form matching nothing in any loaded pos's lexicon.
        """
        results = []
        for pos in ("verb", "noun", "adjective"):
            gi = self._get_gi(pos)
            dot = "" if pos == "verb" else CSG_TAG_PREFIX
            index = self._tag_index(pos)
            for lemma, key in gi.parse(form):
                for row in index.get(dot + key, ()):
                    results.append({
                        "lemma": lemma,
                        "pos": pos,
                        "tag": row["tag"],
                        "features": self._row_features(row),
                    })
        return results

    def list_lemmas(self, pos: str) -> list[str]:
        if pos not in ("verb", "noun", "adjective", "pronoun"):
            return []
        if pos not in self._lemma_cache:
            # A fresh, uncached load -- NOT self._get_gi(pos)/self._gi_cache[pos].
            # Querying .generate()/.inflect() for a lemma absent from the loaded
            # lexicon has a documented side effect upstream (inflexion library):
            # it can add a phantom stem entry to the shared Lexicon object for
            # that lemma. Once this instance's cached _gi_cache[pos] has been used
            # for any such query (e.g. paradigm() called for lemmas outside this
            # lexicon, as a tagging/coverage loop over a full vocabulary would),
            # gi.lexicon.lemma_to_stems no longer reflects only what the bundled
            # YAML actually contains. list_lemmas must stay correct regardless of
            # what this instance has already been asked about, so it computes its
            # own independent copy rather than trusting the shared cache -- and
            # caches *that* result separately, in a dict .generate()/.paradigm()
            # never write to, so repeat calls don't pay for a fresh YAML reload.
            gi = self._loaders()[pos](list(self._lexicons))
            lemmas = set(gi.lexicon.lemma_to_stems.keys())
            lemmas.update(lemma for lemma, _ in gi.form_override.keys())
            self._lemma_cache[pos] = sorted(lemmas)
        return self._lemma_cache[pos]

    def paradigm(self, lemma: str, pos: str) -> dict[str, set[str]]:
        """Return the full paradigm as a dict keyed by TVM/CSG string.

        Raises:
            ValueError: if pos is not "verb", "noun", "adjective", or "pronoun"
        """
        if pos in ("noun", "adjective"):
            cache_key = (lemma, pos)
            if cache_key not in self._paradigm_cache:
                self._paradigm_cache[cache_key] = self._build_nominal_cache(lemma, pos)
            return dict(self._paradigm_cache[cache_key])
        if pos == "verb":
            cache_key = (lemma, pos)
            if cache_key not in self._paradigm_cache:
                self._paradigm_cache[cache_key] = self._build_verb_paradigm(lemma)
            return dict(self._paradigm_cache[cache_key])
        if pos == "pronoun":
            return dict(self._get_pronoun_cache(lemma))
        raise ValueError(f"Unknown pos: {pos!r}. Expected 'verb', 'noun', 'adjective', or 'pronoun'.")

    def _build_verb_paradigm(self, lemma: str) -> dict[str, set[str]]:
        gi = self._get_gi("verb")
        result: dict[str, set[str]] = {}
        # _tag_index already caches tag -> rows per instance; reused here as a
        # plain membership check rather than rebuilding a separate set from
        # get_tags() on every call.
        known_tags = self._tag_index("verb")
        for t in _VERB_TENSES:
            for v in _VERB_VOICES:
                # indicative / subjunctive / optative
                for m in "ISO":
                    for pn in _VERB_PERSONS:
                        key = f"{t}{v}{m}.{pn}"
                        if pn in _VERB_DUAL_PERSONS and key not in known_tags:
                            continue
                        forms = self._sweep_form(gi, lemma, key, tags=_VERB_TAGS)
                        if forms:
                            result[key] = forms
                # imperative
                for pn in _VERB_IMP_PN:
                    key = f"{t}{v}D.{pn}"
                    if pn in _VERB_DUAL_PERSONS and key not in known_tags:
                        continue
                    forms = self._sweep_form(gi, lemma, key, tags=_VERB_TAGS)
                    if forms:
                        result[key] = forms
                # infinitive
                key = f"{t}{v}N"
                forms = self._sweep_form(gi, lemma, key, tags=_VERB_TAGS)
                if forms:
                    result[key] = forms
                # participle (all 45 case/number/gender/dual cells -- same
                # _CSG_KEYS enumeration nouns/adjectives use). The claim
                # that used to be here -- "no participle in the lexicon
                # has dual data, so those cells never actually surface
                # anything" -- was wrong: dual participles are regularly
                # formed for many verbs (e.g. αἰνέω -> PAP.NDF αἰνεούσα),
                # confirmed directly against real paradigm() output, not
                # assumed. Most (lemma, tense, voice) combinations still
                # come back empty, but not uniformly/predictably enough
                # to safely prune the way the person-based dual sweep
                # was (that had a clean, verb-tags.tsv-backed allowlist
                # of exactly which combos work; participles have no such
                # TSV coverage at all to check against).
                for csg in _CSG_KEYS:
                    key = f"{t}{v}P.{csg}"
                    forms = self._sweep_form(gi, lemma, key, tags=_VERB_TAGS)
                    if forms:
                        result[key] = forms
        return result
