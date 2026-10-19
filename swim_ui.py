"""Native Streamlit rendering helpers adapted from the provided Lovable design.

The Lovable source lives in lovable_ui_source/. This Python counterpart uses the
same main palette, side settings, hero, recording checklist, navigation and cards,
while leaving controls native to Streamlit for reliable Community Cloud uploads.

Author: Jasper Ding | Advisor: Dr. Qingyang Xiao
"""
from __future__ import annotations

from html import escape


LOVABLE_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
    --swim-bg: #f7fafb;
    --swim-text: #203b4e;
    --swim-primary: #168397;
    --swim-primary-hover: #106d80;
    --swim-sidebar: #eaf4f5;
    --swim-border: #d9e7eb;
    --swim-muted: #687c89;
    --swim-card: #ffffff;
    --swim-coach: #153446;
    --swim-accent: #f4b34e;
}
html, body, [data-testid='stAppViewContainer'] {
    background: var(--swim-bg) !important;
    color: var(--swim-text);
    font-family: 'Manrope', Arial, sans-serif;
}
[data-testid='stMainBlockContainer'] {max-width: 1280px; padding-top: 1.1rem; padding-bottom: 4rem;}
[data-testid='stHeader'] {background: rgba(247,250,251,0.90);}
[data-testid='stSidebar'] {background: var(--swim-sidebar); border-right: 1px solid #d5e5e9;}
[data-testid='stSidebar'] [data-testid='stVerticalBlock'] {gap: .74rem;}
[data-testid='stSidebar'] [data-testid='stMarkdownContainer'] {font-family: 'Manrope',Arial,sans-serif;}
[data-testid='stSidebar'] h1, [data-testid='stSidebar'] h2 {font-size: .98rem !important;}
[data-testid='stSidebar'] label {font-size: .8rem !important; color: #294c5d !important;}
[data-testid='stSidebar'] hr {margin: .65rem 0 1rem; border-color: #d5e5e9;}
[data-testid='stSidebar'] [data-baseweb='select'] > div {border-radius: 8px; background: white;}
[data-testid='stSidebar'] [data-testid='stWidgetLabel'] p {font-weight: 650;}
[data-testid='stApp'] h1, [data-testid='stApp'] h2, [data-testid='stApp'] h3 {font-family: 'Manrope',Arial,sans-serif; letter-spacing: -.035em; color: var(--swim-text);}
[data-testid='stApp'] .stButton > button[kind='primary'],
[data-testid='stApp'] .stDownloadButton > button[kind='primary'],
[data-testid='stApp'] button[data-testid='stBaseButton-primary'] {
    background: var(--swim-primary); color: white; border: 1px solid var(--swim-primary);
    border-radius: 8px; font-weight: 750; box-shadow: 0 3px 10px rgba(25,127,149,.15);
}
[data-testid='stApp'] .stButton > button[kind='primary']:hover,
[data-testid='stApp'] .stDownloadButton > button[kind='primary']:hover,
[data-testid='stApp'] button[data-testid='stBaseButton-primary']:hover {background:var(--swim-primary-hover); color:white;}
[data-testid='stApp'] .stButton button,
[data-testid='stApp'] .stDownloadButton button {border-radius:8px; min-height:2.6rem;}
[data-testid='stFileUploader'] {border:1.5px dashed #95b7c4; border-radius:11px; background:#fbfefe; padding: .6rem;}
[data-testid='stFileUploader'] > section {background:#f9fdfd; border:none; min-height:200px; border-radius:8px;}
[data-testid='stFileUploader'] > section:hover {background:#edf8f9;}
[data-testid='stFileUploader'] button {background:#168397; color:white; border:none; font-weight:700; border-radius:7px;}
[data-testid='stFileUploader'] button:hover {background:#116d7d; color:white;}
[data-testid='stMetric'] {border:1px solid var(--swim-border); border-radius:9px; padding: 16px; background:white; box-shadow: 0 4px 20px rgba(16,53,71,.045);}
[data-testid='stMetricLabel'] {font-size:.79rem;color:var(--swim-muted)}
[data-testid='stMetricValue'] {font-size:1.7rem; font-weight:800; color:var(--swim-text); letter-spacing:-.04em;}
[data-testid='stDataFrame'] {border-radius:9px; overflow:hidden;}
[data-testid='stAlert'] {border-radius:9px;}
[data-testid='stForm'] {background:white; padding:1rem 1.25rem; border:1px solid var(--swim-border); border-radius:10px;}
[data-testid='stExpander'] {background:white;border:1px solid var(--swim-border);border-radius:9px;}
/* Navigation: use a native, keyboard-accessible Streamlit segmented-control. */
[data-testid='stSegmentedControl'] {padding: 0 0 4px;}
[data-testid='stSegmentedControl'] button {background: transparent !important; border:0 !important; color:#677c88; font-weight:650; font-size:.84rem; padding:.63rem .9rem; border-radius:5px;}
[data-testid='stSegmentedControl'] button[aria-pressed='true'] {color:#0c7285 !important; background:#e0f1f3 !important; box-shadow:inset 0 -2px #168397;}
[data-testid='stSegmentedControl'] button:hover {color:#14768a !important;}
.swim-brand {display:flex;align-items:center;gap:12px; margin-bottom:1.12rem; padding:5px 0 14px; border-bottom:1px solid var(--swim-border)}
.swim-logo {display:grid;place-items:center;width:38px;height:38px;border-radius:8px;background:#166c82;color:white;font-size:23px;font-weight:800;}
.swim-brand-title {font-weight:800;font-size:14px;letter-spacing:-.02em;color:#183b50;}
.swim-brand-subtitle {font-size:12px;color:#687c89;margin-top:2px;}
.swim-topbar {border-bottom:1px solid var(--swim-border); display:flex; align-items:center; justify-content:space-between; padding:9px 0 17px; margin-bottom:9px;}
.swim-topbar h2 {font-size:15px !important;line-height:1.4;margin:0;font-weight:800 !important;}
.swim-topbar p {font-size:12px;color:#687c89;margin:2px 0 0;}
.swim-top-status {background:#e6f4ec;border-radius:100px;color:#22734e;padding:6px 12px;font-size:11px;font-weight:750;}
.swim-hero {background:linear-gradient(116deg,#183c52 0%,#19495d 62%,#1e6671 100%);border-radius:10px;padding:34px 37px;color:#fff;box-shadow:0 13px 38px rgba(21,54,69,.12); margin:20px 0 21px;}
.swim-hero .eyebrow {font-size:11px;letter-spacing:.17em;text-transform:uppercase;font-weight:800;color:#d5ebed; margin-bottom:15px;}
.swim-hero h1 {color:#fff !important;font-size:clamp(1.7rem,3vw,2.6rem) !important;line-height:1.2;margin:0 0 11px;font-weight:800 !important;max-width:820px;}
.swim-hero p {color:#cbdee2;font-size:14px;line-height:1.75;margin:0;max-width:780px;}
.swim-notice {display:flex;gap:12px;background:#edf5fa;border:1px solid #cedfe9;border-radius:8px;color:#24516b;padding:13px 16px;font-size:12px;line-height:1.6;margin-bottom:30px;}
.swim-section-kicker {font-size:11px;font-weight:850;text-transform:uppercase;letter-spacing:.14em;color:#168397;margin-bottom:5px;}
.swim-section-title {font-size:20px;font-weight:850;letter-spacing:-.04em;color:#203b4e;margin:2px 0 5px;line-height:1.4;}
.swim-section-intro {font-size:13px;color:#687c89;line-height:1.7;margin:0 0 22px;}
.swim-guide-heading {font-size:15px;font-weight:750;color:#274354;margin:1px 0 15px;}
.swim-guide-item {display:flex; gap:11px; color:#687c89; font-size:13px; line-height:1.6;margin:0 0 15px;}
.swim-check {color:#2a9a74;font-weight:900;font-size:15px;}
.swim-tip {border-radius:8px;background:#e5f2f5;padding:17px;color:#345367;font-size:13px;line-height:1.6;margin-top:14px;}
.swim-tip strong {text-transform:uppercase;color:#17778a;letter-spacing:.12em;font-size:11px;}
.swim-feature-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin-top:16px;}
.swim-feature {display:flex;gap:12px;align-items:start;}
.swim-feature-num {font-size:11px;font-family:'IBM Plex Mono',monospace;color:#168397;font-weight:750;padding-top:3px;}
.swim-feature h3 {font-size:14px !important;font-weight:750;margin:0 0 6px;color:#2c4656;}
.swim-feature p {font-size:12px;line-height:1.8;color:#687c89;margin:0;}
.swim-card {background:#fff;border:1px solid var(--swim-border);border-radius:9px;padding:21px;box-shadow:0 6px 24px rgba(24,53,67,.045);height:100%;margin-bottom:13px;}
.swim-card h3 {font-size:14px !important;font-weight:800;margin:0 0 8px;color:#24465a;}
.swim-card p {color:#687c89;font-size:13px;line-height:1.75;margin:0;}
.swim-coach {background:#19394b;color:white;border-radius:10px;padding:25px 27px;margin:11px 0 18px;box-shadow:0 9px 26px rgba(12,42,60,.12);}
.swim-coach .kicker {text-transform:uppercase;font-size:11px;letter-spacing:.13em;font-weight:750;color:#efb957;}
.swim-coach h3 {color:white !important;margin:13px 0 8px;font-size:21px !important;font-weight:800;}
.swim-coach p {font-size:13px;color:#d5e3e9;line-height:1.8;margin:0 0 10px;}
.swim-coach .drill {margin-top:13px;border-top:1px solid #48626e;padding-top:12px;color:#f7d19a;}
.swim-rec {border:1px solid var(--swim-border);border-left:4px solid #168397;border-radius:8px;background:white;padding:15px 17px;margin:10px 0;}
.swim-rec[data-priority='high'] {border-left-color:#cc6359;}
.swim-rec[data-priority='medium'] {border-left-color:#dfa34b;}
.swim-rec .heading {font-size:14px;font-weight:800;color:#263e50;margin-bottom:5px;}
.swim-rec .meta {font-size:11px;color:#8a6a49;margin-bottom:7px;}
.swim-rec p {font-size:12px;line-height:1.65;color:#536d7b;margin:5px 0;}
.swim-small-muted {font-size:12px;color:#738793;line-height:1.7;}
.swim-pill {display:inline-flex;padding:5px 10px;background:#e6f2f4;color:#197d91;border-radius:60px;font-size:11px;font-weight:750;}
.swim-upload-label {font-size:11px;letter-spacing:.12em;color:#168397;font-weight:850;text-transform:uppercase;}
.swim-side-caption {font-size:12px;color:#667d88;line-height:1.7;}
.swim-empty {border:1px dashed #a7c4ce;border-radius:9px;background:#f9fdfd;padding:35px 24px;text-align:center;color:#657e8c;margin:20px 0;}
.swim-empty strong {display:block;color:#244b5b;font-size:16px;margin-bottom:5px;}
.swim-rule {border:0;border-top:1px solid var(--swim-border);margin:33px 0 24px;}
@media(max-width:760px){
 .swim-hero {padding:26px 23px;} .swim-feature-grid{grid-template-columns:1fr;}
 .swim-top-status{display:none;} [data-testid='stMainBlockContainer']{padding-top:1rem;}
}
</style>
"""


def clean(value: object) -> str:
    return escape(str(value) if value is not None else "", quote=True)


def metric_html(label: str, value: str, details: str = "") -> str:
    return (
        '<div class="swim-card" style="min-height:130px">'
        f'<div style="font-size:12px;color:#6d8490">{clean(label)}</div>'
        f'<div style="font-size:29px;color:#193c4f;font-weight:850;margin:14px 0 4px;">{clean(value)}</div>'
        f'<div class="swim-small-muted">{clean(details)}</div></div>'
    )


def card_html(title: str, body: str) -> str:
    return f'<div class="swim-card"><h3>{clean(title)}</h3><p>{clean(body)}</p></div>'


def page_intro(eyebrow: str, title: str, text: str) -> str:
    return (
        f'<div class="swim-section-kicker">{clean(eyebrow)}</div>'
        f'<div class="swim-section-title" style="font-size:29px">{clean(title)}</div>'
        f'<div class="swim-section-intro">{clean(text)}</div>'
    )
