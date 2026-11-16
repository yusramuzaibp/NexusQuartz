
import streamlit as st
import pandas as pd

from database.database import get_user_predictions
from ui.dashboard_ui import render_dashboard


def show_dashboard():

    # Fetch prediction history
    history = get_user_predictions(st.session_state.user_id)
    df = pd.DataFrame(history)

    total = len(df)

    # Calculate disease-wise counts
    if total and "condition" in df.columns:
        diabetes_count = (df["condition"] == "Diabetes").sum()
        heart_count = (df["condition"] == "Heart Disease").sum()
        parkinsons_count = (df["condition"] == "Parkinsons").sum()
    else:
        diabetes_count = 0
        heart_count = 0
        parkinsons_count = 0

    # Render dashboard UI
    render_dashboard(
        total=total,
        diabetes_count=diabetes_count,
        heart_count=heart_count,
        parkinsons_count=parkinsons_count,
        history_df=df
    )
