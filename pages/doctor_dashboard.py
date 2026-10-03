import streamlit as st


def show_doctor_dashboard():

    st.title("👨‍⚕️ Doctor Dashboard")

    st.write(
        f"Welcome, Dr. {st.session_state.user_name}"
    )

    st.divider()

    st.subheader("Patient Profiles")

    st.info(
        "Patient profiles will appear here."
    )