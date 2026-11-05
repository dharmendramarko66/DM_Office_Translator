"""Shared pytest fixtures for SOHT engine tests."""

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
STABLE_DIR = PROJECT_DIR / "stable"
PROJECT_DICT_DIR = PROJECT_DIR / "dictionary"

# ताकि engines का `from soht_version import ...` test में भी
# असली module से resolve हो।
sys.path.insert(0, str(STABLE_DIR))


def _load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, STABLE_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def e2h():
    """English → Hindi engine module."""
    return _load_module("english_to_hindi_hybrid.py", "soht_e2h_under_test")


@pytest.fixture(scope="session")
def h2e():
    """Hindi → English engine module."""
    return _load_module("hindi_to_english_hybrid.py", "soht_h2e_under_test")


@pytest.fixture()
def dict_dir(tmp_path):
    """Project dictionaries की एक अलग copy — tests इसे mutate कर सकें।"""
    target = tmp_path / "dictionary"
    target.mkdir()
    for name in (
        "english_to_hindi_dictionary.txt",
        "hindi_to_english_dictionary.txt",
    ):
        shutil.copy(PROJECT_DICT_DIR / name, target / name)
    return target


@pytest.fixture()
def offline(monkeypatch):
    """Offline-only मोड — network calls बिल्कुल नहीं।"""
    monkeypatch.setenv("SOHT_OFFLINE", "1")


@pytest.fixture(autouse=True)
def isolate_user_modes(monkeypatch, tmp_path):
    """हर test को user की अपनी settings से अलग रखें।

    v3.0.5: अगर developer की मशीन पर Alt+T (Online mode) चालू है या
    SOHT_TRANSLIT environment variable सेट है, तो tests गलत तरीके से
    fail हो रहे थे। अब हर test खाली USER_DATA_DIR के साथ चलता है और
    SOHT_TRANSLIT हटा दिया जाता है — tests हमेशा एक जैसे चलेंगे।
    """
    monkeypatch.delenv("SOHT_TRANSLIT", raising=False)

    for module_name in ("soht_e2h_under_test", "soht_h2e_under_test"):
        module = sys.modules.get(module_name)
        if module is not None:
            monkeypatch.setattr(
                module, "USER_DATA_DIR", str(tmp_path), raising=False
            )
