# Deployment notes

The user-provided `AI-Swim-Repo-main.zip` is the Python 3.14-compatible starting backend. The supplied Lovable `ai-swim-coach.zip` is a separate TanStack Start/React project. Streamlit Community Cloud does not run a TanStack Start application as its `app.py` module.

The integrated repository provides an actual Python Streamlit UI port in `app.py` and `swim_ui.py` while retaining the Lovable React files in `lovable_ui_source/` (not loaded by Streamlit). There is no Node/npm install step in the Cloud app. `packages.txt` uses the same shared-library set from the provided Python 3.14 backend. Python video/ML libraries are defined by `requirements.txt`.

The earlier Python 3.12-only guard is absent. Deployment's Python version is governed by the Community Cloud deployment configuration; this package retains Python 3.14 dependencies because the supplied backend was configured for that runtime.

For first deployment and troubleshooting steps, see `DEPLOYMENT_CHECKLIST.md`. For the exact UI mapping, see `docs/LOVABLE_UI_INTEGRATION.md`.
