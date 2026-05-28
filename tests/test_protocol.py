"""Protocol compliance and lazy-load tests."""
import subprocess
import sys

import pytest

from ancient_greek_backend_eee import AncientGreekBackend

def test_has_language_attribute():
    assert AncientGreekBackend.language == "grc"


def test_has_inflect_method():
    assert callable(AncientGreekBackend.inflect)


def test_lazy_load_no_import_on_module_import():
    script = (
        "import ancient_greek_backend_eee; "
        "import sys; "
        "assert 'greek_inflexion_eee' not in sys.modules, "
        "'greek_inflexion_eee was imported at module level'"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_library_loaded_after_inflect():
    backend = AncientGreekBackend()
    backend.inflect(
        "λύω",
        {"VerbForm": "Fin", "Tense": "Pres", "Voice": "Act",
         "Mood": "Ind", "Person": "1", "Number": "Sing"},
        "verb",
    )
    assert "greek_inflexion_eee" in sys.modules
