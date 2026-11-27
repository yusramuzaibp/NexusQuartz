
import streamlit as st
import pandas as pd
import plotly.express as px
import html
from utils.encryption import decrypt_text

from database.database import (
    db_cursor,
    get_all_users,
    get_all_predictions,
    update_user,
    update_user_status,
    delete_user,
)


# ================= ADMIN ACCESS SECURITY =================

def require_admin():
    """Verify login, active status, and admin role directly from Neon."""

    if not st.session_state.get("logged_in", False):
        st.error("Access denied. Please log in first.")
        st.stop()

    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("Access denied. Invalid user session.")
        st.stop()

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT role, status
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )
            user = cursor.fetchone()

    except Exception as e:
        st.error(f"Unable to verify admin access: {e}")
        st.stop()

    if not user:
        st.error("Access denied. User account not found.")
        st.stop()

    role, status = user
    role = (role or "").strip().lower()
    status = (status or "").strip().lower()

    if status != "active":
        st.error("Access denied. Your account is not active.")
        st.stop()

    if role != "admin":
        st.error("Access denied. Admin privileges are required.")
        st.stop()

    return True


# ================= ADMIN DASHBOARD =================

def show_admin_dashboard():

    require_admin()

    st.title("🛡️ Admin Dashboard")
    st.write("Welcome to the system administration panel.")

    try:
        users = get_all_users()
        predictions = get_all_predictions()

    except Exception as e:
        st.error(f"Could not load dashboard data: {e}")
        return

    users_df = pd.DataFrame(users)
    predictions_df = pd.DataFrame(predictions)

    total_users = len(users_df)
    total_predictions = len(predictions_df)

    if not predictions_df.empty:
        high_risk = (
            predictions_df["risk"]
            .astype(str).str.strip().str.lower() == "high"
        ).sum()

        low_risk = (
            predictions_df["risk"]
            .astype(str).str.strip().str.lower() == "low"
        ).sum()
    else:
        high_risk = 0
        low_risk = 0

    st.markdown("""
        <style>
        .dashboard-subtitle {
            color: #527586;
            font-size: 16px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p class="dashboard-subtitle">'
        'System overview and prediction analytics</p>',
        unsafe_allow_html=True
    )

    st.subheader("📊 System Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Total Users", total_users)
    col2.metric("📋 Total Predictions", total_predictions)
    col3.metric("🔴 High Risk", int(high_risk))
    col4.metric("🟢 Low Risk", int(low_risk))

    st.divider()

    st.subheader("🧬 Disease-wise Prediction Analytics")

    if not predictions_df.empty:

        disease_counts = (
            predictions_df["condition"]
            .value_counts()
            .reindex(
                ["Diabetes", "Heart Disease", "Parkinsons"],
                fill_value=0
            )
            .rename_axis("Disease")
            .reset_index(name="Predictions")
        )

        risk_counts = pd.DataFrame({
            "Risk Level": ["High Risk", "Low Risk"],
            "Predictions": [int(high_risk), int(low_risk)]
        })

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### Predictions by Disease")

            disease_fig = px.bar(
                disease_counts,
                x="Disease",
                y="Predictions",
                color="Disease",
                text="Predictions",
                color_discrete_map={
                    "Diabetes": "#43899B",
                    "Heart Disease": "#5DA5A8",
                    "Parkinsons": "#80B8B0"
                },
                template="plotly_white"
            )

            disease_fig.update_traces(
                textposition="outside",
                textfont=dict(size=14, color="#263B4A"),
                marker_line_width=0
            )

            disease_fig.update_layout(
                height=420,
                showlegend=False,
                margin=dict(l=20, r=20, t=35, b=20),
                xaxis_title="Disease",
                yaxis_title="Number of Predictions",
                yaxis=dict(
                    rangemode="tozero",
                    gridcolor="#E5EAF0",
                    zeroline=False
                ),
                xaxis=dict(showgrid=False),
                font=dict(
                    family="Arial",
                    size=13,
                    color="#263B4A"
                ),
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(disease_fig, width="stretch")

        with chart_col2:
            st.markdown("#### Risk Distribution")

            risk_fig = px.bar(
                risk_counts,
                x="Risk Level",
                y="Predictions",
                color="Risk Level",
                text="Predictions",
                color_discrete_map={
                    "High Risk": "#D68B65",
                    "Low Risk": "#43899B"
                },
                template="plotly_white"
            )

            risk_fig.update_traces(
                textposition="outside",
                textfont=dict(size=14, color="#263B4A"),
                marker_line_width=0
            )

            risk_fig.update_layout(
                height=420,
                showlegend=False,
                margin=dict(l=20, r=20, t=35, b=20),
                xaxis_title="Risk Level",
                yaxis_title="Number of Predictions",
                yaxis=dict(
                    rangemode="tozero",
                    gridcolor="#E5EAF0",
                    zeroline=False
                ),
                xaxis=dict(showgrid=False),
                font=dict(
                    family="Arial",
                    size=13,
                    color="#263B4A"
                ),
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(risk_fig, width="stretch")

        st.divider()

        st.subheader("🕒 Recent Prediction Activity")

        recent_predictions = predictions_df.copy()

        if "timestamp" in recent_predictions.columns:
            recent_predictions = recent_predictions.sort_values(
                "timestamp",
                ascending=False
            )

        display_columns = [
            col for col in [
                "id",
                "user_id",
                "condition",
                "result",
                "risk",
                "timestamp"
            ]
            if col in recent_predictions.columns
        ]

        st.dataframe(
            recent_predictions[display_columns].head(5),
            width="stretch",
            hide_index=True
        )

    else:
        st.info("No prediction records available yet.")

    st.divider()
    st.subheader("👤 Registered Users")

    if not users_df.empty:
        st.dataframe(
            users_df.head(5),
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No registered users found.")

    st.divider()


# ================= MANAGE USERS =================

def show_manage_users():

    require_admin()

    st.subheader("👥 Manage Users")

    users = get_all_users()

    st.metric("Total Accounts", len(users))

    if not users:
        st.info("No users registered yet.")
        return

    df = pd.DataFrame(users)

    def color_status(status):
        if status == "active":
            return (
                "background-color: #D9F2E3;"
                "color: #166534;"
                "font-weight: bold;"
            )
        elif status == "frozen":
            return (
                "background-color: #DCEEFF;"
                "color: #1E40AF;"
                "font-weight: bold;"
            )
        elif status == "revoked":
            return (
                "background-color: #FEE2E2;"
                "color: #991B1B;"
                "font-weight: bold;"
            )
        return ""

    if "status" in df.columns:
        styled_df = df.style.map(
            color_status,
            subset=["status"]
        )

        st.dataframe(
            styled_df,
            width="stretch",
            hide_index=True
        )
    else:
        st.dataframe(
            df,
            width="stretch",
            hide_index=True
        )

    # PDF download
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle
    )
    from io import BytesIO

    pdf_buffer = BytesIO()

    pdf = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(A4)
    )

    table_data = [
        ["ID", "Name", "Email", "Role", "Status"]
    ]

    for user in users:
        table_data.append([
            user["id"],
            user["name"],
            user["email"],
            user["role"],
            user["status"],
        ])

    table = Table(table_data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))

    pdf.build([table])
    pdf_buffer.seek(0)

    st.download_button(
        "📄 Download User List (PDF)",
        data=pdf_buffer.getvalue(),
        file_name="user_list.pdf",
        mime="application/pdf",
    )

    st.divider()
    st.subheader("Manage Individual Accounts")

    selected_id = st.selectbox(
        "Select User ID",
        [user["id"] for user in users],
    )

    selected_user = next(
        user for user in users if user["id"] == selected_id
    )

    st.write(f"**Selected:** {selected_user['name']}")

    with st.expander("✏️ Edit User"):

        new_name = st.text_input(
            "Name",
            value=selected_user["name"],
            key="edit_name",
        )

        new_email = st.text_input(
            "Email",
            value=selected_user["email"],
            key="edit_email",
        )

        new_role = st.selectbox(
            "Role",
            ["user", "admin"],
            index=0 if selected_user["role"] == "user" else 1,
            key="edit_role",
        )

        if st.button("Save Changes"):
            success, message = update_user(
                selected_id,
                new_name,
                new_email,
                new_role
            )

            if success:
                st.session_state["user_update_message"] = message
                st.rerun()
            else:
                st.error(message)

        if "user_update_message" in st.session_state:
            st.success(st.session_state["user_update_message"])
            del st.session_state["user_update_message"]

    if selected_user["status"] == "frozen":
        st.info("❄️ Account status: FROZEN")
    elif selected_user["status"] == "revoked":
        st.error("🚫 Account status: REVOKED")
    else:
        st.success("🟢 Account status: ACTIVE")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("❄️ Freeze"):
            success, message = update_user_status(
                selected_id, "frozen"
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col2:
        if st.button("🔓 Unfreeze"):
            success, message = update_user_status(
                selected_id, "active"
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col3:
        if st.button("🚫 Revoke Access"):
            success, message = update_user_status(
                selected_id, "revoked"
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col4:
        if st.button("🔑 Grant Access"):
            success, message = update_user_status(
                selected_id, "active"
            )
            if success:
                st.success("Access granted successfully.")
                st.rerun()
            else:
                st.error(message)

    st.divider()

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this account.",
        key="confirm_delete",
    )

    if st.button("🗑️ Delete User", type="primary"):
        if confirm_delete:
            success, message = delete_user(
                selected_id,
                st.session_state.user_id
            )

            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Please confirm before deleting.")


# ================= ALL PREDICTION RECORDS =================

def show_all_predictions():

    require_admin()

    st.markdown("""
        <style>
        .prediction-count {
            background: rgba(255, 255, 255, 0.85);
            border-radius: 18px;
            padding: 22px 28px;
            margin: 18px 0;
            border: 1px solid #d8eeee;
        }

        .prediction-count-label {
            color: #31566b;
            font-size: 16px;
        }

        .prediction-count-number {
            color: #24465e;
            font-size: 42px;
            font-weight: 600;
        }

        div[data-baseweb="select"] > div,
        div[data-testid="stDateInput"] input {
            border-radius: 12px;
            background-color: #f8ffff;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("All Prediction Records")

    # Retrieve prediction records and linked patient names
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    p.id,
                    p.condition_name,
                    p.risk,
                    p.timestamp,
                    pt.name AS patient_name
                FROM predictions p
                LEFT JOIN patients pt
                    ON p.patient_id = pt.id
                ORDER BY p.timestamp DESC
            """)


            rows = cursor.fetchall()

        # Decrypt patient names before displaying them
        decrypted_rows = []

        for row in rows:
            patient_name = decrypt_text(row[4]) if row[4] else "—"

            decrypted_rows.append((
                row[0],
                row[1],
                row[2],
                row[3],
                patient_name
            ))

        predictions_df = pd.DataFrame(
            decrypted_rows,
            columns=[
                "id",
                "Disease",
                "Risk",
                "Date & Time",
                "Patient Name"
            ]
        )


    except Exception as e:
        st.error(f"Could not load prediction records: {e}")
        return

    if predictions_df.empty:
        st.info("No prediction records found.")
        return

    predictions_df["Date & Time"] = pd.to_datetime(
        predictions_df["Date & Time"],
        errors="coerce"
    )

    predictions_df["Patient Name"] = (
        predictions_df["Patient Name"].fillna("—")
    )

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        diseases = ["All"] + sorted(
            predictions_df["Disease"].dropna().unique().tolist()
        )

        selected_disease = st.selectbox(
            "Disease",
            diseases
        )

    with col2:
        risks = ["All"] + sorted(
            predictions_df["Risk"].dropna().unique().tolist()
        )

        selected_risk = st.selectbox(
            "Risk",
            risks
        )

    with col3:
        valid_dates = predictions_df["Date & Time"].dropna()

        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            selected_dates = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            selected_dates = ()

    filtered_df = predictions_df.copy()

    if selected_disease != "All":
        filtered_df = filtered_df[
            filtered_df["Disease"] == selected_disease
        ]

    if selected_risk != "All":
        filtered_df = filtered_df[
            filtered_df["Risk"] == selected_risk
        ]

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates

        filtered_df = filtered_df[
            (filtered_df["Date & Time"].dt.date >= start_date)
            & (filtered_df["Date & Time"].dt.date <= end_date)
        ]

    # Prediction count card
    st.markdown(f"""
        <div class="prediction-count">
            <div class="prediction-count-label">
                Filtered Predictions
            </div>
            <div class="prediction-count-number">
                {len(filtered_df)}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Prepare the four columns shown in the reference design
    display_df = filtered_df[
        ["Patient Name", "Disease", "Risk", "Date & Time"]
    ].copy()

    display_df["Date & Time"] = (
        display_df["Date & Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    )

    # Build a clean, borderless HTML table
    table_rows = ""

    for _, row in display_df.iterrows():
        patient_name = html.escape(str(row["Patient Name"]))
        disease = html.escape(str(row["Disease"]))
        risk = html.escape(str(row["Risk"]))
        date_time = html.escape(str(row["Date & Time"]))

        table_rows += f"""
            <tr>
                <td>{patient_name}</td>
                <td>{disease}</td>
                <td>{risk}</td>
                <td>{date_time}</td>
            </tr>
        """

    table_html = f"""
    <style>
        .records-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            color: #29465a;
            font-family: Arial, sans-serif;
            font-size: 17px;
        }}

        .records-table th {{
            text-align: left;
            font-size: 18px;
            font-weight: 600;
            padding: 12px 18px 65px 18px;
            color: #29465a;
            border: none;
            background: transparent;
        }}

        .records-table td {{
            padding: 18px;
            border: none;
            background: transparent;
            vertical-align: middle;
        }}

        .records-table tr,
        .records-table tbody,
        .records-table thead {{
            border: none;
            background: transparent;
        }}

        .records-table td:first-child,
        .records-table th:first-child {{
            padding-left: 18px;
        }}
    </style>

    <table class="records-table">
        <thead>
            <tr> 
                <th>Patient Name</th>
                <th>Disease</th>
                <th>Risk</th>
                <th>Date &amp; Time</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """

    # Render HTML instead of displaying it as code
    st.html(table_html)
