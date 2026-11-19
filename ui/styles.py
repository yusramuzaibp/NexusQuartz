
import streamlit as st
import base64
from pathlib import Path


def apply_global_styles():
    """Apply consistent global styling across the healthcare application."""

    # ================= GLOBAL BACKGROUND IMAGE =================

    image_path = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "dashboard.png"
    )

    if image_path.exists():
        image_base64 = base64.b64encode(
            image_path.read_bytes()
        ).decode("utf-8")

        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image:
                    linear-gradient(
                        rgba(243, 248, 250, 0.45),
                        rgba(243, 248, 250, 0.45)
                    ),
                    url("data:image/png;base64,{image_base64}");

                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}

            [data-testid="stMain"],
            [data-testid="stMainBlockContainer"] {{
                background: transparent !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    else:
        st.warning(f"Background image not found: {image_path}")

    # ================= GLOBAL STYLING =================

    st.markdown("""
        <style>

        /* ================= MAIN APPLICATION ================= */

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            background-color: transparent !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }


        /* ================= HEADINGS ================= */

        h1, h2, h3 {
            color: #073B4C !important;
            font-weight: 700;
        }


        /* ================= SIDEBAR ================= */

        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarHeader"] {
            background-color: #C9E7E9 !important;
        }

        section[data-testid="stSidebar"] {
            border-right: 1px solid #B5DDE0 !important;
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.5rem;
        }


        /* ================= SIDEBAR TEXT ================= */

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: #073B4C !important;
        }


        /* ================= NAVIGATION MENU ================= */

        [data-testid="stSidebar"] .nav-link {
            color: #36525F !important;
            background-color: transparent !important;
            border-radius: 10px !important;
            margin: 5px 0 !important;
            padding: 12px 14px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out;
        }

        [data-testid="stSidebar"] .nav-link:hover {
            background-color: #E4F3F4 !important;
            color: #07566B !important;
        }

        [data-testid="stSidebar"] .nav-link-selected {
            background-color: #FFFFFF !important;
            color: #07566B !important;
            font-weight: 700 !important;
        }

        [data-testid="stSidebar"] .nav-link i {
            color: #087E8B !important;
        }


        /* ================= SIDEBAR BUTTONS ================= */

        section[data-testid="stSidebar"] div[data-testid="stButton"] button {
            background-color: #EAF7F7 !important;
            color: #07566B !important;
            border: 1px solid #C5E7E9 !important;
            border-radius: 10px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
            background-color: #FFFFFF !important;
            border-color: #087E8B !important;
            color: #07566B !important;
        }


        /* ================= GENERAL BUTTONS ================= */

        div[data-testid="stButton"] > button {
            background-color: #F0FAFA !important;
            color: #07566B !important;
            border-radius: 10px !important;
            min-height: 42px;
            font-weight: 600;
            border: 1px solid #C5E7E9 !important;
            transition: all 0.2s ease-in-out;
        }

        div[data-testid="stButton"] > button:hover {
            background-color: #DDF1F2 !important;
            border-color: #087E8B !important;
            color: #07566B !important;
        }


        /* ================= INPUTS ================= */

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            border-radius: 9px;
        }


        /* ================= METRIC CARDS ================= */

        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            padding: 18px;
            border-radius: 14px;
            border: 1px solid #E5EDF0;
        }

        </style>
    """, unsafe_allow_html=True)
