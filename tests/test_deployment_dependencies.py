"""Deployment dependency checks for the Python 3.14 Community Cloud build."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_headless_opencv_imports() -> None:
    import cv2

    assert cv2.__version__
    assert hasattr(cv2, "VideoCapture")
    assert hasattr(cv2, "VideoWriter")


def test_bundled_ffmpeg_is_available() -> None:
    import imageio_ffmpeg

    executable = Path(imageio_ffmpeg.get_ffmpeg_exe())
    assert executable.is_file()


def test_mediapipe_tasks_api_when_installed() -> None:
    if importlib.util.find_spec("mediapipe") is None:
        print("MediaPipe is not installed in this local test environment; fallback test covers continuity.")
        return
    from mediapipe.tasks.python.vision import pose_landmarker
    from mediapipe.tasks.python.vision.core import image

    assert hasattr(pose_landmarker, "PoseLandmarker")
    assert hasattr(pose_landmarker, "PoseLandmarkerOptions")
    assert hasattr(image, "Image")


def test_pipeline_exposes_ffmpeg_locator() -> None:
    from ai_pipeline import get_ffmpeg_executable

    executable = get_ffmpeg_executable()
    assert executable is not None
    assert Path(executable).is_file()


def main() -> None:
    test_headless_opencv_imports()
    test_bundled_ffmpeg_is_available()
    test_mediapipe_tasks_api_when_installed()
    test_pipeline_exposes_ffmpeg_locator()
    print("Deployment dependency checks passed.")


if __name__ == "__main__":
    main()
