
import streamlit as st
import pandas as pd
import calendar
from datetime import date
from html import escape
import base64
from pathlib import Path


def render_dashboard(
    total,
    diabetes_count,
    heart_count,
    parkinsons_count,
    history_df
):
    today = date.today()
    # ================= GLOBAL DASHBOARD STYLING =================

    st.markdown("""
    <style>
    .dash-stat {
        background: white;
        border: 1px solid #E2EDF0;
        border-radius: 16px;
        padding: 20px;
        min-height: 130px;
        box-shadow: 0 3px 12px rgba(7,59,76,.05);
    }

    .dash-stat-icon {
        font-size: 23px;
        margin-bottom: 9px;
    }

    .dash-stat-value {
        font-size: 30px;
        font-weight: 750;
        color: #073B4C;
    }

    .dash-stat-label {
        font-size: 13px;
        color: #64748B;
        font-weight: 600;
    }

    .dash-panel {
        background: white;
        border: 1px solid #E2EDF0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 3px 12px rgba(7,59,76,.05);
        min-height: 100%;
    }

    .dash-panel-title {
        font-size: 18px;
        font-weight: 700;
        color: #073B4C;
        margin-bottom: 14px;
    }

    .calendar-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 5px;
        text-align: center;
    }

    .calendar-table th {
        color: #64748B;
        font-size: 12px;
        padding: 8px 2px;
    }

    .calendar-table td {
        height: 37px;
        border-radius: 9px;
        font-size: 13px;
        color: #334155;
    }

    .calendar-today {
        background: #087E8B;
        color: white !important;
        font-weight: 800;
    }

    .calendar-empty {
        background: transparent;
    }

    .activity-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }

    .activity-table th {
        background: #F5F8FA;
        color: #64748B;
        padding: 13px;
        text-align: left;
        font-size: 12px;
        text-transform: uppercase;
        border-bottom: 1px solid #E2EDF0;
    }

    .activity-table td {
        padding: 14px 13px;
        color: #334155;
        border-bottom: 1px solid #EDF2F4;
    }

    .activity-table tr:last-child td {
        border-bottom: none;
    }

    .risk-pill {
        padding: 5px 12px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
    }

    .risk-low {
        background: #DCFCE7;
        color: #15803D;
    }

    .risk-high {
        background: #FEE2E2;
        color: #B91C1C;
    }
    </style>
    """, unsafe_allow_html=True)

    # ================= PAGE HEADING =================

    st.markdown(
        """
        <h1 style="color:#073B4C; margin-bottom:5px;">
            Dashboard Overview
        </h1>
        <p style="color:#64748B; margin-bottom:25px;">
            Your personal health prediction activity at a glance.
        </p>
        """,
        unsafe_allow_html=True
    )

    # ================= STATISTICS =================

    stats = [
        ("📊", total, "Total Predictions"),
        ("🩸", diabetes_count, "Diabetes Tests"),
        ("❤️", heart_count, "Heart Disease Tests"),
        ("🧠", parkinsons_count, "Parkinson's Tests")
    ]

    columns = st.columns(4)

    for col, (icon, value, label) in zip(columns, stats):
        with col:
            st.markdown(
                f"""
                <div class="dash-stat">
                    <div class="dash-stat-icon">{icon}</div>
                    <div class="dash-stat-value">{value}</div>
                    <div class="dash-stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= CHART + CALENDAR =================

    chart_col, calendar_col = st.columns([2, 1], gap="large")

    with chart_col:

        st.markdown(
            '<div class="dash-panel-title">📈 Prediction Activity Timeline</div>',
            unsafe_allow_html=True
        )

        if (
            not history_df.empty
            and "timestamp" in history_df.columns
        ):
            chart_data = history_df.copy()

            chart_data["Date"] = pd.to_datetime(
                chart_data["timestamp"], errors="coerce"
            ).dt.date

            chart_data = chart_data.dropna(subset=["Date"])

            if not chart_data.empty:

                daily_counts = (
                    chart_data.groupby("Date")
                    .size()
                    .reset_index(name="Predictions")
                    .sort_values("Date")
                )

                st.line_chart(
                    daily_counts,
                    x="Date",
                    y="Predictions",
                    color="#087E8B",
                    use_container_width=True,
                    height=300,
                    width="stretch"
                )

                st.caption(
                    "Daily number of predictions recorded in your account."
                )

            else:
                st.info("No valid prediction timestamps available.")

        else:
            st.info("Your prediction timeline will appear here once you run a prediction.")

    with calendar_col:

        # Initialize calendar month
        if "dashboard_calendar_month" not in st.session_state:
            st.session_state.dashboard_calendar_month = today.replace(day=1)

        current_month = st.session_state.dashboard_calendar_month

        # Month navigation
        previous_col, month_col, next_col = st.columns([1, 4, 1])

        with previous_col:
            if st.button("◀", key="calendar_previous"):
                year = current_month.year
                month = current_month.month - 1

                if month == 0:
                    month = 12
                    year -= 1

                st.session_state.dashboard_calendar_month = date(
                    year, month, 1
                )
                st.rerun()

        with month_col:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    color:#073B4C;
                    font-weight:750;
                    font-size:17px;
                    padding-top:5px;
                ">
                    {calendar.month_name[current_month.month]} {current_month.year}
                </div>
                """,
                unsafe_allow_html=True
            )

        with next_col:
            if st.button("▶", key="calendar_next"):
                year = current_month.year
                month = current_month.month + 1

                if month == 13:
                    month = 1
                    year += 1

                st.session_state.dashboard_calendar_month = date(
                    year, month, 1
                )
                st.rerun()

        # Build calendar with Sunday as the first day
        calendar_generator = calendar.Calendar(
            firstweekday=calendar.SUNDAY
        )

        month_calendar = calendar_generator.monthdayscalendar(
        current_month.year,
        current_month.month
     )

        calendar_html = """
        <table class="calendar-table">
        <thead>
        <tr>
            <th>Su</th><th>Mo</th><th>Tu</th>
            <th>We</th><th>Th</th><th>Fr</th><th>Sa</th>
        </tr>
        </thead>
        <tbody>
        """

        for week in month_calendar:
            calendar_html += "<tr>"

            for day in week:
                if day == 0:
                    calendar_html += (
                        '<td class="calendar-empty"></td>'
                    )

                elif (
                    day == today.day
                    and current_month.month == today.month
                    and current_month.year == today.year
                ):
                    calendar_html += (
                        f'<td class="calendar-today">{day}</td>'
                    )

                else:
                    calendar_html += f"<td>{day}</td>"

            calendar_html += "</tr>"

        calendar_html += "</tbody></table>"

        st.markdown(calendar_html, unsafe_allow_html=True)

        st.caption(
            f"Today: {today.strftime('%d %B %Y')}"
        )

    # ================= RECENT HEALTH ACTIVITY =================

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="dash-panel-title">📋 Recent Health Activity</div>',
        unsafe_allow_html=True
    )

    if not history_df.empty:

        recent = history_df.copy()

        if "timestamp" in recent.columns:
            recent["_sort_date"] = pd.to_datetime(
                recent["timestamp"], errors="coerce"
            )
            recent = recent.sort_values(
                "_sort_date",
                ascending=False,
                na_position="last"
            )

        recent = recent.head(10)

        rows = ""

        for _, row in recent.iterrows():

            condition = escape(str(row.get("condition", "Unknown")))
            risk = str(row.get("risk", "Unknown"))
            safe_risk = escape(risk)

            timestamp = row.get("timestamp", "")
            parsed_date = pd.to_datetime(
                timestamp, errors="coerce"
            )

            date_text = (
                parsed_date.strftime("%b %d, %Y")
                if pd.notna(parsed_date)
                else escape(str(timestamp))
            )

            risk_class = (
                "risk-high"
                if risk.strip().lower() == "high"
                else "risk-low"
            )

            rows += f"""
            <tr>
                <td>{condition}</td>
                <td>{date_text}</td>
                <td>
                    <span class="risk-pill {risk_class}">
                        {safe_risk} Risk
                    </span>
                </td>
            </tr>
            """

        st.markdown(
            f"""
            <div class="dash-panel">
                <table class="activity-table">
                    <thead>
                        <tr>
                            <th>Condition</th>
                            <th>Date</th>
                            <th>Risk</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.info(
            "No predictions yet. Visit Disease Prediction to get started."
        )
