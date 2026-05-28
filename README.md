# ancient-greek-backend-eee

Ancient Greek (ISO 639-2: `grc`) morphology backend for the
Ελληνικά Εκπαιδευτικά Εργαλεία (EEE) — Greek Language Educational Tools.

Implements `AncientGreekBackend`, satisfying the `MorphologyBackend` protocol
defined in the [`eee`](https://codeberg.org/EEE-project/eee) package.

Wraps [greek-inflexion-eee](https://codeberg.org/EEE-project/greek-inflexion-eee),
a fork of James Tauber's `greek-inflexion` library.


## Installation

```bash
pip install "ancient-greek-backend-eee @ git+https://codeberg.org/EEE-project/ancient-greek-backend-eee.git"
```


## Usage

```python
from ancient_greek_backend_eee import AncientGreekBackend

backend = AncientGreekBackend()
forms = backend.inflect("λύω", {
    "VerbForm": "Fin", "Tense": "Pres", "Voice": "Act",
    "Mood": "Ind", "Person": "1", "Number": "Sing"
}, "verb")
# {"λύω"}
```


## Development

```bash
uv sync --dev
uv run pytest
```


## Status

v0.2.0 — implemented. `inflect()`, `paradigm()`, and `list_lemmas()` are available for verbs, nouns, and adjectives.

Coverage is limited to the stems present in the `greek-inflexion-eee` lexicon (Pratt nouns, a small set of verbs and adjectives).
