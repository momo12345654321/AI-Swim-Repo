"""Static runtime checks for the Python 3.14 cloud build."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_app_has_no_runtime_stop_guard() -> None:
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert "requires Python 3.12" not in source
    assert "Delete the current Community Cloud app" not in source
    assert "SUPPORTED_PYTHON_LABEL" in source
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "set_page_config"
        for node in ast.walk(tree)
    )


def test_pipeline_has_automatic_fallback() -> None:
    source = (ROOT / "ai_pipeline.py").read_text(encoding="utf-8")
    assert 'backend: str = "auto"' in source
    assert "_OpenCVMotionPoseBackend" in source
    assert '"opencv_motion_fallback"' in source


def main() -> None:
    test_app_has_no_runtime_stop_guard()
    test_pipeline_has_automatic_fallback()
    print("Python 3.14 runtime compatibility checks passed.")


if __name__ == "__main__":
    main()
