
import streamlit as st
import pandas as pd

from database.database import get_all_users, get_all_predictions


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

    # Quick navigation information
    st.subheader("⚙️ Administration")

    quick_col1, quick_col2 = st.columns(2)

    with quick_col1:
        st.info(
            "👥 **Manage Users**\n\n"
            "View all registered accounts and download user records."
        )

    with quick_col2:
        st.info(
            "📋 **Prediction Records**\n\n"
            "Monitor prediction history across all registered users."
        )


def show_manage_users():
    st.title("👥 Manage Users")
    st.write("View all registered accounts in the system.")

    users = get_all_users()

    if users:
        users_df = pd.DataFrame(users)

        st.metric("Total Registered Accounts", len(users))

        st.dataframe(
            users_df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = users_df.to_csv(index=False)

        st.download_button(
            "⬇️ Download User List",
            data=csv_data,
            file_name="registered_users.csv",
            mime="text/csv"
        )
    else:
        st.info("No registered accounts found.")


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
