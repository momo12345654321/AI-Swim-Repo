# Streamlit Community Cloud deployment checklist

## 1. Replace the GitHub repository

Upload every file and folder from the regenerated ZIP to the repository root. Delete obsolete dependency files from the earlier Python 3.12 version.

Critical root files:

- `app.py`
- `ai_pipeline.py`
- `requirements.txt`
- `packages.txt` (empty)
- `.python-version`
- `runtime.txt`
- `.streamlit/config.toml`
- `vendor/opencv_contrib_python-4.14.0.94-py3-none-any.whl`

## 2. Confirm the runtime and requirements

`.python-version`:

```text
3.14
```

`runtime.txt`:

```text
python-3.14
```

`requirements.txt` must include:

```text
streamlit==1.64.0
mediapipe==1.0.1
numpy==2.5.3
pandas==3.0.6
scikit-learn==1.9.1
```

`packages.txt` must be empty.

## 3. Update the existing app

1. Commit and push the regenerated repository to the branch used by Streamlit.
2. Open **Manage app**.
3. Reboot the app, or wait for the GitHub push to trigger a rebuild.
4. Keep the main file path as `app.py`.

The screenshot already shows Python 3.14.7, which this repository supports. You do not need the previous Python 3.12 repair screen or a delete/recreate cycle.

## 4. Verify

The app should open with the video uploader rather than a runtime-blocking message. In the sidebar, open **Deployment diagnostics** and run the dependency check.

- MediaPipe ready: Automatic mode uses anatomical pose landmarks.
- MediaPipe unavailable: Automatic mode uses the clearly labelled OpenCV motion fallback.
- OpenCV and bundled FFmpeg must report ready.
