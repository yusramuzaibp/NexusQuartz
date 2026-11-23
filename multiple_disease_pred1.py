# -*- coding: utf-8 -*-
import os
import pickle
from datetime import datetime

from ui.styles import apply_global_styles
from ui.authui import show_auth_page
from ui.navigation import show_navigation
from ui.disease_prediction_ui import (
    render_disease_selection,
    render_disease_form_header,
    render_back_button,
    render_patient_details,
    render_disease_parameters_header,
    render_prediction_button,
    load_css,
)

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

from chatbot_snippet import render_ai_assistant_page

from database.database import (
    create_database,
    save_prediction_to_db,
    get_user_predictions,
    get_all_users,
    get_all_predictions,
    get_or_create_patient,
)
from auth.authentication import (
    create_user,
    login_user,
    validate_password,
)
from utils.validation import check_ranges
from dashboard import show_dashboard

from app_modules.patient_reports import show_patient_reports
from app_modules.find_specialist import show_find_specialist
from app_modules.profile import show_profile
from admin.admin import (
    show_admin_dashboard,
    show_manage_users,
    show_all_predictions,
)

def only_digits(key):
    value = st.session_state.get(key, "")
    st.session_state[key] = "".join(
        ch for ch in value if ch.isdigit()
    )
# ---------------------------------------------------------------------
# page config -- must be the very first Streamlit command in the file
# ---------------------------------------------------------------------
load_css()
st.set_page_config(page_title="Multiple Disease Prediction", layout="wide", page_icon="🧑‍⚕️")
# =======================================================================
# LOGIN / SIGN UP
# =======================================================================
@st.cache_resource
def initialize_database():
    create_database()

initialize_database()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if not st.session_state.logged_in:

    show_auth_page()
    st.stop()
#==============================================
# EVERYTHING BELOW ONLY RUNS AFTER A SUCCESSFUL LOGIN
# =======================================================================

# ---------------------------------------------------------------------
# loading the saved models
# Path is relative to this file's location, so it works on any machine
# and on Streamlit Community Cloud, not just your local PC.
# ---------------------------------------------------------------------
working_dir = os.path.dirname(os.path.abspath(__file__))

