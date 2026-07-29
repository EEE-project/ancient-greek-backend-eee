# ancient-greek-backend-eee

Ancient Greek (ISO 639-2: `grc`) morphology backend for the
Ελληνικά Εκπαιδευτικά Εργαλεία (EEE) — Greek Language Educational Tools.

Implements `AncientGreekBackend`, satisfying the `MorphologyBackend` protocol
defined in the [`eee`](https://github.com/EEE-project/eee-project) package.

🔓 Open source:
- prod — https://github.com/EEE-project/ancient-greek-backend-eee
- prod mirror — https://gitlab.com/EEE-project/ancient-greek-backend-eee
- dev — https://codeberg.org/EEE-project/ancient-greek-backend-eee

💬 Community: https://telegram.me/eee_greek

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

# Named historical period (avoids hand-copying the lexicon list; the lexicon
# names are an implementation detail behind the period, not the identifier)
backend = AncientGreekBackend.for_period("byzantine")
# same as: AncientGreekBackend(lexicons=["lxx", "morphgnt", "pratt", "ltrg", "lsj", "byzantine"])

# Other periods: "epic" (Homer), "attic" (Classical Attic — pratt+ltrg+lsj),
# "hellenistic_koine" (Septuagint), "roman_koine" (NT)

# ...with extra lexicons layered on top of the preset
backend = AncientGreekBackend.for_period("epic", extra_lexicons=["odyssey_morpheus"])

# Multiple periods union into one backend (order doesn't affect the result —
# lexicon merging is a set union, confirmed empirically, not a sequential
# override)
backend = AncientGreekBackend.for_period("epic", "attic", "hellenistic_koine", "roman_koine")

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

For `grc`, [unimorph-backend-eee](https://codeberg.org/EEE-project/unimorph-backend-eee)
is the other available backend. Coverage is complementary rather than one
superseding the other: θεός is in this package only; βοηθός is in `unimorph`
only.


## Implementation

Rule-based generator. A YAML stem database stores principal stems (e.g. `βαλλ`,
`βαλ`) for each lemma; `stemming.yaml` maps morphological keys to stem-slots
and endings; a separate accentuation engine applies Attic accent rules. Forms
are generated on demand — not pre-computed.

Adding a new lemma requires annotating its principal stems; the rule engine
then generates the full paradigm automatically.


## Limitations

- Two-termination adjectives (ἀληθής, ἄδικος, μείζων, ἐυπλόκαμος) share
  Masc/Fem forms, generated directly under their own Masc and Fem keys in
  every bundled lexicon — no runtime fallback. There used to be one
  (`_inflect_nominal`: fall back to the Fem key when Masc was absent), added
  for `ἀληθής` specifically, but it fired for *any* adjective with a missing
  Masc key — confirmed silently wrong for `ἴσος` (regular 2-1-2, Masc/Fem
  genuinely differ), which returned the Fem form as if it were Masc rather
  than an empty set. Removed entirely once every genuinely-2-termination
  adjective's data was independently verified complete (real Perseids
  Morpheus lookups, not declension-class guessing) — see
  [greek-inflexion-eee#3](https://codeberg.org/EEE-project/greek-inflexion-eee/pulls/3)
  and [issue #11](https://codeberg.org/EEE-project/ancient-greek-backend-eee/issues/11).
  Querying a gender an adjective genuinely lacks now always returns an empty
  set, never a wrong-gender substitute.
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


