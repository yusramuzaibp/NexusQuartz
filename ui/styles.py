
import streamlit as st


def apply_global_styles():
    """Apply consistent styling across the healthcare application."""

    st.markdown("""
        <style>

        /* ================= GLOBAL APP ================= */

        .stApp {
            background-color: #D5ECEE !important;
        }

        [data-testid="stAppViewContainer"] {
            background-color: #D5ECEE !important;
        }

        [data-testid="stMain"] {
            background-color: #D5ECEE !important;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        h1, h2, h3 {
            color: #073B4C;
        }


        /* ================= SIDEBAR ================= */

        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarHeader"] {
            background-color: #55A8B3 !important;
        }

        section[data-testid="stSidebar"] {
            border-right: 1px solid #438F99 !important;
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
            background-color: #C5E9EC !important;
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
            background-color: rgba(255, 255, 255, 0.65);
            color: #07566B;
            border: 1px solid #C5E7E9;
            border-radius: 10px;
        }

        section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
            background-color: #FFFFFF;
            border-color: #087E8B;
            color: #07566B;
        }


        /* ================= GENERAL BUTTONS ================= */

        div[data-testid="stButton"] > button {
            border-radius: 10px;
            min-height: 42px;
            font-weight: 600;
            border: 1px solid #DCE7EB;
        }

        div[data-testid="stButton"] > button:hover {
            border-color: #087E8B;
            color: #087E8B;
        }


        /* ================= INPUTS ================= */

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {
            border-radius: 9px;
        }


        /* ================= CARDS ================= */

        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            padding: 18px;
            border-radius: 14px;
            border: 1px solid #E5EDF0;
        }

        </style>
    """, unsafe_allow_html=True)
