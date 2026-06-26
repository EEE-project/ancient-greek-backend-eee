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

**Nouns** — Pratt base is always included; `"homer"` extends it:

| Name | Nouns | Source |
|------|------:|--------|
| `"pratt"` | 26 | Pratt textbook paradigm nouns |
| `"homer"` | 15 | Homeric Odyssey/Iliad vocabulary |

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

v0.3.0 — `inflect()`, `paradigm()`, `list_lemmas()`, and `get_slot_templates()` for verbs, nouns, and adjectives.
Verb and noun coverage depends on the selected lexicon(s); adjectives use the Pratt paradigm lexicon.
Adjective paradigms include adverb derivation: regular `-ος/-ός` → `-ῶς` (e.g. `καλός` → `καλῶς`),
accessible via the `"ADV"` key in `paradigm()` or the `"ag-paradigm"` tag type in slot templates.
