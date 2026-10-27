import importlib.util
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).parent.parent / "skills" / "nanobanana" / "scripts" / "nanobanana.py"
)


@pytest.fixture(scope="session")
def nb():
    """The nanobanana script, imported as a module (it isn't an installed package)."""
    spec = importlib.util.spec_from_file_location("nanobanana", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Run every test in an empty directory with no API key in the environment."""
    monkeypatch.chdir(tmp_path)
    for var in (
        "NANOBANANA_API_KEY",
        "NANOBANANA_GEMINI_API_KEY",
        "NANOBANANA_GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "NANOBANANA_MODEL",
    ):
        monkeypatch.delenv(var, raising=False)
