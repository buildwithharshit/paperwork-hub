import streamlit as st


# =========================================================
# LIGHT THEME
# Soft luxury / premium fintech
# =========================================================

LIGHT = {
    "background": "#F5F6F8",
    "surface": "#FFFFFF",
    "surface_alt": "#F9FAFB",

    "border": "#E4E7EC",

    "text": "#172033",
    "muted": "#7A8496",

    "primary": "#4B83E8",
    "primary_soft": "#EEF4FF",

    "success": "#4F9F78",
    "success_soft": "#EDF8F2",

    "warning": "#C9953C",
    "warning_soft": "#FFF7E8",

    "danger": "#C95D67",
    "danger_soft": "#FFF0F2",

    "info": "#5C82B8",
    "info_soft": "#EEF4FB",

    "pink": "#C96BA5",
    "purple": "#8171C9",
    "orange": "#D99A4A",

    "shadow": "rgba(15, 23, 42, 0.045)",
}


# =========================================================
# DARK THEME
# Graphite / slate / luxury
# =========================================================

DARK = {
    "background": "#111418",
    "surface": "#191D22",
    "surface_alt": "#20252B",

    "border": "#30363F",

    "text": "#F1F3F5",
    "muted": "#9AA3AE",

    "primary": "#79A7F2",
    "primary_soft": "#1D2A3D",

    "success": "#78C59D",
    "success_soft": "#1D3028",

    "warning": "#DDB76A",
    "warning_soft": "#342D1D",

    "danger": "#E47C86",
    "danger_soft": "#352126",

    "info": "#83A9D8",
    "info_soft": "#202C3C",

    "pink": "#D984B5",
    "purple": "#9588D5",
    "orange": "#DDAA67",

    "shadow": "rgba(0, 0, 0, 0.20)",
}


# =========================================================
# CSS
# =========================================================

