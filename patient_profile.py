
import streamlit as st
import pandas as pd

from database.database import get_patients, get_user_predictions


def render_patient_profile():
    st.title("👤 Patient Profile")

    patient_id = st.session_state.get("patient_profile_id")

    if patient_id is None:
        st.info("Please register or select a patient to view their profile.")
        return

    doctor_id = st.session_state.user_id
    patients = get_patients(doctor_id)

    patient = next(
        (p for p in patients if p["id"] == patient_id),
        None,
    )

    if patient is None:
        st.error("Patient not found.")
        return

    st.subheader(patient["name"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Patient Code", patient["patient_code"])
    col2.metric("Age", patient["age"])
    col3.metric("Gender", patient["sex"])

    st.divider()

    st.subheader("Disease Tests")

    st.write(
        "Choose Disease Prediction from the sidebar to run a test. "
        "We will connect this profile to the prediction workflow next."
    )

    st.divider()

    st.subheader("Previous Prediction Results")

    predictions = get_user_predictions(doctor_id)

    if predictions:
        st.info(
            "Your prediction history is available. "
            "Patient-specific filtering will be connected next."
        )
    else:
        st.info("No prediction records found yet.")
