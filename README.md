# AI Swimming Coach — Lovable UI × Streamlit integration

**Author:** Jasper Ding  
**Advisor:** Dr. Qingyang Xiao

A GitHub-ready, single-service Streamlit Community Cloud app merging:

1. The existing Python `AI-Swim-Repo-main.zip` (computer vision, annotated video, metrics, supervised ML, sequence preparation, feedback), and
2. The uploaded `ai-swim-coach.zip` Lovable/TanStack Start UI (layout, workspace hero, color palette, sidebar, navigation, recording guidance, results, and seven pages).

The primary app uses a **Streamlit-native reproduction of the Lovable UI** so the real upload widget, model training, video playback, CSV/ZIP downloads, and feedback form work on Streamlit Community Cloud without Node, Bun, a React build server, or additional exposed ports. The original Lovable React/TypeScript source is preserved in `lovable_ui_source/` for future front-end development; the React code is **not** run directly by Streamlit.

## Features

- **Analyze:** Lovable-style sidebar, teal/navy hero, native drop-zone upload, recording checklist, configurable MediaPipe/OpenCV engine, genuine progress, a real metrics/coach dashboard, and complete analysis bundle download.
- **Annotated video:** Real annotated video playback and MP4 download. The app labels fallback OpenCV proxy landmarks clearly.
- **Time-series data:** Interactive metric selection, actual frame-derived plots, data table, and feature/raw-landmark CSV downloads.
- **Supervised ML:** Trainable Logistic Regression, Random Forest, Gradient Boosting, optional XGBoost/LightGBM, demo accuracy charts, and a model ZIP download.
- **Deep learning:** Original sequence-design concepts, Conv1D + BiLSTM architecture, real data-window preparation, and downloadable TensorFlow template for separate Colab training.
- **Feedback learning:** Submit helpfulness/rating/comment and view a reward-ranking demonstration. Download session feedback CSV.
- **About:** Authors, technical workflow, limitations, and model provenance.

**Important:** The original Lovable mock results (e.g., 31 spm, 92% symmetry, 1:42/100m pace, fictional model scores) were intentionally removed from the live interface; those numbers could misleadingly appear as measured data. The integration instead renders real, computable video features, and clearly states that generated demo ML labels and feedback ranking are prototypes, not trained elite-coach performance.

## Deploy on Streamlit Community Cloud

1. Download and **extract the new ZIP**.
2. Open your GitHub repository, e.g. `qxiao2ub/ai_swim_coach`, and upload **the contents of this extracted folder** to the repository root. Do **not** upload the ZIP without extracting it, and do **not** place `app.py` one folder below the root.
3. Commit the files on your deployed branch (typically `main`).
4. On [share.streamlit.io](https://share.streamlit.io/), create an app or manage your existing app with:

   - **Repository:** your GitHub repository
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **Python:** select **3.14** in Advanced settings if creating a deployment. The supplied backend was configured for the existing Python 3.14 runtime.

5. Deploy / reboot the app, and wait for `requirements.txt` to finish installing.
6. Open **Analysis settings → Deployment diagnostics** in the Streamlit sidebar if a dependency check is needed.

> **Runtime:** An existing Community Cloud app cannot necessarily change its configured Python version by editing `.python-version`. Select the desired version when first deploying. This repo targets the provided backend's Python 3.14 dependency set rather than the earlier 3.12-only blocker.

### Repository structure

```text
app.py                           # Streamlit entry point; live Lovable-style UI + backend
swim_ui.py                       # Lovable-derived colors, cards, responsive styling
ai_pipeline.py                   # Original pose tracking and analysis pipeline
requirements.txt                 # Cloud Python dependencies
packages.txt                     # Runtime shared libraries
.streamlit/config.toml           # Theme and upload limits
vendor/                          # Existing OpenCV headless metadata wheel
notebooks/                       # Existing Colab notebook
lovable_ui_source/               # Preserved original Lovable React + TanStack project
  src/routes/index.tsx           # Original homepage/UI design
  src/routes/annotated-video.tsx  # Original video page
  src/routes/time-series.tsx     # Original time series page
  src/routes/supervised-ml.tsx    # Original ML page
  src/routes/deep-learning.tsx    # Original DL page
  src/routes/feedback-learning.tsx
  src/routes/about.tsx
  src/styles.css                 # Original design tokens and CSS
  package.json                   # Original React project dependencies
docs/LOVABLE_UI_INTEGRATION.md   # Design mapping and migration notes
tests/                           # Source/deployment and pipeline smoke tests
```

### Local testing

Using a supported Python environment matching `requirements.txt`:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

For a lightweight video processing test in an environment with OpenCV, scikit-learn, pandas, and `imageio-ffmpeg`:

```bash
python -m pytest -q tests/test_pipeline_smoke.py tests/test_ui_integration.py
```

### Expected behavior and limitations

- MediaPipe supplies anatomical pose landmarks **if available**; OpenCV otherwise supplies **motion/silhouette proxy** landmarks, **not anatomical points**.
- The two upload formats `.mp5` and `.api` from the early concept are not standard supported video containers; use the provided supported list and preferentially an H.264 MP4 (5–20 seconds).
- ML demo accuracy uses KMeans-derived labels and does not validate technique against certified swimming-coach labels.
- The deep neural network is an **untrained template** in the default Streamlit deployment; train it offline or in Colab on verified labels.
- Feedback is **session-local** and stored temporarily in Community Cloud. Export it before server restart; persistent multi-user storage requires a database/service.
- Underwater refraction, occlusion, and camera angle can make joint estimates unreliable. The app is an educational/research prototype rather than medical or professional training advice.
- React-only interactions are reproduced with equivalent native Streamlit widgets for compatibility; exact pixel-perfect React rendering and TanStack routing are not provided by the Streamlit host.

**Source:** User-provided `AI-Swim-Repo-main.zip` backend and `ai-swim-coach.zip` Lovable UI. See `docs/LOVABLE_UI_INTEGRATION.md` for a detailed map.