diabetes_model = pickle.load(open(f'{working_dir}/saved_models/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open(f'{working_dir}/saved_models/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open(f'{working_dir}/saved_models/parkinsons_model.sav', 'rb'))
# ---------------------------------------------------------------------
# session state: keeps a running log of predictions for the Dashboard
# (resets when the app restarts — swap for a CSV/DB write if you want
# history to persist across sessions)
# ---------------------------------------------------------------------
if 'history' not in st.session_state:
    st.session_state.history = []  # each entry: {condition, result, risk, timestamp}

def log_prediction(condition, result, risk, inputs=None):
    inputs = inputs or {}
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    patient_id = st.session_state.get("selected_patient_id")
    patient_details = st.session_state.get("patient_details", {})

    inputs["Patient Name"] = patient_details.get("name", "")
    inputs["Patient Age"] = patient_details.get("age", "")
    inputs["Patient Gender"] = patient_details.get("gender", "")
    inputs["Contact Number"] = patient_details.get("contact", "")

    st.session_state.history.append({
        'condition': condition,
        'result': result,
        'risk': risk,
        'timestamp': timestamp,
        'inputs': inputs,
        'patient_id': patient_id,
    })

    save_prediction_to_db(
        st.session_state.user_id,
        condition,
        result,
        risk,
        timestamp,
        inputs,
        patient_id=patient_id,
    )
# ---------------------------------------------------------------------
# Apply global application styling
apply_global_styles()

# Sidebar Navigation
selected = show_navigation()

# ================= PROFILE PAGE =================
if selected == "Profile":
    show_profile()
    st.stop()
# ---------------------------------------------------------------------
# Admin pages
# ---------------------------------------------------------------------
if selected == "Admin Dashboard":
    show_admin_dashboard()

elif selected == "Manage Users":
    show_manage_users()

elif selected == "All Prediction Records":
    show_all_predictions()

# ---------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------
if selected == 'Dashboard':
    show_dashboard()
# ---------------------------------------------------------------------
# Disease Prediction Page (Diabetes / Heart Disease / Parkinsons)
# ---------------------------------------------------------------------
if selected == 'Disease Prediction':

    if 'disease_choice' not in st.session_state:
        st.session_state.disease_choice = None

    disease_info = {
        'Diabetes': {
            'icon': '🩸',
            'desc': 'Predicts likelihood of Type 2 Diabetes based on clinical and lifestyle parameters.',
            'params': 8,
            'color': '#4f46e5',
        },
        'Heart Disease': {
            'icon': '❤️',
            'desc': 'Assesses cardiovascular disease risk using clinical and ECG-based features.',
            'params': 13,
            'color': '#dc2626',
        },
        'Parkinsons': {
            'icon': '🧠',
            'desc': "Detects Parkinson's disease using vocal/biomedical voice measurements.",
            'params': 22,
            'color': '#7c3aed',
        },
    }

    # ===================================================================
    # STEP 1: choose which disease to predict
    # ===================================================================
    if st.session_state.disease_choice is None:

        selected_disease = render_disease_selection(disease_info)

        if selected_disease:
            st.session_state.disease_choice = selected_disease
            st.rerun()
    # ===================================================================
    # STEP 2: show the form for the chosen disease
    # ===================================================================
    else:
        disease_choice = st.session_state.disease_choice
        info = disease_info[disease_choice]

        if render_back_button():
            st.session_state.disease_choice = None
            st.rerun()
        render_disease_form_header(disease_choice)

        # ---------------------------------------------------------
        # Diabetes
        # ---------------------------------------------------------
        if disease_choice == 'Diabetes':

            patient_name, patient_age, patient_gender, patient_contact = render_patient_details(only_digits,"diabetes_contact")

            render_disease_parameters_header("Diabetes")

            st.session_state.patient_details = {
                "name": patient_name,
                "age": patient_age,
                "gender": patient_gender,
                "contact": patient_contact,
            }

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('**Pregnancies**')
                st.caption('Number of times pregnant (0 for males)')
                Pregnancies = st.text_input('Pregnancies', placeholder='0', label_visibility='collapsed')

            with col2:
                st.markdown('**Glucose Level**')
                Glucose = st.text_input('Glucose', placeholder='120', label_visibility='collapsed')

            with col1:
                st.markdown('**Blood Pressure value**')
                BloodPressure = st.text_input('BloodPressure', placeholder='72', label_visibility='collapsed')

            with col2:
                st.markdown('**Skin Thickness value**')
                SkinThickness = st.text_input('SkinThickness', placeholder='20', label_visibility='collapsed')

            with col1:
                st.markdown('**Insulin Level**')
                Insulin = st.text_input('Insulin', placeholder='80', label_visibility='collapsed')

            with col2:
                st.markdown('**BMI value**')
                BMI = st.text_input('BMI', placeholder='25.0', label_visibility='collapsed')

            with col1:
                st.markdown('**Diabetes Pedigree Function**')
                st.caption('Family history diabetes score')
                DiabetesPedigreeFunction = st.text_input('DPF', placeholder='0.47', label_visibility='collapsed')

            with col2:
                st.markdown("**Age** (years)")
                Age = str(patient_age) if patient_age is not None else ""
                st.text_input(
                    'Age',
                    value=Age,
                    disabled=True,
                    label_visibility='collapsed'
                )

            diab_diagnosis = ''

            if render_prediction_button("Diabetes"):
                user_input = [Pregnancies, Glucose, BloodPressure, SkinThickness,
                              Insulin, BMI, DiabetesPedigreeFunction, Age]

                if (
                    '' in user_input
                    or not patient_name.strip()
                    or patient_age is None
                    or patient_gender == "Select Gender"
                    or not patient_contact.strip()
                    or len(patient_contact) != 10
                ):
                    st.warning("Please complete all patient details and health parameters.")
                else:
                    try:
                        user_input = [float(x) for x in user_input]

                        range_specs = [
                            ("Pregnancies", 0, 20),
                            ("Glucose", 40, 300),
                            ("Blood Pressure", 40, 200),
                            ("Skin Thickness", 5, 100),
                            ("Insulin", 5, 900),
                            ("BMI", 10, 70),
                            ("Diabetes Pedigree Function", 0.05, 3.0),
                            ("Age", 1, 120),
                        ]
                        problems = check_ranges(user_input, range_specs)

                        if problems:
                            st.warning(
                                "Some values look unusual — please double-check "
                                "before predicting:\n" + "\n".join(problems)
                            )
                        else:

                            diab_prediction = diabetes_model.predict([user_input])
                            input_labels = [label for label, _, _ in range_specs]
                            inputs_dict = dict(zip(input_labels, user_input))

                            risk_pct = None
                            if hasattr(diabetes_model, 'predict_proba'):
                                risk_pct = round(diabetes_model.predict_proba([user_input])[0][1] * 100, 1)

                            is_diabetic = diab_prediction[0] == 1
                            verdict = 'Diabetic' if is_diabetic else 'Not Diabetic'
                            diab_diagnosis = f'The person is {verdict}'
                            if risk_pct is not None:
                                diab_diagnosis += f' ({risk_pct}% estimated risk)'

                            # Save or retrieve the patient record
                            patient_id = get_or_create_patient(
                                doctor_id=st.session_state.user_id,
                                name=patient_name.strip(),
                                age=int(patient_age),
                                sex=patient_gender,
                                contact=patient_contact.strip()
                            )

                            # Store the selected patient ID for this prediction
                            st.session_state.selected_patient_id = patient_id

                            log_prediction('Diabetes', diab_diagnosis, 'High' if is_diabetic else 'Low', inputs_dict)
                            st.success(diab_diagnosis)
                            if risk_pct is not None:
                                st.progress(risk_pct / 100)


                    except ValueError:
                        st.error('Please enter valid numeric values in all fields.')

        # ---------------------------------------------------------
        # Heart Disease
        # ---------------------------------------------------------
        elif disease_choice == 'Heart Disease':
            patient_name, patient_age, patient_gender, patient_contact = render_patient_details(
                only_digits, "heart_contact"
            )

            render_disease_parameters_header("Heart Disease")

            st.session_state.patient_details = {
                "name": patient_name,
                "age": patient_age,
                "gender": patient_gender,
                "contact": patient_contact,
            }

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Age** (years)")
                age = str(patient_age) if patient_age is not None else ""
                st.text_input(
                    'age',
                    value=age,
                    disabled=True,
                    label_visibility='collapsed'
                )

            with col2:
                st.markdown("**Gender**")
                st.caption('1 = male, 0 = female')

                gender = (
                    "1" if patient_gender == "Male"
                    else "0" if patient_gender == "Female"
                    else ""
                )

                st.text_input(
                    'gender',
                    value=gender,
                    disabled=True,
                    label_visibility='collapsed'
                )

            with col1:
                st.markdown('**Chest Pain Type**')
                st.caption('0–3 scale')
                cp = st.text_input('cp', placeholder='0', label_visibility='collapsed')

            with col2:
                st.markdown('**Resting Blood Pressure** (mmHg)')
                trestbps = st.text_input('trestbps', placeholder='130', label_visibility='collapsed')

            with col1:
                st.markdown('**Serum Cholesterol** (mg/dL)')
                chol = st.text_input('chol', placeholder='246', label_visibility='collapsed')

            with col2:
                st.markdown('**Fasting Blood Sugar**')
                st.caption('1 if > 120 mg/dL, else 0')
                fbs = st.text_input('fbs', placeholder='0', label_visibility='collapsed')

            with col1:
                st.markdown('**Resting ECG Results**')
                st.caption('0–2 scale')
                restecg = st.text_input('restecg', placeholder='1', label_visibility='collapsed')

            with col2:
                st.markdown('**Maximum Heart Rate Achieved**')
                thalach = st.text_input('thalach', placeholder='150', label_visibility='collapsed')

            with col1:
                st.markdown('**Exercise Induced Angina**')
                st.caption('1 = yes, 0 = no')
                exang = st.text_input('exang', placeholder='0', label_visibility='collapsed')

            with col2:
                st.markdown('**ST Depression (Exercise)**')
                oldpeak = st.text_input('oldpeak', placeholder='1.0', label_visibility='collapsed')

            with col1:
                st.markdown('**Slope of Peak Exercise ST**')
                st.caption('0–2 scale')
                slope = st.text_input('slope', placeholder='1', label_visibility='collapsed')


            with col2:
                st.markdown('**Major Vessels Colored (Fluoroscopy)**')
                st.caption('0–3')
                ca = st.text_input('ca', placeholder='0', label_visibility='collapsed')

            with col1:
                st.markdown('**Thalassemia**')
                st.caption('0 = normal, 1 = fixed defect, 2 = reversible defect')
                thal = st.text_input('thal', placeholder='2', label_visibility='collapsed')

            heart_diagnosis = ''

            if st.button('Heart Disease Test Result'):
                user_input = [age, gender, cp, trestbps, chol, fbs, restecg,
                              thalach, exang, oldpeak, slope, ca, thal]

                if (
                    '' in user_input
                    or not patient_name.strip()
                    or patient_age is None
                    or patient_gender == "Select Gender"
                    or patient_gender == "Other"
                    or not patient_contact.strip()
                    or len(patient_contact) != 10

                ):
                    st.warning("Please complete all patient details and health parameters.")
                else:
                    try:
                        user_input = [float(x) for x in user_input]

                        range_specs = [
                            ("Age", 1, 120),
                            ("Gender", 0, 1),
                            ("Chest Pain Type", 0, 3),
                            ("Resting Blood Pressure", 60, 250),
                            ("Cholesterol", 100, 600),
                            ("Fasting Blood Sugar", 0, 1),
                            ("Resting ECG", 0, 2),
                            ("Max Heart Rate", 60, 220),
                            ("Exercise Induced Angina", 0, 1),
                            ("ST Depression", 0, 10),
                            ("Slope", 0, 2),
                            ("Major Vessels (ca)", 0, 4),
                            ("Thalassemia", 0, 3),
                        ]
                        problems = check_ranges(user_input, range_specs)

                        if problems:
                            st.warning(
                                "Some values look unusual — please double-check "
                                "before predicting:\n" + "\n".join(problems)
                            )
                        else:
                            heart_prediction = heart_disease_model.predict([user_input])
                            heart_proba = heart_disease_model.predict_proba([user_input])[0][1]
                            risk_pct = round(heart_proba * 100, 1)
                            input_labels = [label for label, _, _ in range_specs]
                            inputs_dict = dict(zip(input_labels, user_input))

                            # Save or retrieve the patient record
                            patient_id = get_or_create_patient(
                                doctor_id=st.session_state.user_id,
                                name=patient_name.strip(),
                                age=int(patient_age),
                                sex=patient_gender,
                                contact=patient_contact.strip()
                            )

                            st.session_state.selected_patient_id = patient_id
                            if heart_prediction[0] == 1:
                                heart_diagnosis = f'The person has a {risk_pct}% risk of Heart Disease (High Risk)'
                                log_prediction('Heart Disease', heart_diagnosis, 'High', inputs_dict)
                            else:
                                heart_diagnosis = f'The person has a {risk_pct}% risk of Heart Disease (Low Risk)'
                                log_prediction('Heart Disease', heart_diagnosis, 'Low', inputs_dict)

                            st.success(heart_diagnosis)
                            st.progress(heart_proba)
                    except ValueError:
                        st.error('Please enter valid numeric values in all fields.')

        # ---------------------------------------------------------
        # Parkinson's
        # ---------------------------------------------------------
        elif disease_choice == 'Parkinsons':
            patient_name, patient_age, patient_gender, patient_contact = render_patient_details(
                only_digits, "parkinsons_contact"
            )

            render_disease_parameters_header("Parkinson's")

            st.session_state.patient_details = {
                "name": patient_name,
                "age": patient_age,
                "gender": patient_gender,
                "contact": patient_contact,
            }


            col1, col2 = st.columns(2)

            with col1:
                st.markdown('**MDVP:Fo(Hz)**')
                st.caption('Average vocal fundamental frequency')
                fo = st.text_input('fo', placeholder='150.0', label_visibility='collapsed')

            with col2:
                st.markdown('**MDVP:Fhi(Hz)**')
                st.caption('Maximum vocal fundamental frequency')
                fhi = st.text_input('fhi', placeholder='180.0', label_visibility='collapsed')

            with col1:
                st.markdown('**MDVP:Flo(Hz)**')
                st.caption('Minimum vocal fundamental frequency')
                flo = st.text_input('flo', placeholder='110.0', label_visibility='collapsed')

            with col2:
                st.markdown('**MDVP:Jitter(%)**')
                Jitter_percent = st.text_input('jitter_pct', placeholder='0.005', label_visibility='collapsed')

            with col1:
                st.markdown('**MDVP:Jitter(Abs)**')
                Jitter_Abs = st.text_input('jitter_abs', placeholder='0.00003', label_visibility='collapsed')

            with col2:
                st.markdown('**MDVP:RAP**')
                RAP = st.text_input('rap', placeholder='0.003', label_visibility='collapsed')

            with col1:
                st.markdown('**MDVP:PPQ**')
                PPQ = st.text_input('ppq', placeholder='0.003', label_visibility='collapsed')

            with col2:
                st.markdown('**Jitter:DDP**')
                DDP = st.text_input('ddp', placeholder='0.009', label_visibility='collapsed')

            with col1:
                st.markdown('**MDVP:Shimmer**')
                Shimmer = st.text_input('shimmer', placeholder='0.03', label_visibility='collapsed')

            with col2:
                st.markdown('**MDVP:Shimmer(dB)**')
                Shimmer_dB = st.text_input('shimmer_db', placeholder='0.3', label_visibility='collapsed')

            with col1:
                st.markdown('**Shimmer:APQ3**')
                APQ3 = st.text_input('apq3', placeholder='0.015', label_visibility='collapsed')

            with col2:
                st.markdown('**Shimmer:APQ5**')
                APQ5 = st.text_input('apq5', placeholder='0.018', label_visibility='collapsed')

            with col1:
                st.markdown('**MDVP:APQ**')
                APQ = st.text_input('apq', placeholder='0.024', label_visibility='collapsed')

            with col2:
                st.markdown('**Shimmer:DDA**')
                DDA = st.text_input('dda', placeholder='0.045', label_visibility='collapsed')

            with col1:
                st.markdown('**NHR**')
                st.caption('Noise-to-harmonics ratio')
                NHR = st.text_input('nhr', placeholder='0.02', label_visibility='collapsed')

            with col2:
                st.markdown('**HNR**')
                st.caption('Harmonics-to-noise ratio')
                HNR = st.text_input('hnr', placeholder='21.0', label_visibility='collapsed')

            with col1:
                st.markdown('**RPDE**')
                st.caption('Nonlinear dynamical complexity measure')
                RPDE = st.text_input('rpde', placeholder='0.5', label_visibility='collapsed')

            with col2:
                st.markdown('**DFA**')
                st.caption('Signal fractal scaling exponent')
                DFA = st.text_input('dfa', placeholder='0.7', label_visibility='collapsed')

            with col1:
                st.markdown('**spread1**')
                spread1 = st.text_input('spread1', placeholder='-5.5', label_visibility='collapsed')

            with col2:
                st.markdown('**spread2**')
                spread2 = st.text_input('spread2', placeholder='0.2', label_visibility='collapsed')

            with col1:
                st.markdown('**D2**')
                st.caption('Nonlinear dynamical complexity measure')
                D2 = st.text_input('d2', placeholder='2.3', label_visibility='collapsed')

            with col2:
                st.markdown('**PPE**')
                st.caption('Nonlinear measure of frequency variation')
                PPE = st.text_input('ppe', placeholder='0.2', label_visibility='collapsed')

            parkinsons_diagnosis = ''

            if render_prediction_button("Parkinsons"):
                user_input = [fo, fhi, flo, Jitter_percent, Jitter_Abs,
                              RAP, PPQ, DDP, Shimmer, Shimmer_dB, APQ3, APQ5,
                              APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE]

                if (
                    '' in user_input
                    or not patient_name.strip()
                    or patient_age is None
                    or patient_gender == "Select Gender"
                    or not patient_contact.strip()
                    or len(patient_contact) != 10

                ):
                    st.warning("Please complete all patient details and health parameters.")
                else:
                    try:
                        user_input = [float(x) for x in user_input]

                        range_specs = [
                            ("MDVP:Fo(Hz)", 60, 320),
                            ("MDVP:Fhi(Hz)", 80, 650),
                            ("MDVP:Flo(Hz)", 50, 260),
                            ("MDVP:Jitter(%)", 0.0005, 0.05),
                            ("MDVP:Jitter(Abs)", 0.000005, 0.0005),
                            ("MDVP:RAP", 0.0002, 0.03),
                            ("MDVP:PPQ", 0.0002, 0.03),
                            ("Jitter:DDP", 0.0005, 0.09),
                            ("MDVP:Shimmer", 0.003, 0.16),
                            ("MDVP:Shimmer(dB)", 0.03, 1.6),
                            ("Shimmer:APQ3", 0.001, 0.08),
                            ("Shimmer:APQ5", 0.001, 0.10),
                            ("MDVP:APQ", 0.002, 0.18),
                            ("Shimmer:DDA", 0.005, 0.20),
                            ("NHR", 0.0001, 0.40),
                            ("HNR", 5, 38),
                            ("RPDE", 0.15, 0.75),
                            ("DFA", 0.40, 0.90),
                            ("spread1", -9, -1.5),
                            ("spread2", 0, 0.60),
                            ("D2", 1.0, 4.2),
                            ("PPE", 0.02, 0.65),
                        ]
                        problems = check_ranges(user_input, range_specs)

                        if problems:
                            st.warning(
                                "Some values look unusual — please double-check "
                                "before predicting:\n" + "\n".join(problems)
                            )
                        else:

                            parkinsons_prediction = parkinsons_model.predict([user_input])
                            input_labels = [label for label, _, _ in range_specs]
                            inputs_dict = dict(zip(input_labels, user_input))

                            risk_pct = None
                            if hasattr(parkinsons_model, 'predict_proba'):
                                risk_pct = round(parkinsons_model.predict_proba([user_input])[0][1] * 100, 1)

                            # Save or retrieve the patient record
                            patient_id = get_or_create_patient(
                                doctor_id=st.session_state.user_id,
                                name=patient_name.strip(),
                                age=int(patient_age),
                                sex=patient_gender,
                                contact=patient_contact.strip()
                            )

                            st.session_state.selected_patient_id = patient_id
                            has_pd = parkinsons_prediction[0] == 1
                            parkinsons_diagnosis = ("The person has Parkinson's disease" if has_pd
                                                    else "The person does not have Parkinson's disease")
                            if risk_pct is not None:
                                parkinsons_diagnosis += f' ({risk_pct}% estimated risk)'

                            log_prediction('Parkinsons', parkinsons_diagnosis, 'High' if has_pd else 'Low', inputs_dict)
                            st.success(parkinsons_diagnosis)
                            if risk_pct is not None:
                                st.progress(risk_pct / 100)

                    except ValueError as e:
                        st.error(f'Invalid value: {e}')
# ---------------------------------------------------------------------
# Patient Reports Page
# ---------------------------------------------------------------------
if selected == 'Patient Reports':
    show_patient_reports()
# ---------------------------------------------------------------------
# AI Chatbot Page
# ---------------------------------------------------------------------
if selected == 'AI Chatbot':
    render_ai_assistant_page()
# ---------------------------------------------------------------------
# Find a Specialist Page
# ---------------------------------------------------------------------
if selected == 'Find a Specialist':
    show_find_specialist()
