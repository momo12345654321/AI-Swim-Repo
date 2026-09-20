# AI Swimming Coach - Streamlit Community Cloud Repository

A GitHub-ready Streamlit prototype that accepts a swimming video, creates an annotated video and machine-readable time series, generates coaching insights, trains supervised-learning baselines, and collects swimmer or coach feedback.

## Project team

- **Author:** Jasper Ding
- **Advisor:** Dr. Qingyang Xiao

## Python 3.14 deployment fix

This version is built for the Python 3.14 runtime shown by Streamlit Community Cloud. The previous repository intentionally stopped on Python 3.14 and displayed a repair page. That guard has been removed.

The dependency set now uses Python 3.14 wheels for Streamlit, OpenCV, NumPy, pandas, and scikit-learn. MediaPipe was updated to the current Tasks package layout. Because MediaPipe's published classifiers may lag behind the cloud runtime, the pipeline also has an automatic OpenCV motion/silhouette fallback. The fallback keeps the app operational if MediaPipe cannot import, initialize, or download its model, and it is always labelled as a proxy rather than anatomical pose detection.

## Analysis engines

- **Automatic (recommended):** attempts MediaPipe Tasks first, then uses the OpenCV fallback when necessary.
- **MediaPipe only:** requires the pose package and model to initialize successfully.
- **OpenCV fallback only:** uses motion/silhouette proxy landmarks and does not require MediaPipe inference.

The app displays the engine used in the results. Do not treat fallback proxy angles as medical or biomechanical ground truth.

## Main functions

- Upload MP4, MOV, M4V, AVI, MKV, or WMV video containers.
- Extract 33 MediaPipe pose landmarks when the pose engine is available.
- Continue with a clearly labelled 33-point OpenCV motion/silhouette proxy when it is not.
- Generate an annotated video and downloadable analysis bundle.
- Calculate joint-angle, body-line, head-alignment, kick, movement-speed, and symmetry time series.
- Generate prioritized coach-style observations and training drills.
- Train Logistic Regression, Random Forest, and Gradient Boosting baselines.
- Prepare sequence windows for an optional Conv1D plus bidirectional LSTM model.
- Collect ratings and demonstrate reward-based recommendation ranking.

## Repository structure

```text
.
|-- app.py                              Streamlit entry point
|-- ai_pipeline.py                      Pose/fallback, feature, ML, and feedback pipeline
|-- deep_learning_template.py           Optional TensorFlow/Colab template
|-- requirements.txt                    Python 3.14 Community Cloud dependencies
|-- requirements-optional-boosters.txt  Optional XGBoost and LightGBM
|-- packages.txt                        Empty to avoid mixed-Debian APT conflicts
|-- .python-version                     Python 3.14 host hint
|-- runtime.txt                         Python 3.14 compatibility hint
|-- DEPLOYMENT_CHECKLIST.md             Exact deployment steps
|-- STREAMLIT_DEPLOYMENT_FIX.md         Technical explanation
|-- AUTHORS.md                          Project credits
|-- vendor/
|   `-- opencv_contrib_python-4.14.0.94-py3-none-any.whl
|-- .streamlit/config.toml              Upload and theme settings
|-- notebooks/
|-- data/.gitkeep
|-- models/.gitkeep
|-- outputs/.gitkeep
|-- tests/
`-- .github/workflows/streamlit-smoke.yml
```

## Update the existing Streamlit app

1. Extract the ZIP.
2. Replace the files in the GitHub repository root with the extracted contents.
3. Commit and push to the same branch used by Streamlit.
4. In Streamlit Community Cloud, open **Manage app** and choose **Reboot app**. A full delete/recreate is not required for this Python 3.14 build.
5. Confirm the deployment log installs `streamlit==1.64.0`, `mediapipe==1.0.1`, and the Python 3.14 scientific stack.
6. Open **Deployment diagnostics** in the sidebar and run the dependency check.

Keep `packages.txt` empty. FFmpeg is supplied by `imageio-ffmpeg`, and OpenCV uses a headless wheel, so the earlier APT conflict is avoided.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

## Recommended video input

Use a 5-20 second H.264 MP4 clip with the full swimmer visible. A stable side view usually gives the most interpretable results. Underwater refraction, splashes, glare, camera motion, and overlapping limbs can reduce both pose and motion-proxy quality.

## Limitations

- Coaching thresholds are prototype heuristics and need qualified-coach validation.
- OpenCV fallback points are silhouette/motion proxies, not anatomical detections.
- Demonstration labels prove the training pipeline; they are not coach ground truth.
- TensorFlow is excluded from the default cloud build to reduce installation time and memory.
- Community Cloud storage is temporary; download outputs before restart or redeployment.
- This educational prototype is not a medical device or injury assessment.
