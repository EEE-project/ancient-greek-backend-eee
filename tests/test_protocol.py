"""Protocol compliance and lazy-load tests."""
import subprocess
import sys

import pytest

from ancient_greek_morphology_eee import AncientGreekBackend
from eee._protocol import MorphologyBackend
from eee import AnalysisNotSupportedError


def test_has_language_attribute():
    assert AncientGreekBackend.language == "grc"


def test_has_inflect_method():
    assert callable(AncientGreekBackend.inflect)


def test_has_analyze_method():
    assert callable(AncientGreekBackend.analyze)


def test_protocol_isinstance():
    backend = AncientGreekBackend()
    assert isinstance(backend, MorphologyBackend)


def test_analyze_raises():
    backend = AncientGreekBackend()
    with pytest.raises(AnalysisNotSupportedError, match="AncientGreekBackend"):
        backend.analyze("λόγου")


def test_lazy_load_no_import_on_module_import():
    script = (
        "import ancient_greek_morphology_eee; "
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
