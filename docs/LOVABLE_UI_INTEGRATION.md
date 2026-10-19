# Lovable UI integration map

The original user-supplied UI was a **TanStack Start / React / Tailwind** project and Streamlit Community Cloud serves **Python**, not the Node runtime assumed by TanStack. A native Streamlit port keeps interactive upload and AI analysis integrated with the backend and avoids the additional build server. All original UI source files are preserved under `lovable_ui_source/`.

| Lovable component or behavior | Streamlit implementation | Functional integration |
| --- | --- | --- |
| Main navy hero / slogan | `app.py:page_analyze` + `.swim-hero` in `swim_ui.py` | Same copy and visual hierarchy |
| Analysis settings sidebar | `app.py:render_sidebar` | Real max frame, stride, width, confidence, backend configuration |
| Project team | `render_sidebar`, `page_about`, footer | Jasper Ding / Dr. Qingyang Xiao |
| Seven-route page header | `st.segmented_control` in `render_header` | Seven real page views; no server routes |
| Upload drop zone and preview | `st.file_uploader`, `st.video` | Real Streamlit file upload, progress, pose extraction |
| Recording checklist / capture tip | `recording_checklist` | Original tips and card styling |
| Analysis results metric tiles | `render_session_summary` | Real detected frames, detection rate, duration, head alignment |
| Stroke consistency example bars | `render_session_summary` | Real chronological metric bins; not falsely labeled cycles |
| Coach's focus dark card | `render_session_summary` | Real highest-priority generated recommendation |
| Annotated video page | `page_video` | Processed MP4 video and download |
| Time-series page | `page_timeseries` | Selectable feature chart, data table, CSV downloads |
| Supervised ML page | `page_supervised_ml` | Train actual baselines; display measured demo-label accuracy |
| Deep learning page | `page_deep_learning` | Conv1D / BiLSTM design and real sequence windows |
| Feedback learning page | `page_feedback` | Real rating forms, persisted within the server session, ranking, download |
| About page | `page_about` | Team, architecture and responsible limitations |
| Tailwind colors, card tokens | `swim_ui.py:LOVABLE_CSS` | Translated to vanilla CSS targeting Streamlit widgets |
| React/TanStack source | `lovable_ui_source/` | Kept intact for optional separate React deployment |

## Intentional changes from the Lovable design

- Original Lovable index `Results` uses hard-coded `31 spm`, `92%`, `1:42/100m`, and generic coach feedback. Those **were design mock data**, not measurements. Replaced with measured metrics and current video recommendations.
- Original `Analyze video` increments a timer to 100% without running a backend. Replaced with `extract_pose_timeseries` with actual processing progress and error handling.
- Original `Supervised ML` displays assumed sample accuracies. Replaced with real training scores on **demo** clusters; proper coach-labeled evaluation is still outstanding.
- Original `Deep learning` gives fictional F1 scores. The port instead exposes the architecture and sequence preparation without claiming pretrained neural model accuracy.
- Original `Feedback` votes are browser-only. The port writes a session CSV and computes feedback-based action ranking. Cloud storage is not permanent.
- Native Streamlit navigation replaces TanStack routing and native Streamlit upload replaces the JavaScript file uploader. The original TSX is retained but **not embedded as an interactive React app**: this is a faithful Streamlit adaptation, not a React runtime.

## Future extension

If exact pixel-level React fidelity becomes a requirement, reuse `lovable_ui_source/` for a separately built React app and implement a secure upload/API backend, or build a Streamlit custom component with a bidirectional bridge. Streamlit Community Cloud alone does not host the uploaded TanStack Start server as-is.
