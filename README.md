# ancient-greek-backend-eee

Ancient Greek (ISO 639-2: `grc`) morphology backend for the
Ελληνικά Εκπαιδευτικά Εργαλεία (EEE) — Greek Language Educational Tools.

Implements `AncientGreekBackend`, satisfying the `MorphologyBackend` protocol
defined in the [`eee`](https://codeberg.org/EEE-project/eee-project) package.

Wraps [greek-inflexion-eee](https://codeberg.org/EEE-project/greek-inflexion-eee),
a fork of James Tauber's `greek-inflexion` library.


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


## Development

```bash
uv sync --dev
uv run pytest
```


## Status

v0.3.2 — `inflect()`, `paradigm()`, `list_lemmas()`, and `get_slot_templates()` for verbs, nouns, and adjectives.
Verb and noun coverage depends on the selected lexicon(s); adjectives use the Pratt paradigm lexicon.
Adjective paradigms include adverb derivation: regular `-ος/-ός` → `-ῶς` (e.g. `καλός` → `καλῶς`),
accessible via the `"ADV"` key in `paradigm()` or the `"ag-paradigm"` tag type in slot templates.

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
