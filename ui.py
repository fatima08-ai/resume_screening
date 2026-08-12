"""
ui.py
------
Theme management for the app: light/dark mode CSS, applied at runtime
based on the user's toggle choice.

Design system: everything is driven off CSS variables set once in :root,
so components reference tokens instead of hardcoded colors. If you want to
retint later, change the variables at the top of DARK_CSS / LIGHT_CSS —
you shouldn't need to touch anything below them.
"""

import streamlit as st

FONT_IMPORT = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');
"""

DARK_CSS = f"""
<style>
{FONT_IMPORT}
:root {{
    --bg: #14161c;
    --bg-elevated: #1c1f28;
    --bg-sidebar: #191b22;
    --border: #2a2e3a;
    --text: #eceef2;
    --text-muted: #9296a3;
    --accent: #e3a33e;
    --accent-contrast: #14161c;
    --accent-soft: rgba(227, 163, 62, 0.14);
    --success: #3ecf8e;
    --success-soft: rgba(62, 207, 142, 0.14);
    --danger: #ef5350;
    --danger-soft: rgba(239, 83, 80, 0.14);
    --radius: 10px;
    --font-display: 'Space Grotesk', sans-serif;
    --font-body: 'IBM Plex Sans', sans-serif;
    --font-mono: 'IBM Plex Mono', monospace;
}}
</style>
"""

LIGHT_CSS = f"""
<style>
{FONT_IMPORT}
:root {{
    --bg: #f7f7f5;
    --bg-elevated: #ffffff;
    --bg-sidebar: #efeeea;
    --border: #dcdad3;
    --text: #1c1c1a;
    --text-muted: #6b6a64;
    --accent: #b8791f;
    --accent-contrast: #ffffff;
    --accent-soft: rgba(184, 121, 31, 0.10);
    --success: #1e8e5a;
    --success-soft: rgba(30, 142, 90, 0.10);
    --danger: #c62828;
    --danger-soft: rgba(198, 40, 40, 0.10);
    --radius: 10px;
    --font-display: 'Space Grotesk', sans-serif;
    --font-body: 'IBM Plex Sans', sans-serif;
    --font-mono: 'IBM Plex Mono', monospace;
}}
</style>
"""
SHARED_CSS = """
<style>
    .stApp { background-color: var(--bg); color: var(--text); font-family: var(--font-body); }
    .stApp, .stApp p, .stApp li, .stApp span,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span {
        font-size: 16px !important;
        color: var(--text);
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-display) !important;
        color: var(--text) !important;
        font-weight: 600 !important;
    }
    h1 { font-size: 2.6rem !important; }
    h2 { font-size: 1.6rem !important; }
    h3 { font-size: 1.25rem !important; }
    div[data-testid="stHeadingWithActionElements"] h1,
    [data-testid="stMarkdownContainer"] h1 {
        font-size: 2.6rem !important;
    }

    h1 [data-testid="stIconMaterial"] { font-size: 1.05em !important; }
    h2 [data-testid="stIconMaterial"] { font-size: 1em !important; }
    h3 [data-testid="stIconMaterial"] { font-size: 1em !important; }

    h1, h2, h3 {
        display: flex !important;
        align-items: flex-start;
        gap: 0.35em;
    }
    h1 [data-testid="stIconMaterial"],
    h2 [data-testid="stIconMaterial"],
    h3 [data-testid="stIconMaterial"] {
        margin-top: 0.2em;
        flex-shrink: 0;
    }

    [data-testid="stCaptionContainer"], .stCaption, small {
        color: var(--text-muted) !important;
        font-size: 14px !important;
    }

    hr { border-color: var(--border) !important; }

    .main .block-container,
    [data-testid="stMainBlockContainer"],
    section[data-testid="stMain"] .block-container,
    div[data-testid="stAppViewContainer"] .block-container {
        padding-top: 2rem !important;
    }
    section[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 1rem !important;
    }

    header[data-testid="stHeader"] {
        background-color: var(--bg) !important;
    }
    header[data-testid="stHeader"] * { color: var(--text) !important; }
    div[data-testid="stToolbar"] { background-color: var(--bg) !important; }
    div[data-testid="stDecoration"] { background-image: none !important; background-color: var(--bg) !important; }

    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 1.4rem !important;
        color: var(--text) !important;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: var(--accent) !important;
        font-size: 1.05rem !important;
    }

    label[data-testid="stWidgetLabel"] p {
        font-family: var(--font-body) !important;
        color: var(--text-muted) !important;
        font-weight: 500;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: var(--bg-elevated) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-size: 15px !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: var(--text-muted) !important;
        opacity: 1 !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }
    [data-testid="InputInstructions"],
    [data-testid="stTextAreaInstructions"],
    [class*="InputInstructions"] {
        display: none !important;
    }

    div[data-testid="stSelectbox"] .react-aria-ComboBox,
    div[data-testid="stSelectbox"] .react-aria-ComboBox div {
        background-color: var(--bg-elevated) !important;
    }
    div[data-testid="stSelectbox"] input[role="combobox"] {
        background-color: var(--bg-elevated) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }
    div[data-testid="stSelectbox"] button[aria-haspopup="listbox"] {
        background-color: transparent !important;
        color: var(--text-muted) !important;
    }
    div[data-testid="stSelectbox"] button[aria-haspopup="listbox"] svg {
        fill: var(--text-muted) !important;
    }
    [role="listbox"],
    [role="listbox"] div,
    [role="option"] {
        background-color: var(--bg-elevated) !important;
        color: var(--text) !important;
    }
    [role="option"]:hover {
        background-color: var(--accent-soft) !important;
    }

    .stRadio label span { color: var(--text) !important; font-size: 15px !important; }
    .stRadio [role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .stRadio [role="radiogroup"] label {
        background-color: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 8px 12px;
    }

    section[data-testid="stFileUploaderDropzone"] {
        background-color: var(--bg-elevated) !important;
        border: 1px dashed var(--border) !important;
        border-radius: var(--radius) !important;
    }
    section[data-testid="stFileUploaderDropzone"] * { color: var(--text) !important; }
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }

    div[data-testid="stFileChip"],
    div[data-testid="stFileChip"] div {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }
    div[data-testid="stFileChipName"] {
        color: var(--text) !important;
    }
    small[data-testid="stFileChipDeleteBtn"] {
        color: var(--text-muted) !important;
    }
    small[data-testid="stFileChipDeleteBtn"] svg {
        fill: var(--text-muted) !important;
    }

    button[kind="primary"] {
        background-color: var(--accent) !important;
        color: var(--accent-contrast) !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: var(--radius) !important;
        font-size: 15px !important;
    }
    button[kind="primary"]:hover { filter: brightness(1.1); }
    button[kind="secondary"] {
        background-color: var(--bg-elevated) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-size: 15px !important;
    }
    button[kind="secondary"]:hover { border-color: var(--accent) !important; }

    .st-key-theme_toggle button {
        width: 42px !important;
        height: 42px !important;
        min-width: 42px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 50% !important;
    }
    .st-key-theme_toggle button > div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        gap: 0 !important;
    }
    .st-key-theme_toggle button span {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
    }
    .st-key-theme_toggle button [data-testid="stMarkdownContainer"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--text-muted) !important;
        font-family: var(--font-body) !important;
        font-weight: 500;
        border-radius: var(--radius) var(--radius) 0 0;
        padding: 8px 16px;
    }
    .stTabs [data-baseweb="tab"] p { color: inherit !important; font-size: 15px !important; }
    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 2px solid var(--accent) !important;
    }
    .stTabs [aria-selected="true"] p { color: var(--accent) !important; }

    div[data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        background-color: var(--bg-elevated) !important;
    }
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary p {
        color: var(--text) !important;
        font-size: 15px !important;
        font-weight: 500;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: var(--accent-soft) !important;
    }
    div[data-testid="stExpanderDetails"] {
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    div[data-testid="stMetric"] {
        background-color: var(--bg-elevated);
        padding: 14px;
        border-radius: var(--radius);
        border: 1px solid var(--border);
    }
    div[data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-family: var(--font-mono) !important;
    }
    div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; }

    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: var(--accent) !important;
    }
    .stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] {
        color: var(--text-muted) !important;
    }

    .stProgress > div > div > div { background-color: var(--accent) !important; }

    .stAlert { background-color: var(--bg-elevated) !important; border-radius: var(--radius) !important; }
    .stAlert p { color: var(--text) !important; }

    div[data-testid="stChatMessage"] {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }
    div[data-testid="stChatInput"],
    div[data-testid="stChatInput"] div {
        background-color: var(--bg-elevated) !important;
    }
    div[data-testid="stChatInput"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: var(--bg-elevated) !important;
        color: var(--text) !important;
        border: none !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-muted) !important;
        opacity: 1 !important;
    }
    button[data-testid="stChatInputSubmitButton"] {
        background-color: var(--accent) !important;
        border-radius: var(--radius) !important;
    }
    button[data-testid="stChatInputSubmitButton"] svg {
        fill: var(--accent-contrast) !important;
    }
    div[data-testid="stChatFloatingInputContainer"],
    div[data-testid="stBottomBlockContainer"],
    div[data-testid="stBottom"],
    [class*="stChatFloatingInputContainer"],
    [class*="stBottom"],
    [data-testid*="Bottom"],
    [data-testid*="ChatFloating"],
    [data-testid*="ChatInputContainer"] {
        background-color: var(--bg) !important;
    }
    div[data-testid="stBottomBlockContainer"] .block-container {
        background-color: var(--bg) !important;
        padding-bottom: 1rem !important;
    }

    div[data-testid="stTable"] {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden;
    }
    div[data-testid="stTable"] table {
        color: var(--text) !important;
        font-family: var(--font-body) !important;
        width: 100%;
    }
    div[data-testid="stTable"] thead th {
        background-color: var(--bg-sidebar) !important;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 12px !important;
        letter-spacing: 0.03em;
        border-bottom: 1px solid var(--border) !important;
        padding: 10px 12px !important;
    }
    div[data-testid="stTable"] tbody td {
        border-bottom: 1px solid var(--border) !important;
        padding: 8px 12px !important;
        font-family: var(--font-mono) !important;
        font-size: 14px !important;
    }
    div[data-testid="stTable"] tbody tr:last-child td {
        border-bottom: none !important;
    }
    div[data-testid="stTable"] tbody tr:hover td {
        background-color: var(--accent-soft) !important;
    }

    div[data-testid="stDataFrame"] {
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
    }
    div[data-testid="stDataFrame"] * { color: var(--text) !important; font-family: var(--font-body) !important; }
</style>
"""


def apply_theme():
    """
    Renders a single icon-only toggle button in the sidebar (sun/moon,
    using Material icons) and injects the matching CSS. Call this once,
    early in app.py.
    """
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"

    with st.sidebar:
        icon = ":material/dark_mode:" if st.session_state.theme == "Dark" else ":material/light_mode:"
        if st.button(" ", icon=icon, key="theme_toggle"):
            st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
            st.rerun()

    tokens_css = DARK_CSS if st.session_state.theme == "Dark" else LIGHT_CSS
    st.markdown(tokens_css, unsafe_allow_html=True)
    st.markdown(SHARED_CSS, unsafe_allow_html=True)