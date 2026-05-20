# ancient-greek-morphology-eee

Ancient Greek (ISO 639-2: `grc`) morphology backend for the
Ελληνικά Εκπαιδευτικά Εργαλεία (EEE) — Greek Language Educational Tools.

Implements `AncientGreekBackend`, satisfying the `MorphologyBackend` protocol
defined in the [`eee`](https://codeberg.org/EEE-project/eee) package.

Wraps [greek-inflexion-eee](https://codeberg.org/EEE-project/greek-inflexion-eee),
a fork of James Tauber's `greek-inflexion` library.


## Installation

```bash
pip install "ancient-greek-morphology-eee @ git+https://codeberg.org/EEE-project/ancient-greek-morphology-eee.git"
```


## Usage

```python
from ancient_greek_morphology_eee import AncientGreekBackend

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

v0.1.0 — scaffold. `inflect()`, `analyze()`, and `paradigm()` not yet implemented.
Logic is added in sections 04–05 of the `02-ag-morphology` plan.
