"""Simulated Streamlit widget exercise when Streamlit is unavailable locally.

This is a functional code-path smoke test, not a live browser rendering check.
"""
from __future__ import annotations

import importlib.util
import sys
from contextlib import AbstractContextManager
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]

class Session(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name, value):
        self[name] = value

class FakeUI(ModuleType, AbstractContextManager):
    def __init__(self):
        super().__init__('streamlit')
        self.sidebar = self
        self.session_state = Session()
        self.renders = 0

    def __enter__(self): return self
    def __exit__(self, *args): return False
    def set_page_config(self, **kwargs): pass
    def markdown(self, *args, **kwargs): self.renders += 1
    def caption(self, *args, **kwargs): pass
    def divider(self, *args, **kwargs): pass
    def json(self, *args, **kwargs): pass
    def write(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def code(self, *args, **kwargs): pass
    def success(self, *args, **kwargs): pass
    def subheader(self, *args, **kwargs): pass
    def dataframe(self, *args, **kwargs): pass
    def bar_chart(self, *args, **kwargs): pass
    def line_chart(self, *args, **kwargs): pass
    def video(self, *args, **kwargs): pass
    def metric(self, *args, **kwargs): pass
    def download_button(self, *args, **kwargs): return False
    def button(self, *args, **kwargs): return False
    def form_submit_button(self, *args, **kwargs): return False
    def checkbox(self, *args, **kwargs): return kwargs.get('value', False)
    def expander(self, *args, **kwargs): return self
    def form(self, *args, **kwargs): return self
    def columns(self, widths, **kwargs):
        return [self] * (widths if isinstance(widths, int) else len(widths))
    def selectbox(self, label, options, **kwargs):
        return list(options)[0]
    def select_slider(self, label, options, **kwargs):
        return kwargs.get('value', list(options)[0])
    def slider(self, label, *args, **kwargs):
        return kwargs.get('value', args[2] if len(args) >= 3 else args[0] if args else 1)
    def segmented_control(self, label, options, **kwargs):
        key = kwargs.get('key')
        return self.session_state.get(key, list(options)[0])
    def file_uploader(self, *args, **kwargs): return None
    def multiselect(self, label, options, **kwargs):
        return kwargs.get('default', [])
    def text_area(self, *args, **kwargs): return ''


def test_all_streamlit_pages_render_without_uploaded_video() -> None:
    fake = FakeUI()
    previous = sys.modules.get('streamlit')
    sys.modules['streamlit'] = fake
    sys.path.insert(0, str(ROOT))
    try:
        spec = importlib.util.spec_from_file_location('_swim_integration_ui_test', ROOT / 'app.py')
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        for page in module.PAGES:
            fake.session_state.section = page
            module.run()
        assert fake.renders > 35
    finally:
        if previous is None:
            sys.modules.pop('streamlit', None)
        else:
            sys.modules['streamlit'] = previous


def test_all_sections_with_real_synthetic_metrics(tmp_path) -> None:
    import ai_pipeline
    from test_pipeline_smoke import synthetic_landmark_frame

    fake = FakeUI()
    previous = sys.modules.get('streamlit')
    sys.modules['streamlit'] = fake
    sys.path.insert(0, str(ROOT))
    try:
        spec = importlib.util.spec_from_file_location('_swim_integration_with_results_test', ROOT / 'app.py')
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        module.init_state()
        raw = synthetic_landmark_frame(120)
        features = ai_pipeline.add_kinematic_features(raw)
        metadata = {
            'video_name': 'synthetic_video.mp4',
            'processed_frames': len(features),
            'pose_detected_frames': len(features),
            'pose_detection_rate': 1.0,
            'analysis_backend': 'mediapipe_tasks',
        }
        metrics = ai_pipeline.summarize_video(features, metadata)
        recs = ai_pipeline.generate_recommendations(metrics)
        saved = ai_pipeline.save_outputs(tmp_path / 'outputs', 'synthetic_video.mp4', raw, features, metrics, recs)
        fake.session_state.analysis = {
            'work_dir': str(tmp_path), 'video_name': 'synthetic_video.mp4',
            'upload_path': '', 'annotated_path': None,
            'raw_df': raw, 'feature_df': features, 'metrics': metrics,
            'recommendations': recs, 'saved_paths': saved,
        }
        for page in module.PAGES:
            fake.session_state.section = page
            module.run()
        assert fake.renders > 35
    finally:
        if previous is None:
            sys.modules.pop('streamlit', None)
        else:
            sys.modules['streamlit'] = previous