def inject_theme(dark=False):

    colors = (
        DARK
        if dark
        else LIGHT
    )

    st.markdown(
        f"""
        <style>

        /* =================================================
           GLOBAL
        ================================================= */

        :root {{
            --bg: {colors["background"]};
            --surface: {colors["surface"]};
            --surface-alt: {colors["surface_alt"]};

            --border: {colors["border"]};

            --text: {colors["text"]};
            --muted: {colors["muted"]};

            --primary: {colors["primary"]};
            --primary-soft: {colors["primary_soft"]};

            --success: {colors["success"]};
            --success-soft: {colors["success_soft"]};

            --warning: {colors["warning"]};
            --warning-soft: {colors["warning_soft"]};

            --danger: {colors["danger"]};
            --danger-soft: {colors["danger_soft"]};

            --info: {colors["info"]};
            --info-soft: {colors["info_soft"]};

            --pink: {colors["pink"]};
            --purple: {colors["purple"]};
            --orange: {colors["orange"]};

            --shadow: {colors["shadow"]};
        }}


        /* =================================================
           APPLICATION
        ================================================= */

        .stApp {{
            background: var(--bg);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        .block-container {{
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}


        /* =================================================
           TYPOGRAPHY
        ================================================= */

        h1,
        h2,
        h3 {{
            color: var(--text) !important;
            letter-spacing: -0.025em;
        }}

        p,
        label,
        [data-testid="stCaptionContainer"] {{
            color: var(--muted);
        }}

        hr {{
            border-color: var(--border) !important;
        }}


        /* =================================================
           SIDEBAR
        ================================================= */

        [data-testid="stSidebar"] {{
            background: var(--surface);
            border-right: 1px solid var(--border);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        [data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            min-height: 2.7rem;

            background: transparent !important;

            color: var(--muted) !important;

            border: 1px solid transparent !important;
            border-radius: 11px;

            font-weight: 600;

            box-shadow: none !important;

            transition:
                background 0.15s ease,
                color 0.15s ease;
        }}

        [data-testid="stSidebar"] .stButton > button:hover {{
            background: var(--primary-soft) !important;
            color: var(--primary) !important;
        }}

        [data-testid="stSidebar"]
        .stButton > button[kind="primary"] {{
            background: var(--primary) !important;
            color: #FFFFFF !important;
            border-color: var(--primary) !important;
        }}

        [data-testid="stSidebar"]
        .stButton > button[kind="primary"]:hover {{
            background: var(--primary) !important;
            color: #FFFFFF !important;
        }}


        /* =================================================
           TOGGLE
        ================================================= */

        [data-testid="stSidebar"] [data-testid="stToggle"] label {{
            color: var(--text) !important;
            font-weight: 600;
        }}

        [data-testid="stSidebar"]
        [data-testid="stToggle"]
        [role="switch"] {{
            background: #D7DCE3 !important;
            border: 1px solid #B9C0CA !important;
        }}

        [data-testid="stSidebar"]
        [data-testid="stToggle"]
        [role="switch"][aria-checked="true"] {{
            background: var(--primary) !important;
            border-color: var(--primary) !important;
        }}


        /* =================================================
           METRICS
        ================================================= */

        [data-testid="stMetric"] {{
            background: var(--surface);

            border: 1px solid var(--border);
            border-radius: 14px;

            padding: 1rem 1.1rem;

            box-shadow:
                0 8px 24px var(--shadow);
        }}

        [data-testid="stMetricLabel"] {{
            color: var(--muted) !important;
        }}

        [data-testid="stMetricValue"] {{
            color: var(--text) !important;
        }}


        /* =================================================
           TEXT INPUTS
        ================================================= */

        [data-testid="stTextInput"] input {{
            background: var(--surface) !important;

            color: var(--text) !important;

            border: 1px solid var(--border) !important;

            border-radius: 10px !important;
        }}

        [data-testid="stTextInput"] input::placeholder {{
            color: var(--muted) !important;
        }}

        [data-testid="stTextInput"] input:focus {{
            border-color: var(--primary) !important;

            box-shadow:
                0 0 0 1px var(--primary) !important;
        }}


        /* =================================================
           SELECTBOX
        ================================================= */

        [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
            background: var(--surface) !important;

            color: var(--text) !important;

            border: 1px solid var(--border) !important;

            border-radius: 10px !important;
        }}

        [data-testid="stSelectbox"] svg {{
            color: var(--muted) !important;
        }}


        /* =================================================
           FILE UPLOADER
        ================================================= */

        [data-testid="stFileUploader"] {{
            background: var(--surface);

            border: 1px dashed var(--primary);

            border-radius: 16px;

            padding: 0.35rem;
        }}

        [data-testid="stFileUploaderDropzone"] {{
            background: var(--surface) !important;

            border: 0 !important;

            border-radius: 12px;
        }}

        [data-testid="stFileUploaderDropzone"] button {{
            background: var(--surface-alt) !important;

            color: var(--text) !important;

            border: 1px solid var(--border) !important;

            border-radius: 9px !important;
        }}


        /* =================================================
           BUTTONS
        ================================================= */

        .stButton > button,
        .stDownloadButton > button {{
            border-radius: 10px;

            min-height: 2.45rem;

            font-weight: 600;
        }}

        .stButton > button[kind="primary"] {{
            background: var(--primary) !important;

            border-color: var(--primary) !important;

            color: #FFFFFF !important;
        }}

        .stDownloadButton > button {{
            background: var(--surface) !important;

            color: var(--text) !important;

            border: 1px solid var(--border) !important;
        }}

        .stDownloadButton > button:hover {{
            border-color: var(--primary) !important;

            color: var(--primary) !important;
        }}


        /* =================================================
           EXPANDERS
        ================================================= */

        [data-testid="stExpander"] {{
            background: var(--surface) !important;

            border: 1px solid var(--border) !important;

            border-radius: 14px;
        }}


        /* =================================================
           ALERTS
        ================================================= */

        [data-testid="stAlert"] {{
            border-radius: 12px;
        }}

        /* Softer success */
        [data-testid="stAlert"][kind="success"] {{
            background: var(--success-soft) !important;
        }}

        /* Softer warning */
        [data-testid="stAlert"][kind="warning"] {{
            background: var(--warning-soft) !important;
        }}

        /* Softer info */
        [data-testid="stAlert"][kind="info"] {{
            background: var(--info-soft) !important;
        }}

        /* Softer error */
        [data-testid="stAlert"][kind="error"] {{
            background: var(--danger-soft) !important;
        }}


       /* =================================================
   DATAFRAME
           ================================================= */

          [data-testid="stDataFrame"] {{
          border: 1px solid var(--border);
          border-radius: 14px;
          overflow: hidden;
          background: var(--surface) !important;
        }}

          [data-testid="stDataFrame"] iframe {{
          background: var(--surface) !important;
        }}

          [data-testid="stDataFrame"] > div {{
          background: var(--surface) !important;
        }}

           [data-testid="stDataFrame"] [role="grid"] {{
           background: var(--surface) !important;
        }}

           [data-testid="stDataFrame"] [role="row"] {{
           background: var(--surface) !important;
        }}

           [data-testid="stDataFrame"] [role="gridcell"] {{
           background: var(--surface) !important;
           color: var(--text) !important;
        }}

           [data-testid="stDataFrame"] [role="columnheader"] {{
             background: var(--surface-alt) !important;
           color: var(--text) !important;
        }}

        /* =================================================
           SCROLLBAR
        ================================================= */

        ::-webkit-scrollbar {{
            width: 7px;
            height: 7px;
        }}

        ::-webkit-scrollbar-track {{
            background: transparent;
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--border);

            border-radius: 10px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--muted);
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# PLOTLY COLORS
# =========================================================

def plotly_theme(dark=False):

    colors = (
        DARK
        if dark
        else LIGHT
    )

    return {
        "paper_bgcolor": colors["surface"],

        "plot_bgcolor": colors["surface"],

        "font_color": colors["text"],

        "muted": colors["muted"],

        "border": colors["border"],

        "primary": colors["primary"],

        "success": colors["success"],

        "warning": colors["warning"],

        "danger": colors["danger"],

        "pink": colors["pink"],

        "purple": colors["purple"],

        "orange": colors["orange"],
    }