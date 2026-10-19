# Deploy the integrated Lovable-style AI Swimming Coach

**Team:** Author Jasper Ding · Advisor Dr. Qingyang Xiao.

1. Unzip the integrated release on your computer.
2. Upload the extracted **contents**, not the wrapping directory, to the root of your GitHub repo, e.g. `qxiao2ub/ai_swim_coach`.
3. Confirm `app.py`, `swim_ui.py`, `ai_pipeline.py`, `requirements.txt`, `packages.txt`, `.streamlit/config.toml`, `vendor/`, `lovable_ui_source/` and `notebooks/` are all present at the correct paths.
4. Commit to the branch your Streamlit Community Cloud deployment tracks (commonly `main`).
5. Set or verify the app **main file path is `app.py`**. Do not choose a React `.tsx` file: the React source is retained for reference, and the working integration is Streamlit-native.
6. If creating a new Community Cloud app, choose Python **3.14** in Advanced settings. Existing apps retain their configured Python runtime; this repository is based on the supplied Python 3.14 backend.
7. Wait for Python dependencies to install, then launch. **Do not `npm install` or run Vite in Streamlit Cloud.**
8. Verify the navy hero / drop-zone uploader, seven navigation sections, and project credits in the sidebar and About page.
9. Upload a short H.264 MP4. First try Automatic; if MediaPipe model download fails, retry the OpenCV motion fallback. Proxy outputs must be interpreted cautiously.
10. Download the annotated video, CSVs and analysis bundle. Visit Supervised ML and Feedback Learning after analysis for further outputs.

## If launch fails

- Inspect Community Cloud **Manage app → Logs**. An error while installing `requirements.txt` is not a front-end bug. APT errors originate in `packages.txt` and the system image.
- Open **Analysis settings → Deployment diagnostics**. MediaPipe may be unavailable on some Python/OS configurations; OpenCV fallback is available without MediaPipe inference.
- Ensure you uploaded `swim_ui.py` and did not accidentally use an older `app.py`.
- If you see a former red **Python 3.12 repair page**, the previous `app.py` is still in the repository or old deployment. Confirm you committed the new files and rebooted the app.
- Community Cloud instance storage is temporary. Download important outputs before a restart.

## Testing performed for this package

- Python source compilation and AST validation of the Streamlit entry point.
- Source-preservation and integration-mapping checks.
- Smoke tests of both MediaPipe-shim and OpenCV motion fallback on generated sample videos.
- Simulated Streamlit rendering across all seven pages, with and without analyzed data.
- Checks of dependency files, vendor wheel and ZIP integrity.

A live hosted Streamlit Community Cloud launch requires your own GitHub/Streamlit account and cannot be performed by the local offline checks alone.
