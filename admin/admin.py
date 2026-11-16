
import streamlit as st
import pandas as pd

from database.database import get_all_users, get_all_predictions


def show_admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    st.write("Welcome to the system administration panel.")
    st.info("User management and prediction record management will be added here.")


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
