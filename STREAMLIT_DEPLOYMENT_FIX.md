# Streamlit Community Cloud Python 3.14 fix

## Reported symptom

The application opened a page stating that Python 3.14.7 was unsupported and required Python 3.12. That message came from an intentional runtime guard in the previous `app.py`; it was not a Streamlit platform error.

## Changes in this repository

1. Removed the Python 3.12-only runtime guard.
2. Updated the default dependency set to Python 3.14-compatible wheels.
3. Updated MediaPipe from 0.10.35 to 1.0.1 and switched to direct MediaPipe Tasks module imports.
4. Added a metadata-only OpenCV shim that installs `opencv-contrib-python-headless`, avoiding desktop GUI libraries on Community Cloud.
5. Kept `packages.txt` empty to avoid the prior Debian/FFmpeg APT conflict.
6. Added an automatic OpenCV motion/silhouette fallback when MediaPipe or its model cannot initialize.
7. Added explicit engine diagnostics and result warnings so proxy landmarks cannot be confused with anatomical detections.
8. Kept XGBoost, LightGBM, and TensorFlow outside the default cloud build.

## Redeployment

Push all files to the same GitHub branch and reboot the existing Streamlit app. The current Python 3.14 deployment can be reused.
