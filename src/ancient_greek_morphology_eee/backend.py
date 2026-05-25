from ancient_greek_morphology_eee._ag_features import ag_verb_key, ag_noun_key, ag_adj_key

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

    def __init__(self) -> None:
        self._gi_verb = None
        self._gi_noun = None
        self._gi_adj  = None
        self._paradigm_cache: dict[tuple[str, str], dict[str, set[str]]] = {}

    def _get_gi(self, pos: str):
        from greek_inflexion_eee import load_default, load_noun_default, load_adj_default
        if pos == "verb":
            if self._gi_verb is None:
                self._gi_verb = load_default()
            return self._gi_verb
        if pos == "noun":
            if self._gi_noun is None:
                self._gi_noun = load_noun_default()
            return self._gi_noun
        if pos == "adjective":
            if self._gi_adj is None:
                self._gi_adj = load_adj_default()
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
                set(gi.generate(lemma, key_mid).keys()) |
                set(gi.generate(lemma, key_pass).keys())
            )
        return set(gi.generate(lemma, key).keys())

    def _inflect_nominal(self, lemma: str, features: dict[str, str], pos: str) -> set[str]:
        cache_key = (lemma, pos)
        if cache_key not in self._paradigm_cache:
            self._paradigm_cache[cache_key] = self._build_nominal_cache(lemma, pos)
        cache = self._paradigm_cache[cache_key]
        suffix = (ag_noun_key if pos == "noun" else ag_adj_key)(features)
        if suffix is None:
            # No Gender — union across all genders for this case/number
            case = features['Case']
            number = features['Number']
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
        for csgsuffix in _CSG_KEYS:
            forms = set(gi.generate(lemma, csgsuffix).keys())
            if forms:
                # store with dot prefix to match ag_noun_key / ag_adj_key output
                cache["." + csgsuffix] = forms
        return cache

    def list_lemmas(self, pos: str) -> list[str]:
        if pos not in ("verb", "noun", "adjective"):
            return []
        gi = self._get_gi(pos)
        return sorted(gi.lexicon.lemma_to_stems.keys())

    def analyze(self, form: str, pos: str | None = None) -> list[dict[str, str]]:
        """Not implemented in v1. Always raises AnalysisNotSupportedError."""
        from eee import AnalysisNotSupportedError
        raise AnalysisNotSupportedError("AncientGreekBackend")

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
                        forms = set(gi.generate(lemma, key).keys())
                        if forms:
                            result[key] = forms
                # imperative
                for pn in _VERB_IMP_PN:
                    key = f"{t}{v}D.{pn}"
                    forms = set(gi.generate(lemma, key).keys())
                    if forms:
                        result[key] = forms
                # infinitive
                key = f"{t}{v}N"
                forms = set(gi.generate(lemma, key).keys())
                if forms:
                    result[key] = forms
                # participle (nom/gen sg all genders)
                for csg in ["NSM", "NSF", "NSN", "GSM", "GSF", "GSN"]:
                    key = f"{t}{v}P.{csg}"
                    forms = set(gi.generate(lemma, key).keys())
                    if forms:
                        result[key] = forms
        return result
