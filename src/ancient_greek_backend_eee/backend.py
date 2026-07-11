import csv
import importlib.resources as _pkg_data

from ancient_greek_backend_eee._ag_features import ag_verb_key, ag_noun_key, ag_adj_key

_POS_TSV = {"noun": "noun-tags.tsv", "adjective": "adj-tags.tsv", "verb": "verb-tags.tsv"}

# All 30 case/number/gender combinations for noun and adjective paradigms
_CSG_KEYS = [
    c + n + g
    for c in "NGDAV"
    for n in "SP"
    for g in "MFN"
]

# Indicative tense/voice/mood combinations for verb paradigm
_VERB_TENSES  = list("PIAFX")   # Pres, Imp, Aor, Fut, Perf
_VERB_VOICES  = list("AMP")
_VERB_PERSONS = ["1S", "2S", "3S", "1P", "2P", "3P"]
_VERB_IMP_PN  = ["2S", "3S", "2P", "3P"]
_VERB_TAGS = {"final-nu-aai.3s"}


class AncientGreekBackend:
    """MorphologyBackend implementation for Ancient Greek (ISO 639-2: grc).

    Wraps greek_inflexion_eee (Pratt lexicon) to generate inflected surface
    forms from Universal Dependencies FEATS dicts.

    Lazy loading: greek_inflexion_eee is not imported at module load time.
    Paradigm results for nouns and adjectives are cached per lemma after
    the first call.

    Exception propagation: library exceptions for unknown lemmas propagate
    unwrapped from generate().
    """

    language = "grc"

    def __init__(
        self, lexicons: "tuple[str, ...] | list[str]" = ("pratt",)
    ) -> None:
        self._lexicons = tuple(lexicons)
        self._gi_verb = None
        self._gi_noun = None
        self._gi_adj  = None
        self._paradigm_cache: dict[tuple[str, str], dict[str, set[str]]] = {}
        self._slot_cache: dict[tuple[str, str], list] = {}
        self._tag_cache: dict[str, list] = {}

    def _get_gi(self, pos: str):
        from greek_inflexion_eee import load_lexicons, load_noun_lexicons, load_adj_lexicons
        if pos == "verb":
            if self._gi_verb is None:
                self._gi_verb = load_lexicons(list(self._lexicons))
            return self._gi_verb
        if pos == "noun":
            if self._gi_noun is None:
                self._gi_noun = load_noun_lexicons(list(self._lexicons))
            return self._gi_noun
        if pos == "adjective":
            if self._gi_adj is None:
                self._gi_adj = load_adj_lexicons(list(self._lexicons))
            return self._gi_adj
        raise ValueError(f"Unknown pos: {pos!r}. Expected 'verb', 'noun', or 'adjective'.")

    def inflect(self, lemma: str, features: dict[str, str], pos: str, **_kw) -> set[str]:
        """Map UD FEATS + pos to a set of inflected surface forms.

        Args:
            lemma: polytonic Greek lemma (must match Pratt lexicon key exactly)
            features: UD FEATS dict (e.g., {"Tense": "Pres", "Voice": "Act", ...})
            pos: one of "verb", "noun", "adjective"

        Returns:
            set[str] of surface forms; empty set if the paradigm path has no forms.

        Raises:
            ValueError: if pos is not "verb", "noun", or "adjective"
            KeyError: if a required feature is absent (propagated from _ag_features)
        """
        if pos == "verb":
            return self._inflect_verb(lemma, features)
        if pos in ("noun", "adjective"):
            return self._inflect_nominal(lemma, features, pos)
        raise ValueError(f"Unknown pos: {pos!r}. Expected 'verb', 'noun', or 'adjective'.")

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
        result = cache.get(suffix, set())
        # Two-termination adjectives (e.g. ἀληθής): Pratt lexicon stores only Fem keys for
        # oblique cases; Masc is identical so fall back to the Fem key when Masc is absent.
        if not result and pos == "adjective" and suffix and suffix.endswith("M"):
            result = cache.get(suffix[:-1] + "F", set())
        return result

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
                # store with dot prefix to match ag_noun_key / ag_adj_key output
                cache["." + csgsuffix] = forms
        if pos == "adjective":
            adv = self._derive_adverb(lemma)
            if adv:
                cache["ADV"] = adv
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
    def _derive_adverb(lemma: str) -> set[str]:
        """Derive adverb from adjective lemma. Handles regular -ος/-ός → -ῶς."""
        import unicodedata
        nfc = unicodedata.normalize("NFC", lemma)
        if nfc.endswith("ός") or nfc.endswith("ος"):
            return {nfc[:-2] + "ῶς"}
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
                         features={k: v for k, v in r.items() if k != "tag"})
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

    def list_lemmas(self, pos: str) -> list[str]:
        if pos not in ("verb", "noun", "adjective"):
            return []
        from greek_inflexion_eee import load_lexicons, load_noun_lexicons, load_adj_lexicons
        # A fresh, uncached load -- NOT self._get_gi(pos)/self._gi_verb etc.
        # Querying .generate()/.inflect() for a lemma absent from the loaded
        # lexicon has a documented side effect upstream (inflexion library):
        # it can add a phantom stem entry to the shared Lexicon object for
        # that lemma. Once this instance's cached _gi_verb has been used for
        # any such query (e.g. paradigm() called for lemmas outside this
        # lexicon, as a tagging/coverage loop over a full vocabulary would),
        # gi.lexicon.lemma_to_stems no longer reflects only what the bundled
        # YAML actually contains. list_lemmas must stay correct regardless of
        # what this instance has already been asked about, so it loads its
        # own independent copy rather than trusting the shared cache.
        loader = {"verb": load_lexicons, "noun": load_noun_lexicons,
                  "adjective": load_adj_lexicons}[pos]
        gi = loader(list(self._lexicons))
        lemmas = set(gi.lexicon.lemma_to_stems.keys())
        lemmas.update(lemma for lemma, _ in gi.form_override.keys())
        return sorted(lemmas)

    def paradigm(self, lemma: str, pos: str) -> dict[str, set[str]]:
        """Return the full paradigm as a dict keyed by TVM/CSG string.

        Raises:
            ValueError: if pos is not "verb", "noun", or "adjective"
        """
        if pos in ("noun", "adjective"):
            cache_key = (lemma, pos)
            if cache_key not in self._paradigm_cache:
                self._paradigm_cache[cache_key] = self._build_nominal_cache(lemma, pos)
            return dict(self._paradigm_cache[cache_key])
        if pos == "verb":
            return self._build_verb_paradigm(lemma)
        raise ValueError(f"Unknown pos: {pos!r}. Expected 'verb', 'noun', or 'adjective'.")

    def _build_verb_paradigm(self, lemma: str) -> dict[str, set[str]]:
        gi = self._get_gi("verb")
        result: dict[str, set[str]] = {}
        for t in _VERB_TENSES:
            for v in _VERB_VOICES:
                # indicative / subjunctive / optative
                for m in "ISO":
                    for pn in _VERB_PERSONS:
                        key = f"{t}{v}{m}.{pn}"
                        forms = set(gi.generate(lemma, key, tags=_VERB_TAGS).keys())
                        if forms:
                            result[key] = forms
                # imperative
                for pn in _VERB_IMP_PN:
                    key = f"{t}{v}D.{pn}"
                    forms = set(gi.generate(lemma, key, tags=_VERB_TAGS).keys())
                    if forms:
                        result[key] = forms
                # infinitive
                key = f"{t}{v}N"
                forms = set(gi.generate(lemma, key, tags=_VERB_TAGS).keys())
                if forms:
                    result[key] = forms
                # participle (nom/gen sg all genders)
                for csg in ["NSM", "NSF", "NSN", "GSM", "GSF", "GSN"]:
                    key = f"{t}{v}P.{csg}"
                    forms = set(gi.generate(lemma, key, tags=_VERB_TAGS).keys())
                    if forms:
                        result[key] = forms
        return result
