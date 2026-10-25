"""AI Swimming Coach - Streamlit + Lovable-inspired integrated user interface.

Original Lovable layout and copy are preserved as closely as possible using
native Streamlit controls, with full backend integration and no Node server.
Original TSX/CSS is retained in lovable_ui_source/ for further development.

Author: Jasper Ding
Advisor: Dr. Qingyang Xiao
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import altair as alt
import streamlit as st

from ai_pipeline import (
    DEFAULT_FEATURE_COLUMNS,
    add_kinematic_features,
    append_feedback,
    create_demo_training_labels,
    demo_contextual_bandit_update,
    extract_pose_timeseries,
    generate_recommendations,
    get_ffmpeg_executable,
    make_sequence_windows,
    save_outputs,
    summarize_video,
    trn_supervised_models,
)
from swim_ui import LOVABLE_CSS, card_html, clean, metric_html, page_intro

AUTHOR = 'Jasper Ding'
ADVISOR = 'Dr. Qingyang Xiao'
PAGES = [
    'Analyze', 'Annotated video', 'Time-series data',
    'Supervised ML', 'Deep learning', 'Feedback learning', 'About',
]
SUPPORTED_EXTENSIONS = ['mp4', 'mov', 'm4v', 'avi', 'mkv', 'wmv']
PROJECT_ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title='IM Coach | Jasper Ding',
    page_icon='🏊',
    layout='wide',
    initial_sidebar_state='expanded',
)
st.markdown(LOVABLE_CSS, unsafe_allow_html=True)


def html(text: str) -> None:
    st.markdown(text, unsafe_allow_html=True)


def init_state() -> None:
    defaults = {
        'section': PAGES[0],
        'analysis': None,
        'upload_fingerprint': None,
        'training': None,
        'feedback': None,
        'upload_revision': 0,
        'chart_view': 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def safe_filename(name: str) -> str:
    safe = Path(name).name
    return ''.join(c if c.isalnum() or c in '._-' else '_' for c in safe) or 'swim_video.mp4'


def fingerprint(contents: bytes, filename: str) -> str:
    digest = hashlib.sha256()
    digest.update(filename.encode('utf-8', errors='replace'))
    digest.update(contents[:2_000_000])
    digest.update(str(len(contents)).encode('ascii'))
    return digest.hexdigest()


def file_bytes(path: str | Path | None) -> bytes:
    if not path:
        return b''
    target = Path(path)
    return target.read_bytes() if target.exists() else b''


def clear_analysis() -> None:
    current = st.session_state.get('analysis')
    if current and current.get('work_dir'):
        shutil.rmtree(current['work_dir'], ignore_errors=True)
    st.session_state.analysis = None
    st.session_state.training = None
    st.session_state.feedback = None
    st.session_state.upload_fingerprint = None
    st.session_state.upload_revision += 1

# Navigation callbacks run before widgets are instantiated so they may set the 'section' key that the navigation segmented control owns.
def go_to_analyze() -> None:
    st.session_state.section = 'Analyze'


def start_new_analysis() -> None:
    clear_analysis()
    go_to_analyze()

def reset_chart_view() -> None:
    st.session_state.chart_view += 1


def fmt_number(value: Any, places: int = 1, suffix: str = '') -> str:
    try:
        v = float(value)
        if not pd.notna(v):
            return 'N/A'
        return f'{v:.{places}f}{suffix}'
    except (ValueError, TypeError):
        return 'N/A'


def render_sidebar() -> dict[str, Any]:
    with st.sidebar:
        html('''
        <div class="swim-brand">
          <div class="swim-logo">≋</div>
          <div><div class="swim-brand-title">AI Swimming Coach</div>
          <div class="swim-brand-subtitle">Motion intelligence lab</div></div>
        </div>
        <div class="swim-section-kicker" style="color:#7e949a">Project team</div>
        <div class="swim-side-caption" style="margin:8px 0 14px;">
          <strong>Author</strong> · Jasper Ding<br>
          <strong>Advisor</strong> · Dr. Qingyang Xiao
        </div>
        ''')
        st.divider()
        st.markdown('**Analysis settings**')
        engine_display = st.selectbox(
            'Analysis engine',
            options=[
                'Automatic · MediaPipe, then OpenCV',
                'Precision pose model · MediaPipe only',
                'OpenCV fallback · motion proxies',
            ],
            help='Automatic first attempts MediaPipe anatomical landmarks. OpenCV is a clearly labeled motion-proxy fallback.',
        )
        backend = {
            'Automatic · MediaPipe, then OpenCV': 'auto',
            'Precision pose model · MediaPipe only': 'mediapipe',
            'OpenCV fallback · motion proxies': 'opencv_motion',
        }[engine_display]
        max_frames = st.slider('Maximum processed frames', 150, 900, 450, 50)
        stride = st.slider('Frame stride', 1, 6, 2)
        width = st.select_slider('Analysis width', options=[480, 600, 720, 840, 960, 1080], value=720)
        detect = st.slider('Pose detection confidence', 0.30, 0.90, 0.50, 0.05)
        track = st.slider('Pose tracking confidence', 0.30, 0.90, 0.50, 0.05)
        st.divider()
        html('''<div class="swim-side-caption">ⓘ &nbsp; For best results, use a stable 5–20 second side-view clip with the full swimmer visible.</div>''')
        with st.expander('Deployment diagnostics'):
            diagnostics = {'Python': sys.version.split()[0]}
            for name in ['streamlit', 'mediapipe', 'opencv-contrib-python-headless']:
                try:
                    diagnostics[name] = importlib.metadata.version(name)
                except importlib.metadata.PackageNotFoundError:
                    diagnostics[name] = 'Not installed'
            diagnostics['XGBoost optional'] = importlib.util.find_spec('xgboost') is not None
            diagnostics['LightGBM optional'] = importlib.util.find_spec('lightgbm') is not None
            st.json(diagnostics)
            if st.button('Check video engine dependencies', use_container_width=True):
                try:
                    import cv2
                    st.success(f'OpenCV is ready: {cv2.__version__}')
                    st.write('FFmpeg:', get_ffmpeg_executable() or 'unavailable')
                except Exception as exc:
                    st.error(f'OpenCV failed: {exc}')
                try:
                    from mediapipe.tasks.python.vision import pose_landmarker as pl
                    st.write('MediaPipe Tasks:', 'Ready' if hasattr(pl, 'PoseLandmarker') else 'Unavailable')
                except Exception as exc:
                    st.warning(f'MediaPipe unavailable; try the OpenCV fallback. Details: {exc}')
        if st.session_state.analysis is not None:
            st.button('Start a new video analysis', use_container_width=True, on_click=start_new_analysis)
    return {
        'backend': backend,
        'max_frames': max_frames,
        'stride': stride,
        'resize_width': width,
        'min_detection_confidence': detect,
        'min_tracking_confidence': track,
    }


def render_header() -> None:
    status = ('SESSION ANALYZED' if st.session_state.analysis else 'RESEARCH PROTOTYPE')
    html(f'''<div class="swim-topbar"><div>
      <h2>Performance workspace</h2><p>Video pose &amp; technique analysis</p>
    </div><div class="swim-top-status">● {status}</div></div>''')
    st.segmented_control('Navigation', options=PAGES, key='section', label_visibility='collapsed')


def recording_checklist() -> None:
    html('''
    <div class="swim-guide-heading">Recording checklist</div>
    <div class="swim-guide-item"><span class="swim-check">✓</span>Keep the entire swimmer in frame</div>
    <div class="swim-guide-item"><span class="swim-check">✓</span>Prefer a stable side view</div>
    <div class="swim-guide-item"><span class="swim-check">✓</span>Reduce glare, splashes, and obstructions</div>
    <div class="swim-guide-item"><span class="swim-check">✓</span>Avoid uploading sensitive footage</div>
    <div class="swim-tip"><strong>Capture tip</strong><br>
       Place the camera near hip height and keep it still through at least three full stroke cycles.</div>
    ''')


def analyze_video(uploaded: Any, settings: dict[str, Any]) -> None:
    uploaded_bytes = uploaded.getvalue()
    work_dir = Path(tempfile.mkdtemp(prefix='ai_swim_coach_'))
    input_path = work_dir / safe_filename(uploaded.name)
    output_dir = work_dir / 'outputs'
    input_path.write_bytes(uploaded_bytes)
    progress = st.progress(0, text='Analyzing Video')
    progress_message = st.empty()
    progress_message.caption('Preparing your swimming video')

    def update_progress(amount: float, message: str) -> None:
        progress.progress(min(100, max(0, round(100 * amount))), text='Analyzing Video')
        progress_message.caption(message)

    try:
        raw_df, annotated_path, metadata = extract_pose_timeseries(
            input_path,
            output_dir=output_dir,
            max_frames=settings['max_frames'],
            stride=settings['stride'],
            resize_width=settings['resize_width'],
            min_detection_confidence=settings['min_detection_confidence'],
            min_tracking_confidence=settings['min_tracking_confidence'],
            backend=settings['backend'],
            create_annotated_video=True,
            progress_callback=update_progress,
        )
        features = add_kinematic_features(raw_df)
        metrics = summarize_video(features, metadata)
        recs = generate_recommendations(metrics)
        saved = save_outputs(
            output_dir, uploaded.name, raw_df, features, metrics, recs,
            annotated_video_path=annotated_path,
        )
        update_progress(1.0, 'Analysis complete')
        st.session_state.analysis = {
            'work_dir': str(work_dir),
            'video_name': uploaded.name,
            'upload_path': str(input_path),
            'annotated_path': str(annotated_path) if annotated_path else None,
            'raw_df': raw_df,
            'feature_df': features,
            'metrics': metrics,
            'recommendations': recs,
            'saved_paths': saved,
        }
        st.session_state.upload_fingerprint = fingerprint(uploaded_bytes, uploaded.name)
        st.session_state.training = None
        st.session_state.feedback = None
        st.rerun()
    except Exception as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        progress.empty()
        progress_message.empty()
        st.error(f'The swimming-video analysis failed: {exc}')
        with st.expander('Technical details'):
            st.exception(exc)
        st.info('Try Automatic analysis or the OpenCV motion fallback with a shorter H.264 MP4 clip.')


def render_upload(settings: dict[str, Any]) -> None:
    left, right = st.columns([1.65, .75], gap='large')
    with left:
        html('<div class="swim-upload-label">Step 01</div><div class="swim-section-title">Upload a swimming video</div>')
        st.caption('MP4, MOV, AVI, M4V, MKV, WMV · 300 MB server limit')
        uploader = st.file_uploader(
            'Drop your swim clip here or click Browse files',
            type=SUPPORTED_EXTENSIONS,
            key=f"swim_video_upload_{st.session_state.upload_revision}",
            help='Input formats depend on available codecs. H.264 MP4 is recommended.',
        )
        if uploader is not None:
            uploaded_bytes = uploader.getvalue()
            html(f'<div class="swim-card"><h3>Video ready for analysis</h3><p>🎞 &nbsp; {clean(uploader.name)} · {len(uploaded_bytes)/1024/1024:.1f} MB</p></div>')
            try:
                st.video(uploader)
            except Exception:
                st.caption('Preview unavailable in this browser; the video may still be processed.')
            if st.button('▶ Analyze video', type='primary', use_container_width=True, disabled=len(uploaded_bytes) == 0):
                analyze_video(uploader, settings)
        else:
            html('''<div class="swim-small-muted" style="margin:6px 0 0;">Choose your clip using the drag-and-drop uploader above to start the real computer-vision pipeline.</div>''')
    with right:
        recording_checklist()

    html('<hr class="swim-rule">')
    intro, detail = st.columns([.65, 1.35], gap='large')
    with intro:
        html('''<div class="swim-upload-label">Analysis output</div>
        <div class="swim-section-title" style="font-size:24px;margin-top:7px">From footage to focused feedback.</div>''')
    with detail:
        html('''<div class="swim-feature-grid">
        <div class="swim-feature"><span class="swim-feature-num">01</span><div><h3>Annotated movement</h3><p>Pose landmarks reveal alignment and stroke timing frame by frame.</p></div></div>
        <div class="swim-feature"><span class="swim-feature-num">02</span><div><h3>Time-series data</h3><p>Joint angles, movement speed, symmetry, and body-line features.</p></div></div>
        <div class="swim-feature"><span class="swim-feature-num">03</span><div><h3>Coaching insights</h3><p>Clear observations and training cues grounded in detected motion.</p></div></div>
        <div class="swim-feature"><span class="swim-feature-num">04</span><div><h3>Trainable baseline</h3><p>Structured outputs ready for supervised-learning and feedback experiments.</p></div></div>
        </div>''')


def analysis_warning(analysis: dict[str, Any]) -> None:
    backend = str(analysis['metrics'].get('analysis_backend', ''))
    if backend == 'opencv_motion_fallback':
        st.warning('OpenCV motion fallback used: annotated motion and landmarks are **proxies**, not anatomical pose estimates. Joint angles and coaching guidance are approximate and require human review.')
    else:
        st.caption('Analysis engine: ' + str(analysis['metrics'].get('analysis_backend_label') or backend or 'MediaPipe'))


def render_recommendation(rec: dict[str, Any], number: int) -> None:
    priority = str(rec.get('priority', 'low')).lower()
    if priority not in {'low', 'medium', 'high'}:
        priority = 'low'
    confidence = fmt_number(float(rec.get('confidence') or 0) * 100, 0, '%')
    html(f'''<div class="swim-rec" data-priority="{priority}">
    <div class="heading">{number:02}. {clean(rec.get('title', 'Coaching observation'))}</div>
    <div class="meta">{clean(priority.upper())} PRIORITY · Heuristic confidence {confidence}</div>
    <p><strong>Evidence</strong> · {clean(rec.get('evidence', ''))}</p>
    <p><strong>Suggestion</strong> · {clean(rec.get('suggestion', ''))}</p>
    <p><strong>Training drill</strong> · {clean(rec.get('drill', ''))}</p>
    </div>''')


def render_session_summary(analysis: dict[str, Any]) -> None:
    metrics = analysis['metrics']
    recs = analysis['recommendations']
    html(f'''<div class="swim-section-kicker" style="color:#218967">✓ Analysis complete</div>
    <div class="swim-section-title" style="font-size:26px">Session performance</div>
    <div class="swim-section-intro">{clean(analysis['video_name'])}</div>''')
    if st.button('↺ New analysis', use_container_width=False):
        clear_analysis()
        st.rerun()
    analysis_warning(analysis)
    cards = st.columns(4)
    values = [
        ('Processed frames', str(metrics.get('processed_frames', 0)), 'Frames analyzed'),
        ('Motion detection', fmt_number(100 * float(metrics.get('pose_detection_rate') or 0), 0, '%'), 'Fraction of frames detected'),
        ('Analyzed duration', fmt_number(metrics.get('analyzed_duration_sec'), 1, ' s'), 'Sampled footage duration'),
        ('Head alignment', fmt_number(metrics.get('mean_head_alignment_score'), 0, '/100'), 'Camera-plane heuristic score (100 = nose level with shoulders, drops as the head lifts or sinks)'),
    ]
    for col, (title, value, desc) in zip(cards, values):
        with col:
            html(metric_html(title, value, desc))
    chart_col, coach_col = st.columns([1.12, .88], gap='large')
    with chart_col:
        with st.container(border=True):
            title_col, reset_col = st.columns([4, 1], vertical_alignment='center')
            title_col.markdown('**Movement consistency**')
            reset_col.button('Reset view', key='reset_chart_view', on_click=reset_chart_view, width='stretch')
            features = analysis['feature_df']
            candidates = ['head_alignment_score', 'body_line_deviation', 'elbow_angle_symmetry_gap']
            available = next((k for k in candidates if k in features and features[k].notna().any()), None)
            if available:
                seq = pd.to_numeric(features[available], errors='coerce')
                block_count = min(8, len(seq))
                # These are time blocks, NOT stroke cycles. Avoid claiming cycle detection.
                block_id = pd.Series([min(block_count - 1, index * block_count // len(seq)) for index in range(len(seq))])
                points = pd.DataFrame({'block': block_id, 'value': seq.reset_index(drop=True)}).groupby('block')['value'].mean()
                label = available.replace('_', ' ').title()
                chart_data = pd.DataFrame({'Time block': points.index + 1, label: points.values})
                chart = alt.Chart(chart_data).mark_bar(size=28, color='#0B7285').encode(x=alt.X('Time block:Q', scale=alt.Scale(domain=[0.5, block_count + 0.5]), axis=alt.Axis(labelAngle=0, tickMinStep=1, format='d')), y=alt.Y(f'{label}:Q'), tooltip=['Time block', alt.Tooltip(f'{label}:Q', format='.1f')],).properties(height=260).interactive()
                st.altair_chart(chart, width='stretch', key=f'consistency_chart_{st.session_state.chart_view}')
                st.caption('Eight chronological time blocks; bars are not detected stroke cycles.')
            else:
                st.info('No usable feature time series was measured from this clip.')
    with coach_col:
        lead = recs[0] if recs else None
        if lead:
            html(f'''<div class="swim-coach"><div class="kicker">✦ Main Focus</div>
            <h3>{clean(lead['title'])}</h3><p>{clean(lead['suggestion'])}</p>
            <div class="drill">→ {clean(lead.get('drill', ''))}</div></div>''')
    st.markdown('**Coaching insights and training suggestions**')
    for index, rec in enumerate(recs, start=1):
        render_recommendation(rec, index)
    saved_zip = analysis['saved_paths'].get('analysis_bundle_zip')
    if saved_zip and Path(saved_zip).exists():
        st.download_button(
            '⬇ Download complete analysis bundle',
            data=file_bytes(saved_zip), file_name=Path(saved_zip).name,
            mime='application/zip', type='primary', use_container_width=True,
        )
    with st.expander('View the annotated video here'):
        if analysis.get('annotated_path') and Path(analysis['annotated_path']).exists():
            st.video(analysis['annotated_path'])
        else:
            st.caption('No annotated video was produced.')


def route_to_analyze(message: str) -> None:
    html(f'<div class="swim-empty"><strong>No analyzed video yet</strong>{clean(message)}</div>')
    st.button('Go to Analyze →', type='primary', on_click=go_to_analyze)


def page_analyze(settings: dict[str, Any], analysis: dict[str, Any] | None) -> None:
    html('''<div class="swim-hero">
       <div class="eyebrow">✦ &nbsp; Computer vision coaching</div>
       <h1>See what your stroke is saying.</h1>
       <p>Turn a short poolside video into clear technique signals, movement metrics, and focused coaching cues.</p>
    </div>
    <div class="swim-notice"><span style="font-size:17px">ⓘ</span>
      <div><strong>Prototype analysis.</strong> Pose-derived scores support coaching review and are not a substitute for an in-person qualified coach. Results are not validated clinical or professional performance assessments.</div>
    </div>''')
    if analysis is None:
        render_upload(settings)
    else:
        render_session_summary(analysis)


def page_video(analysis: dict[str, Any] | None) -> None:
    html(page_intro('Output 01', 'Annotated video', 'Watch the swimming footage with pose landmarks and movement overlays applied frame by frame.'))
    if not analysis:
        route_to_analyze('Upload a video to generate a real annotated MP4 rather than a placeholder animation.')
    else:
        analysis_warning(analysis)
        path = analysis.get('annotated_path')
        if path and Path(path).exists():
            st.video(path)
            st.download_button('⬇ Download annotated MP4', file_bytes(path),
                               file_name=Path(path).name, mime='video/mp4', use_container_width=True)
        else:
            st.warning('No annotated video was created. See the output CSV and model diagnostics.')
    one, two, three = st.columns(3)
    with one: html(card_html('Landmarks', 'Up to 33 body landmarks per frame when MediaPipe succeeds; a labeled motion proxy is used otherwise.'))
    with two: html(card_html('Motion analysis', 'Review swimmer alignment and movement timing. Stroke phase classification requires validated labeled training data.'))
    with three: html(card_html('Downloads', 'Export the annotated MP4 and CSV datasets after processing your clip.'))
    st.caption('Heavy splash, underwater refraction, and occlusion reduce pose reliability. Review detection metrics before interpreting joint angles.')


def page_timeseries(analysis: dict[str, Any] | None) -> None:
    html(page_intro('Output 02', 'Time-series data', 'Every processed frame contributes movement features you can chart, compare, and export to train future models.'))
    if not analysis:
        route_to_analyze('Analyze footage to populate real angle, speed, symmetry, and body-line measurements.')
        return
    analysis_warning(analysis)
    features = analysis['feature_df']
    candidates = [
        'left_elbow_angle', 'right_elbow_angle', 'body_line_deviation', 'head_alignment_score',
        'kick_amplitude', 'wrist_symmetry_gap', 'ankle_symmetry_gap',
        'left_wrist_speed', 'right_wrist_speed',
    ]
    selected = st.multiselect(
        'Choose metrics to plot', [name for name in candidates if name in features],
        default=[name for name in ['left_elbow_angle', 'right_elbow_angle', 'head_alignment_score'] if name in features],
    )
    if selected and 'timestamp_sec' in features:
        data = features[['timestamp_sec', *selected]].copy().set_index('timestamp_sec')
        st.line_chart(data, height=360, x_label='Video timestamp (seconds)')
    else:
        st.info('Select at least one available metric to display a time-series chart.')
    preview_columns = [name for name in ['frame_index', 'timestamp_sec', 'pose_detected', *DEFAULT_FEATURE_COLUMNS] if name in features]
    with st.expander('Frame-by-frame feature table', expanded=True):
        st.dataframe(features[preview_columns].head(500), use_container_width=True, height=320)
    saved = analysis['saved_paths']
    c1, c2 = st.columns(2)
    for col, key, label in [
        (c1, 'timeseries_features_csv', '⬇ Download feature CSV'),
        (c2, 'raw_landmarks_csv', '⬇ Download raw landmarks CSV'),
    ]:
        with col:
            path = saved.get(key)
            if path and Path(path).exists():
                st.download_button(label, file_bytes(path), file_name=Path(path).name,
                                   mime='text/csv', use_container_width=True)
    one, two, three = st.columns(3)
    with one: html(card_html('Joint angles', 'Elbow, knee, and body alignment angles in the camera plane.'))
    with two: html(card_html('Body line', 'Head alignment and movement symmetry time series.'))
    with three: html(card_html('CSV export', 'Machine-readable data suitable for spreadsheets and future supervised model datasets.'))


def page_supervised_ml(analysis: dict[str, Any] | None) -> None:
    html(page_intro('Model lab', 'Supervised ML', 'Compare supervised baselines trained on structured stroke features. Expert-labeled technique outcomes are required for meaningful coaching accuracy.'))
    st.warning('Current demo labels are generated by KMeans clustering, NOT swimming-coach ground truth. Demo validation accuracy tests the software pipeline only.')
    if not analysis:
        route_to_analyze('Analyze a sufficiently long video before creating demonstration labels.')
        return
    c1, c2 = st.columns(2)
    with c1:
        n_clusters = st.slider('Number of demo motion patterns', 2, 5, 3)
    with c2:
        boosters_available = all(importlib.util.find_spec(name) is not None for name in ['xgboost', 'lightgbm'])
        include_boosters = st.checkbox('Train optional XGBoost and LightGBM', value=False,
                                       disabled=not boosters_available)
        if not boosters_available:
            st.caption('Default: Logistic Regression, Random Forest, Gradient Boosting. Boosters are optional.')
    if st.button('Train supervised models', type='primary', use_container_width=True):
        try:
            with st.spinner('Creating demo labels and training classification baselines...'):
                training_df = create_demo_training_labels(analysis['feature_df'], n_labels=n_clusters)
                trained = train_supervised_models(
                    training_df, output_dir=Path(analysis['work_dir']) / 'models',
                    include_optional_boosters=include_boosters,
                )
                st.session_state.training = {'training_df': training_df, 'results': trained}
            st.success('Model training complete. The scores are demo-label classification results.')
        except Exception as exc:
            st.error(f'Model training was not possible for this clip: {exc}')
            st.info('Use more usable video frames or gather a multi-clip, coach-labeled dataset.')
    state = st.session_state.training
    if state:
        results = state['results']
        rows = [{'Model': name.replace('_', ' ').title(), 'Demo accuracy': r['accuracy']}
                for name, r in results['models'].items()]
        if rows:
            scores = pd.DataFrame(rows).sort_values('Demo accuracy', ascending=False)
            st.markdown('**Demo validation accuracy — not coaching accuracy**')
            st.bar_chart(scores.set_index('Model'), height=270)
            st.dataframe(scores, hide_index=True, use_container_width=True)
        if results.get('skipped_models'):
            with st.expander('Skipped-model details'):
                st.json(results['skipped_models'])
        if results.get('models'):
            best_name = max(results['models'], key=lambda n: results['models'][n]['accuracy'])
            importances = results['models'][best_name].get('feature_importance')
            if importances:
                st.markdown(f'**Top input features — {best_name.replace("_", " ").title()}**')
                st.bar_chart(pd.DataFrame(importances).set_index('feature')['importance'], horizontal=True, height=300)
        bundle_path = results.get('model_bundle_path')
        if bundle_path and Path(bundle_path).exists():
            st.download_button('⬇ Download trained model bundle', file_bytes(bundle_path),
                               file_name=Path(bundle_path).name, mime='application/zip',
                               use_container_width=True)
    one, two, three = st.columns(3)
    with one: html(card_html('Features', 'Measured joint-angle ranges, motion speeds, and alignment and symmetry statistics.'))
    with two: html(card_html('Training labels', 'Current categories are unsupervised demo patterns; replace them with reviewed technique labels.'))
    with three: html(card_html('Model lab', 'Real trainable baselines: Logistic Regression, Random Forest, Gradient Boosting, and optional boosters.'))


def page_deep_learning(analysis: dict[str, Any] | None) -> None:
    html(page_intro('Model lab', 'Deep learning', 'Temporal sequence models can learn stroke patterns from time-series features after suitable labeled datasets are collected.'))
    one, two, three = st.columns(3)
    with one: html(card_html('Conv1D', 'Extracts local motion motifs across consecutive video frames. Architecture provided; not pre-trained.'))
    with two: html(card_html('Bidirectional LSTM', 'Captures longer temporal dependencies between phases in each movement sequence.'))
    with three: html(card_html('Colab training', 'The optional TensorFlow model can be trained offline. The free Community Cloud build does not install TensorFlow.'))
    html('<div class="swim-tip">Pipeline: pose sequence → normalization → Conv1D → bidirectional LSTM → dense classifier → validated technique labels.</div>')
    arch = [
        ['Input', 'window_size × features', 'Time-series feature sequence'],
        ['Conv1D', '64 filters, kernel 5', 'Local motion pattern representation'],
        ['Batch normalization', '64 channels', 'Stabilize optimization'],
        ['Max pooling', 'pool size 2', 'Downsample time'],
        ['BiLSTM', '64 units', 'Two-way temporal context'],
        ['Dropout', '0.25', 'Reduce overfitting'],
        ['BiLSTM', '32 units', 'Sequence summary'],
        ['Dense', '64 units, ReLU', 'High-level representation'],
        ['Softmax', 'Classes to be defined', 'Predictions if trained'],
    ]
    with st.expander('Inspect the neural network architecture'):
        st.dataframe(pd.DataFrame(arch, columns=['Layer', 'Configuration', 'Role']),
                     use_container_width=True, hide_index=True)
    if analysis:
        a, b = st.columns(2)
        with a: window_size = st.slider('Frames per sequence window', 15, 120, 45, 5)
        with b: step = st.slider('Sequence window step', 5, 60, 15, 5)
        training = st.session_state.training
        source = training['training_df'] if training else None
        if source is None:
            try:
                source = create_demo_training_labels(analysis['feature_df'], n_labels=3)
            except Exception:
                source = None
        if source is not None:
            try:
                xs, ys, cols = make_sequence_windows(
                    source, label_col='demo_label', window_size=window_size, step=step,
                )
                c1, c2, c3 = st.columns(3)
                c1.metric('Sequence windows', len(xs))
                c2.metric('Frames / window', window_size)
                c3.metric('Features / frame', len(cols))
                st.caption('Windows are constructed, not used for a trained deep-network prediction in the Streamlit build.')
            except Exception as exc:
                st.info(f'Sequence construction requires more usable data: {exc}')
        else:
            st.info('Analyze a longer clip to prepare demonstration sequence windows.')
    else:
        st.info('Analyze footage to create sequence-window inputs for the notebook.')
    template = PROJECT_ROOT / 'deep_learning_template.py'
    if template.exists():
        st.download_button('⬇ Download Conv1D + BiLSTM training template', template.read_bytes(),
                           file_name=template.name, mime='text/x-python', use_container_width=True)


def page_feedback(analysis: dict[str, Any] | None) -> None:
    html(page_intro('Model lab', 'Feedback learning', 'Swimmers and coaches can rate suggestions. Ratings update an exploratory reward ranking for this session.'))
    if not analysis:
        route_to_analyze('Run a video analysis to obtain specific recommendations you can rate.')
        return
    recs = analysis['recommendations']
    for i, rec in enumerate(recs, start=1):
        render_recommendation(rec, i)
    options = {str(r['action_id']): str(r['title']) for r in recs}
    with st.form('swim_feedback_form', clear_on_submit=True):
        chosen = st.selectbox('Coaching insight', list(options), format_func=lambda key: options[key])
        rating = st.slider('Recommendation rating', min_value=1, max_value=5, value=4)
        helpful = st.checkbox('This recommendation was helpful', value=True)
        comment = st.text_area('Your comments for the coach/research team', max_chars=1000)
        submitted = st.form_submit_button('Submit rating and update ranking', type='primary', use_container_width=True)
    if submitted:
        try:
            path = Path(analysis['work_dir']) / 'data' / 'feedback_log.csv'
            feedback_df = append_feedback(
                path, video_name=analysis['video_name'], action_id=chosen, rating=rating,
                helpful=helpful, comment=comment, metrics=analysis['metrics'],
            )
            bandit = demo_contextual_bandit_update(feedback_df)
            st.session_state.feedback = {'dataframe': feedback_df, 'state': bandit, 'path': str(path)}
            st.success('Feedback saved for the current session; reward ranking updated.')
        except Exception as exc:
            st.error(f'Feedback could not be saved: {exc}')
    feedback = st.session_state.feedback
    if feedback:
        ranked = feedback['state'].get('ranked_actions', [])
        count = len(feedback['dataframe'])
        html(metric_html('Feedback ratings this session', str(count), 'Stored temporarily on the Community Cloud instance.'))
        if ranked:
            table = pd.DataFrame(ranked)
            cols = [name for name in ['title', 'feedback_count', 'estimated_reward', 'priority'] if name in table]
            st.markdown('**Updated action ranking**')
            st.dataframe(table[cols], hide_index=True, use_container_width=True)
        st.download_button('⬇ Export feedback CSV', file_bytes(feedback['path']),
                           file_name='feedback_log.csv', mime='text/csv', use_container_width=True)
    st.caption('Prototype learning: feedback reorders estimated priorities; it does not automatically retrain the pose model or neural network. Community Cloud storage is ephemeral.')


def page_about(analysis: dict[str, Any] | None) -> None:
    html(page_intro('Project', 'About', 'AI Swimming Coach explores how computer vision and machine learning can offer accessible swimming technique feedback from a short video.'))
    left, right = st.columns(2)
    with left: html(card_html('Project team', 'Author: Jasper Ding · Advisor: Dr. Qingyang Xiao'))
    with right: html(card_html('Research prototype disclaimer', 'Insights support, but do not replace, a qualified in-person coach. Measurements are preliminary and camera-dependent.'))
    st.markdown('### How the system works')
    one, two, three = st.columns(3)
    with one: html(card_html('01 · Video & vision', 'Upload MP4/MOV/AVI, detect pose landmarks when possible, and generate an annotated playback.'))
    with two: html(card_html('02 · Time-series & ML', 'Extract movement features, generate rule-based observations, and explore trainable supervised models.'))
    with three: html(card_html('03 · Deep & feedback learning', 'Build sequence inputs for optional Colab neural-network experiments, then rate recommendations.'))
    st.markdown('### Important limitations')
    st.markdown(
        '- MediaPipe poses can be inaccurate under water, glare, and limb occlusion.\n'
        '- OpenCV fallback landmarks describe silhouette/motion proxies, not anatomical joints.\n'
        '- Camera-plane measurements are not full 3-D biomechanical measurements.\n'
        '- Demo classification labels are KMeans-derived, not coach-verified ground truth.\n'
        '- Feedback ranking is a contextual-bandit illustration, not autonomous model retraining.\n'
        '- Training deep networks and verifying coaching accuracy require a curated, consented dataset.'
    )
    if analysis:
        with st.expander('Inspect this session’s summary JSON'):
            st.code(json.dumps(analysis['metrics'], indent=2, default=str), language='json')
    st.caption(f'Author: {AUTHOR}  |  Advisor: {ADVISOR}  |  Original Lovable UI source included in the GitHub repository.')


def run() -> None:
    init_state()
    settings = render_sidebar()
    render_header()
    section = st.session_state.section or 'Analyze'
    analysis = st.session_state.analysis
    if section == 'Analyze':
        page_analyze(settings, analysis)
    elif section == 'Annotated video':
        page_video(analysis)
    elif section == 'Time-series data':
        page_timeseries(analysis)
    elif section == 'Supervised ML':
        page_supervised_ml(analysis)
    elif section == 'Deep learning':
        page_deep_learning(analysis)
    elif section == 'Feedback learning':
        page_feedback(analysis)
    elif section == 'About':
        page_about(analysis)
    else:
        st.error('Unrecognized page.')
    st.markdown('---')
    st.caption(f'AI Swimming Coach · Author: {AUTHOR} · Advisor: {ADVISOR} · Educational research prototype')


if __name__ == '__main__':
    run()
