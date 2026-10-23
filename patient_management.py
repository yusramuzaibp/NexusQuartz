
import streamlit as st
import pandas as pd

from database.database import create_patient, get_patients


def render_patient_management():
    st.title("👥 Patient Management")
    st.write("Register new patients or view existing patients.")

    user_id = st.session_state.user_id

    st.subheader("Register a New Patient")

    with st.form("register_patient_form"):
        patient_code = st.text_input("Patient Code")
        patient_name = st.text_input("Patient Name")
        patient_age = st.number_input(
            "Age", min_value=1, max_value=120, value=18
        )
        patient_gender = st.selectbox(
            "Gender", ["Male", "Female"]
        )

        register_clicked = st.form_submit_button("Register Patient")

        if register_clicked:
            if not patient_code.strip() or not patient_name.strip():
                st.error("Please enter both patient code and patient name.")
            else:
                success, message = create_patient(
                    doctor_id=user_id,
                    patient_code=patient_code,
                    name=patient_name,
                    age=int(patient_age),
                    sex=patient_gender,
                )

                if success:
                    patients = get_patients(user_id)
                    new_patient = next(
                        (
                            patient for patient in patients
                            if patient["patient_code"] == patient_code.strip()
                        ),
                        None,
                    )

                    if new_patient:
                        st.session_state.selected_patient_id = new_patient["id"]
                        st.session_state.disease_choice = None
                        st.session_state.page = "Disease Prediction"
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    st.divider()
    st.subheader("Existing Patients")

    patients = get_patients(user_id)

    if patients:
        patients_df = pd.DataFrame(patients)
        st.dataframe(
            patients_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No patients registered yet.")
