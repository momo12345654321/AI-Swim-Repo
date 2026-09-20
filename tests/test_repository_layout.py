"""Static checks for the GitHub and Streamlit Community Cloud package."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WHEEL = "vendor/opencv_contrib_python-4.14.0.94-py3-none-any.whl"


def test_required_files_exist() -> None:
    required = [
        "app.py",
        "ai_pipeline.py",
        "requirements.txt",
        "requirements-optional-boosters.txt",
        "packages.txt",
        ".python-version",
        "runtime.txt",
        ".streamlit/config.toml",
        WHEEL,
        "AUTHORS.md",
    ]
    missing = [name for name in required if not (ROOT / name).exists()]
    assert not missing, f"Missing repository files: {missing}"


def test_python_runtime_hints() -> None:
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.14"
    assert (ROOT / "runtime.txt").read_text(encoding="utf-8").strip() == "python-3.14"


def test_apt_package_list_is_empty() -> None:
    assert (ROOT / "packages.txt").read_text(encoding="utf-8").strip() == ""


def test_cloud_requirements() -> None:
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    expected = [
        "--only-binary=:all:",
        "streamlit==1.64.0",
        "mediapipe==1.0.1",
        "opencv_contrib_python-4.14.0.94-py3-none-any.whl",
        "imageio-ffmpeg==0.6.0",
        "numpy==2.5.3",
        "pandas==3.0.6",
        "scikit-learn==1.9.1",
        "joblib==1.5.3",
    ]
    for item in expected:
        assert item in text, f"Missing requirement: {item}"
    assert 'python_version < "3.13"' not in text


def test_headless_shim_metadata() -> None:
    wheel = ROOT / WHEEL
    assert zipfile.is_zipfile(wheel)
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(name for name in archive.namelist() if name.endswith("METADATA"))
        metadata = archive.read(metadata_name).decode("utf-8")
    assert "Name: opencv-contrib-python" in metadata
    assert "Version: 4.14.0.94" in metadata
    assert "opencv-contrib-python-headless == 4.14.0.94" in metadata


def test_optional_boosters_are_not_default() -> None:
    default_text = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    optional_text = (ROOT / "requirements-optional-boosters.txt").read_text(encoding="utf-8").lower()
    assert not re.search(r"^xgboost", default_text, flags=re.MULTILINE)
    assert not re.search(r"^lightgbm", default_text, flags=re.MULTILINE)
    assert re.search(r"^xgboost", optional_text, flags=re.MULTILINE)
    assert re.search(r"^lightgbm", optional_text, flags=re.MULTILINE)


def test_credits_are_present() -> None:
    combined = "\n".join(
        (ROOT / name).read_text(encoding="utf-8", errors="ignore")
        for name in ["app.py", "ai_pipeline.py", "README.md", "AUTHORS.md"]
    )
    assert "Jasper Ding" in combined
    assert "Dr. Qingyang Xiao" in combined


def main() -> None:
    test_required_files_exist()
    test_python_runtime_hints()
    test_apt_package_list_is_empty()
    test_cloud_requirements()
    test_headless_shim_metadata()
    test_optional_boosters_are_not_default()
    test_credits_are_present()
    print("Repository layout and Python 3.14 deployment checks passed.")


if __name__ == "__main__":
    main()
