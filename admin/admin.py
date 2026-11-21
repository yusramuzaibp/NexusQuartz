
import streamlit as st
import pandas as pd

from database.database import (
    get_all_users,
    get_all_predictions,
    update_user,
    update_user_status,
    delete_user,
)

def show_admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    st.write("Welcome to the system administration panel.")

    # Fetch live database records
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

    # Calculate statistics
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

    # Dashboard styling
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

    # Statistic cards
    st.subheader("📊 System Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "👥 Total Users",
        total_users
    )

    col2.metric(
        "📋 Total Predictions",
        total_predictions
    )

    col3.metric(
        "🔴 High Risk",
        int(high_risk)
    )

    col4.metric(
        "🟢 Low Risk",
        int(low_risk)
    )

    st.divider()

    # Disease-wise analytics
    st.subheader("🧬 Disease-wise Prediction Analytics")

    if not predictions_df.empty:

        disease_counts = (
            predictions_df["condition"]
            .value_counts()
            .rename_axis("Disease")
            .reset_index(name="Predictions")
        )

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### Predictions by Disease")
            st.bar_chart(
                disease_counts.set_index("Disease"),
                color="#43899B"
            )

        with chart_col2:
            st.markdown("#### Risk Distribution")

            risk_counts = pd.DataFrame({
                "Risk Level": ["High Risk", "Low Risk"],
                "Predictions": [int(high_risk), int(low_risk)]
            })

            st.bar_chart(
                risk_counts.set_index("Risk Level"),
                color="#D68B65"
            )

        st.divider()

        # Recent prediction activity
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
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No prediction records available yet.")

    st.divider()

    # Recent registered users
    st.subheader("👤 Registered Users")

    if not users_df.empty:
        st.dataframe(
            users_df.tail(5),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No registered users found.")

    st.divider()


def show_manage_users():
    st.subheader("👥 Manage Users")

    users = get_all_users()

    st.metric("Total Accounts", len(users))

    if not users:
        st.info("No users registered yet.")
        return

    df = pd.DataFrame(users)

    st.dataframe(df, use_container_width=True, hide_index=True)

    # PDF download
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from io import BytesIO

    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4))

    table_data = [["ID", "Name", "Email", "Role", "Status"]]

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
                selected_id, new_name, new_email, new_role
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    st.write(f"**Account status:** {selected_user['status']}")

    col1, col2, col3 = st.columns(3)

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

    st.divider()

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this account.",
        key="confirm_delete",
    )

    if st.button("🗑️ Delete User", type="primary"):
        if confirm_delete:
            success, message = delete_user(selected_id)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Please confirm before deleting.")


def show_all_predictions():
    st.title("📋 All Prediction Records")
    st.write("View prediction records from all registered users.")

    predictions = get_all_predictions()

    if predictions:
        predictions_df = pd.DataFrame(predictions)

        st.metric("Total Predictions", len(predictions))

        st.dataframe(
            predictions_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No prediction records found.")
