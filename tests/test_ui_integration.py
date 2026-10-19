"""Static integration checks; no Streamlit import required."""
from pathlib import Path
import ast
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def test_native_ui_app_has_all_routes_and_live_pipeline() -> None:
    app = (ROOT / 'app.py').read_text(encoding='utf-8')
    tree = ast.parse(app)
    functions = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    expected = {
        'page_analyze', 'page_video', 'page_timeseries', 'page_supervised_ml',
        'page_deep_learning', 'page_feedback', 'page_about', 'render_sidebar',
        'render_header', 'analyze_video', 'render_session_summary',
    }
    assert expected <= functions, expected - functions
    assert 'extract_pose_timeseries(' in app
    assert 'add_kinematic_features(' in app
    assert 'save_outputs(' in app
    assert 'train_supervised_models(' in app
    assert 'append_feedback(' in app
    assert 'demo_contextual_bandit_update(' in app
    assert 'st.file_uploader(' in app
    assert 'st.video(' in app
    assert 'st.download_button(' in app
    assert 'st.segmented_control(' in app


def test_lovable_source_is_preserved() -> None:
    ui = ROOT / 'lovable_ui_source'
    required = ['package.json', 'src/styles.css', 'src/routes/index.tsx',
                'src/routes/annotated-video.tsx', 'src/routes/time-series.tsx',
                'src/routes/supervised-ml.tsx', 'src/routes/deep-learning.tsx',
                'src/routes/feedback-learning.tsx', 'src/routes/about.tsx']
    assert all((ui / filename).is_file() for filename in required)
    assert (ROOT / 'swim_ui.py').is_file()
    original_colors = (ui / 'src/styles.css').read_text(encoding='utf-8')
    assert '--hero:' in original_colors and '--sidebar:' in original_colors
    assert 'swim-hero' in (ROOT / 'swim_ui.py').read_text(encoding='utf-8')


def test_credits_and_deployment_files() -> None:
    for name in ['app.py', 'README.md', 'swim_ui.py']:
        content = (ROOT / name).read_text(encoding='utf-8')
        assert 'Jasper Ding' in content and 'Dr. Qingyang Xiao' in content
    for name in ['.streamlit/config.toml', 'requirements.txt',
                 'packages.txt', '.python-version', 'runtime.txt']:
        assert (ROOT / name).is_file()
    assert zipfile.is_zipfile(ROOT / 'vendor/opencv_contrib_python-4.14.0.94-py3-none-any.whl')


def test_mock_values_not_present_in_live_app() -> None:
    app = (ROOT / 'app.py').read_text(encoding='utf-8')
    for sample in ['1:42', '92%', 'Sample F1: 0.90', 'Stroke rate', '8 cycles']:
        assert sample not in app
