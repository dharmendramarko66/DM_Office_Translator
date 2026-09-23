"""--version flag और version-consistency के tests।"""

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import STABLE_DIR

try:
    import soht_version  # conftest STABLE_DIR को sys.path में रखता है
except ImportError:  # pragma: no cover
    pytest.skip("soht_version import नहीं हुआ", allow_module_level=True)


def _run_version_flag(script_name):
    return subprocess.run(
        [sys.executable, str(STABLE_DIR / script_name), "--version"],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_version_constant_single_source():
    # यही एक जगह version बदलनी चाहिए।
    assert soht_version.APP_VERSION == "2.0.7"


def test_e2h_version_flag():
    result = _run_version_flag("english_to_hindi_hybrid.py")
    assert result.returncode == 0
    assert soht_version.APP_VERSION in result.stdout
    assert "English" in result.stdout


def test_h2e_version_flag():
    result = _run_version_flag("hindi_to_english_hybrid.py")
    assert result.returncode == 0
    assert soht_version.APP_VERSION in result.stdout
    assert "Hindi" in result.stdout


def test_deb_control_version_matches():
    control = (
        Path(__file__).resolve().parent.parent
        / "packaging" / "DEBIAN" / "control"
    ).read_text()
    assert f"Version: {soht_version.APP_VERSION}" in control
