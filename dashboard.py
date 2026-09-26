import streamlit as st
import pandas as pd
from datetime import datetime


def show_dashboard():
    st.title('Dashboard')
    st.write("Here's an overview of your recent prediction activity.")

    history = st.session_state.history
    df = pd.DataFrame(history)

    total = len(history)
    diabetes_count = len(df[df['condition'] == 'Diabetes']) if total else 0
    heart_count = len(df[df['condition'] == 'Heart Disease']) if total else 0
    parkinsons_count = len(df[df['condition'] == 'Parkinsons']) if total else 0
    high_risk_count = len(df[df['risk'] == 'High']) if total else 0

    # ---- stat cards ----
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Predictions', total)
    col2.metric('Diabetes Tests', diabetes_count)
    col3.metric('Heart Disease Tests', heart_count)
    col4.metric('Parkinsons Tests', parkinsons_count)

    st.markdown('---')

    # ---- recent health activity (single self-contained HTML block) ----
    if total:
        recent = df.sort_values('timestamp', ascending=False).head(10)
        table_rows = ""
        for _, row in recent.iterrows():
            try:
                date_str = datetime.strptime(
                    row['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
            except ValueError:
                date_str = row['timestamp']
            pill_class = 'rha-pill-high' if row['risk'] == 'High' else 'rha-pill-low'
            table_rows += (
                f'<tr><td>{row["condition"]}</td><td>{date_str}</td>'
                f'<td><span class="rha-pill {pill_class}">{row["risk"]} Risk</span></td></tr>'
            )
        body_html = (
            '<table class="rha-table"><thead><tr>'
            '<th>Condition</th><th>Date</th><th>Risk</th>'
            f'</tr></thead><tbody>{table_rows}</tbody></table>'
        )
    else:
        body_html = ('<div class="rha-empty">No predictions run yet. '
                     'Go to Disease Prediction to get started.</div>')

    st.markdown(f"""
        <style>
        .rha-card{{background:#fff;border-radius:14px;padding:22px 24px;
                  box-shadow:0 1px 3px rgba(15,23,42,.08); color-scheme:light;}}
        .rha-card, .rha-card *{{color:#0f172a !important;}}
        .rha-header{{display:flex;align-items:center;justify-content:space-between;
                    margin-bottom:14px;}}
        .rha-title{{font-weight:700;font-size:18px;margin:0;}}
        .rha-viewall{{color:#0f766e !important;font-weight:700;font-size:14px;}}
        .rha-table{{width:100%;border-collapse:collapse;font-size:14px;}}
        .rha-table th{{
            text-align:left;padding:10px 12px;background:#f8fafc;
            font-size:12px;letter-spacing:.03em;color:#64748b !important;
            border-bottom:1px solid #e2e8f0;
        }}
        .rha-table td{{padding:12px;border-bottom:1px solid #f1f5f9;}}
        .rha-table tr:last-child td{{border-bottom:none;}}
        .rha-pill{{display:inline-block;padding:4px 12px;border-radius:999px;
                  font-size:12.5px;font-weight:700;white-space:nowrap;}}
        .rha-pill-low{{background:#dcfce7 !important;color:#15803d !important;}}
        .rha-pill-high{{background:#fee2e2 !important;color:#b91c1c !important;}}
        .rha-empty{{color:#64748b !important;font-size:14px;padding:8px 0;}}
        </style>
        <div class="rha-card">
            <div class="rha-header">
                <div class="rha-title">Recent Health Activity</div>
                <div class="rha-viewall">View all</div>
            </div>
            {body_html}
        </div>
    """, unsafe_allow_html=True)

