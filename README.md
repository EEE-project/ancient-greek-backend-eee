# ancient-greek-backend-eee

Ancient Greek (ISO 639-2: `grc`) morphology backend for the
Ελληνικά Εκπαιδευτικά Εργαλεία (EEE) — Greek Language Educational Tools.

Implements `AncientGreekBackend`, satisfying the `MorphologyBackend` protocol
defined in the [`eee`](https://codeberg.org/EEE-project/eee-project) package.

Wraps [greek-inflexion-eee](https://codeberg.org/EEE-project/greek-inflexion-eee),
a fork of James Tauber's [greek-inflexion](https://github.com/jtauber/greek-inflexion)
library. License: **MIT**.

Per the upstream README, the library "can precisely generate (i.e. without
over-generation) all the forms in the verbal paradigms in Louise Pratt's _The
Essentials of Greek Grammar_, Helma Dik's _Nifty Greek Handouts_, and Keller
and Russell's _Learn to Read Greek_. It can also generate the nouns in Pratt."
Nominal coverage in this package remains limited to those Pratt nouns — Dik's
and Keller/Russell's nouns are not yet included.

**Period:** Classical Attic Greek (~5th–4th century BCE) is the base pattern —
accentuation logic broadly follows Classical Attic conventions, and Ionic/Doric
forms are not generated from the Pratt/Dik/LTRG teaching stems. The corpus
lexicons (`homer`, `lxx`, `morphgnt`, `lsj`, `morpheus`, `byzantine`) extend
vocabulary into other periods and dialects while reusing this same stemming and
accentuation engine — see the period column in the lexicon tables below.


## Installation

```bash
pip install "ancient-greek-backend-eee @ git+https://codeberg.org/EEE-project/ancient-greek-backend-eee.git"
```


## Usage

```python
from ancient_greek_backend_eee import AncientGreekBackend

# Default: Pratt lexicon (20 teaching verbs)
backend = AncientGreekBackend()

# Corpus lexicon — by name
backend = AncientGreekBackend(lexicons=["homer"])

# Merged corpora
backend = AncientGreekBackend(lexicons=["homer", "lxx", "morphgnt"])

# Custom lexicon file (absolute path, same YAML format)
backend = AncientGreekBackend(lexicons=["pratt", "/path/to/my_course.yaml"])

forms = backend.inflect("ἀκούω", {
    "VerbForm": "Fin", "Tense": "Pres", "Voice": "Act",
    "Mood": "Imp", "Person": "2", "Number": "Sing"
}, "verb")
# {"ἄκουε"}

backend.analyze("βάλλω")
# [{"lemma": "βάλλω", "pos": "verb", "tag": "PAI.1S",
#   "features": {"Tense": "Pres", "VerbForm": "Fin", "Voice": "Act", "Mood": "Ind", "Person": "1", "Number": "Sing"}},
#  {"lemma": "βάλλω", "pos": "verb", "tag": "PAS.1S", ...}]  # syncretic with the subjunctive
```

### Lexicon flavors

The `lexicons` parameter selects the vocabulary for **verbs and nouns**.
Adjectives always use the bundled Pratt paradigm lexicon (no additional adj lexicons yet).

**Verbs:**

| Name | Verbs | Source | Period / dialect |
|------|------:|--------|-----------------|
| `"pratt"` (default) | 20 | Pratt textbook | teaching |
| `"dik"` | 10 | Dik textbook | teaching |
| `"ltrg"` | 34 | LTRG textbook | teaching |
| `"homer"` | 2335 | Homeric corpus | Epic/Ionic, ~800 BCE |
| `"lxx"` | 1905 | Septuagint | Biblical κοινή, ~250–100 BCE |
| `"morphgnt"` | 1848 | New Testament | κοινή, ~1st c. CE |
| `"lsj"` | 9 | LSJ, hand-authored | Classical Attic |
| `"morpheus"` | 46 | Morpheus-confirmed attested forms | Epic/Homeric (mixed) |

**Nouns** — Pratt base is always included; the others extend it:

| Name | Nouns | Source |
|------|------:|--------|
| `"pratt"` | 26 | Pratt textbook paradigm nouns |
| `"homer"` | 15 | Homeric Odyssey/Iliad vocabulary |
| `"lsj"` | 18 | LSJ, hand-authored, Classical Attic |
| `"morpheus"` | 62 | Morpheus-confirmed attested forms, Epic/Homeric (mixed) |

`"lsj"` and `"morpheus"` are hand-authored/Morpheus-confirmed respectively, not
generated from a bulk corpus — see
[greek-inflexion-eee](https://codeberg.org/EEE-project/greek-inflexion-eee)'s
own README for how each is built and its exact scope. `"morpheus"` holds
*verbatim attested forms* (not `stems:` + generated endings) for lemmas the
stem-based lexicons can't handle cleanly — athematic `-μι` verbs, contract
verbs, compounds, deponents, non-2nd-declension nouns, oxytone nouns, and
irregular/suppletive nouns (Ζεύς).

Multiple names are merged additively. Absolute file paths load custom YAML lexicons.


Auto-registered via two entry point groups on install:
- `eee_project.backends.v1` → key `grc` (default backend for Ancient Greek)
- `eee_project.named_backends.v1` → key `ancient-greek` (selectable via `backend="ancient-greek"`)

This means `eee.inflect(..., language="grc")` and `eee.inflect(..., backend="ancient-greek")`
both work without explicit registration.


## Implementation

Rule-based generator. A YAML stem database stores principal stems (e.g. `βαλλ`,
`βαλ`) for each lemma; `stemming.yaml` maps morphological keys to stem-slots
and endings; a separate accentuation engine applies Attic accent rules. Forms
are generated on demand — not pre-computed.

Adding a new lemma requires annotating its principal stems; the rule engine
then generates the full paradigm automatically.


## Limitations

- Two-termination adjectives (ἀληθής, ἄδικος) share Masc/Fem forms. The
  database stores only Fem keys for oblique cases; the backend falls back to
  Fem automatically when a Masc key is absent.
- Nominal coverage is limited to Pratt. Nouns from Dik and Keller/Russell are
  not yet included.
- `analyze()` (reverse lookup) has no disambiguation: it returns every
  candidate the underlying reverse-stemming produces, including known
  over-matches (e.g. a masc. 2nd-declension nominative singular currently
  also comes back tagged as fem. nom./acc. plural). It also does not cover
  pronouns — their lexicons are override-only with no stemming ruleset for
  `parse()` to walk, so `pos="pronoun"` is skipped rather than attempted.


## Development

```bash
uv sync --dev
uv run pytest
```


## Status

v0.6.0 — `inflect()`, `paradigm()`, `list_lemmas()`, `get_slot_templates()`, and `analyze()` for verbs, nouns, adjectives, and pronouns.
Verb and noun coverage depends on the selected lexicon(s); adjectives use the Pratt paradigm lexicon.
Adjective paradigms include adverb derivation: regular `-ος/-ός` → `-ῶς` (e.g. `καλός` → `καλῶς`),
accessible via the `"ADV"` key in `paradigm()` or the `"ag-paradigm"` tag type in slot templates.

**v0.6.0** — Added `analyze(form)`: reverse lookup from a surface form to
candidate `{"lemma", "pos", "tag", "features"}` analyses, one dict per
candidate. Wraps `greek_inflexion_eee.GreekInflexion.parse()` (already
present upstream, not previously surfaced) and maps its raw stemming-rule
key to UD FEATS via the same per-pos tag table `get_tags()`/
`get_slot_templates()` already use. Ambiguous by design — a syncretic
surface form legitimately yields multiple candidates, and the underlying
reverse-stemming can also over-match (see Limitations) — disambiguation is
explicitly out of scope. Pronouns are not covered (see Limitations).

**v0.5.0** — Added `"pronoun"` as a fourth part of speech, covering 10 lemmas
across four families: personal (ἐγώ, σύ — Case+Number+Person shape, no
Gender), demonstrative/relative/interrogative/indefinite/reciprocal (οὗτος,
ἐκεῖνος, ὅδε, ὅς, τίς, τις, ὅστις, ἀλλήλων — Case+Number+Gender shape, same
as adjectives). `SlotTemplate.features` includes a UD FEATS `PronType`
(`Prs`/`Dem`/`Rel`/`Int`/`Ind`/`Rcp`) on every pronoun cell. The
adjective-like families include genuine dual forms shipped in their lexicon
data; regular nouns and adjectives reach the same dual cells structurally
but mostly lack data there — a handful of individually-attested noun duals
(e.g. κῆρυξ's `.NDM` κήρυκε) are the exception. **Caveat:** αὐτός (the standard
3rd-person pronoun / intensive "self"/"same") is intentionally *not* part of
`pos="pronoun"` — it declines exactly like a regular 2-1-2 adjective and is
reachable only via `pos="adjective"`; `list_lemmas("pronoun")` will never
surface it.

**v0.4.1** — Documentation: added Source/License, Period, Implementation, and
Limitations sections (previously only in `eee-project`'s now-removed
`docs/backends.md`). No functional change.

**v0.4.0** — Dual number exposed for verbs (2nd/3rd person only — Ancient
Greek has no 1st-person dual): `get_slot_templates()`/`paradigm()` now
include `2D`/`3D` slots wherever the underlying `greek-inflexion-eee`
stemming engine actually has dual rules (confirmed: Present/Imperfect/
Future/Perfect active indicative, Present active imperative, plus a few
subjunctive/optative/3rd-imperative combinations found via the exhaustive
`paradigm()` sweep) — was previously generated correctly but never queried,
since `_VERB_PERSONS`/`_VERB_IMP_PN` (Python) and `verb-tags.tsv` (the data
`get_slot_templates()` reads) both hardcoded singular/plural only. Aorist and
Middle/Passive dual remain genuinely unsupported (zero rule coverage in the
stemming engine, not a gap in this fix) and correctly return nothing rather
than a wrong or invented form. Noun dual is a separate, larger gap: the
stemming engine has zero declension rules for it at all (only 3 individually
attested forms exist project-wide, via `greek-inflexion-eee`'s `morpheus`
lexicon) — not addressed here. Also tightens two tests that were tolerant of
a since-fixed upstream bug (`greek-inflexion-eee` v0.4.1) where macron-bearing
stems like λύω leaked a stray combining mark into acute-accented forms.

**v0.3.3** — `list_lemmas()` no longer trusts the shared, mutable
`GreekInflexion` cache: the upstream `inflexion` library's `.generate()` has
an undocumented side effect where querying an unknown lemma can add a
phantom stem entry to the shared lexicon object, so a `list_lemmas()` call
made after any unrelated `.paradigm()`/`.inflect()` query on the same
instance (e.g. a coverage/tagging loop over a full vocabulary) could return
lemmas that were never actually in the loaded lexicon. `list_lemmas()` now
does its own independent, uncached load every call.

**v0.3.2** — `list_lemmas()` now includes lemmas that only exist via a
`forms:` override (e.g. the `byzantine` and `morpheus` lexicons in
`greek-inflexion-eee`, which have zero `stems:` entries) — previously it only
enumerated the stem-based lexicon, so a `forms:`-only lemma was invisible to
any "pick a word" UI even though `.inflect()`/`.paradigm()` correctly
returned data for it.

**v0.3.1** — `paradigm()` now restricts a noun's full paradigm table to its own
detected gender(s), instead of mechanically generating all three for every
noun. Previously *every* noun using a bare `stems: {noun: ...}` entry showed
spurious forms for genders it doesn't have (e.g. `Ζεύς` getting a plural and
a feminine it grammatically can't have). An explicit `forms:` override is
always trusted regardless of the detected gender, so genuinely dual-gender
nouns (`γείτων` "neighbor", `ἅλς` "salt"/"sea") keep all their real forms.
Adjectives are unaffected (they genuinely decline through all three genders).
