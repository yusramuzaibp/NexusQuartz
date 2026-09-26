# -*- coding: utf-8 -*-
import os
import pickle
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

from chatbot_snippet import bot_reply, render_ai_assistant_page

from database.database import (
    create_database,
    save_prediction_to_db,
    get_user_predictions,
    clear_user_predictions
   
)
from auth.authentication import hash_password, create_user, login_user
from utils.validation import check_ranges
from dashboard import show_dashboard
# ---------------------------------------------------------------------
# page config -- must be the very first Streamlit command in the file
# ---------------------------------------------------------------------
st.set_page_config(page_title="Multiple Disease Prediction", layout="wide", page_icon="🧑‍⚕️")


# =======================================================================


# LOGIN / SIGN UP
# =======================================================================

create_database()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if not st.session_state.logged_in:

    st.markdown(
        """
        <div style="text-align:center;">
        <h1>🧑‍⚕️ Multiple Disease Prediction</h1>
        <p style="font-size:18px;">Log in or create an account to continue.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])

    with login_tab:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", placeholder="Enter your email", key="login_email")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

        if st.button("🔐 Login", use_container_width=True):
            if email == "" or password == "":
                st.warning("⚠️ Please enter your email and password.")
            else:
                user = login_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.user_name = user[1]
                    st.session_state.history = get_user_predictions(user[0])
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password.")

    with signup_tab:
        st.subheader("Create Your Account")
        name = st.text_input("Full Name", placeholder="Enter your name", key="signup_name")
        email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
        password = st.text_input("Password", type="password", placeholder="Create a password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="confirm_password")

        if st.button("📝 Create Account", use_container_width=True):
            if not name or not email or not password or not confirm_password:
                st.warning("⚠️ Please fill in all fields.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif len(password) < 6:
                st.warning("⚠️ Password must contain at least 6 characters.")
            else:
                result = create_user(name, email, password)
                if result:
                    st.success("✅ Account created successfully!")
                    st.info("You can now go to the Login tab and log in.")
                else:
                    st.error("❌ An account with this email already exists.")

    st.stop()  # nothing below this line runs until the user logs in


# =======================================================================
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
    st.session_state.history.append({
        'condition': condition,
        'result': result,
        'risk': risk,               # 'Low' or 'High'
        'timestamp': timestamp,
        'inputs': inputs,
    })
    # Persist so this shows up under "Previous Records" -- including every
    # parameter the user typed in -- even after logging out / restarting
    # the app, not just for this session.
    save_prediction_to_db(st.session_state.user_id, condition, result, risk, timestamp, inputs)

# ---------------------------------------------------------------------
# sidebar for navigation
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### 👋 Welcome, **{st.session_state.user_name}**")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_id = None
        st.rerun()
    st.divider()

    selected = option_menu('Multiple Disease Prediction System',
                            ['Dashboard',
                             'Disease Prediction',
                             'Previous Records',
                             'AI Chatbot',
                             'Find a Specialist'],
                            icons=['speedometer2', 'clipboard2-pulse',
                                   'clock-history', 'chat-dots', 'geo-alt'],
                            default_index=0)

# Dashboard
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

    st.markdown("""
        <style>
        div[data-testid="stButton"] > button {
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ===================================================================
    # STEP 1: choose which disease to predict
    # ===================================================================
    if st.session_state.disease_choice is None:

        st.title('Select Disease to Predict')
        st.write('Choose a disease category. You will be guided through the required clinical parameters.')

        cols = st.columns(3)
        for col, (name, info) in zip(cols, disease_info.items()):
            with col:
                st.markdown(f"""
                    <div style="border:2px solid #e5e7eb; border-radius:14px; padding:20px;
                                margin-bottom:10px; background:#fff; min-height:190px;">
                        <div style="font-size:26px;">{info['icon']}</div>
                        <div style="font-weight:700; font-size:16px; margin-top:10px; color:#0f172a;">{name}</div>
                        <div style="font-size:13px; color:#64748b; margin-top:6px; line-height:1.5;">{info['desc']}</div>
                        <div style="font-size:13px; color:{info['color']}; font-weight:600; margin-top:10px;">{info['params']} parameters &rsaquo;</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f'Select {name}', key=f'select_{name}', use_container_width=True):
                    st.session_state.disease_choice = name
                    st.rerun()

    # ===================================================================
    # STEP 2: show the form for the chosen disease
    # ===================================================================
    else:
        disease_choice = st.session_state.disease_choice
        info = disease_info[disease_choice]

        if st.button('← Back to disease selection'):
            st.session_state.disease_choice = None
            st.rerun()

        st.title(f'{disease_choice} Prediction')
        st.markdown('---')

        # ---------------------------------------------------------
        # Diabetes
        # ---------------------------------------------------------
        if disease_choice == 'Diabetes':

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('**Pregnancies**')
                st.caption('Number of times pregnant (0 for males)')
                Pregnancies = st.text_input('Pregnancies', placeholder='0', label_visibility='collapsed')

            with col2:
                st.markdown('**Plasma Glucose (2h OGTT)** (mg/dL)')
                Glucose = st.text_input('Glucose', placeholder='120', label_visibility='collapsed')

            with col1:
                st.markdown('**Diastolic Blood Pressure** (mmHg)')
                BloodPressure = st.text_input('BloodPressure', placeholder='72', label_visibility='collapsed')

            with col2:
                st.markdown('**Triceps Skin Fold Thickness** (mm)')
                SkinThickness = st.text_input('SkinThickness', placeholder='20', label_visibility='collapsed')

            with col1:
                st.markdown('**2-Hour Serum Insulin** (μU/mL)')
                Insulin = st.text_input('Insulin', placeholder='80', label_visibility='collapsed')

            with col2:
                st.markdown('**Body Mass Index (BMI)** (kg/m²)')
                BMI = st.text_input('BMI', placeholder='25.0', label_visibility='collapsed')

            with col1:
                st.markdown('**Diabetes Pedigree Function**')
                st.caption('Family history diabetes score')
                DiabetesPedigreeFunction = st.text_input('DPF', placeholder='0.47', label_visibility='collapsed')

            with col2:
                st.markdown('**Age** (years)')
                Age = st.text_input('Age', placeholder='35', label_visibility='collapsed')

            diab_diagnosis = ''

            if st.button('Diabetes Test Result'):
                user_input = [Pregnancies, Glucose, BloodPressure, SkinThickness,
                              Insulin, BMI, DiabetesPedigreeFunction, Age]

                if '' in user_input:
                    st.warning('Please fill in all fields before predicting.')
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

                            if diab_prediction[0] == 1:
                                diab_diagnosis = 'The person is Diabetic'
                                log_prediction('Diabetes', diab_diagnosis, 'High', inputs_dict)
                            else:
                                diab_diagnosis = 'The person is Not Diabetic'
                                log_prediction('Diabetes', diab_diagnosis, 'Low', inputs_dict)

                            st.success(diab_diagnosis)
                    except ValueError:
                        st.error('Please enter valid numeric values in all fields.')

        # ---------------------------------------------------------
        # Heart Disease
        # ---------------------------------------------------------
        elif disease_choice == 'Heart Disease':

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('**Age** (years)')
                age = st.text_input('age', placeholder='54', label_visibility='collapsed')

            with col2:
                st.markdown('**Sex**')
                st.caption('1 = male, 0 = female')
                sex = st.text_input('sex', placeholder='1', label_visibility='collapsed')

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
                user_input = [age, sex, cp, trestbps, chol, fbs, restecg,
                              thalach, exang, oldpeak, slope, ca, thal]

                if '' in user_input:
                    st.warning('Please fill in all fields before predicting.')
                else:
                    try:
                        user_input = [float(x) for x in user_input]

                        range_specs = [
                            ("Age", 1, 120),
                            ("Sex", 0, 1),
                            ("Chest Pain Type", 0, 3),
                            ("Resting Blood Pressure", 60, 250),
                            ("Cholesterol", 100, 600),
                            ("Fasting Blood Sugar", 0, 1),
                            ("Resting ECG", 0, 2),
                            ("Max Heart Rate", 60, 220),
                            ("Exercise Induced Angina", 0, 1),
                            ("ST Depression", 0, 10),
                            ("Slope", 0, 2),
                            ("Major Vessels (ca)", 0, 3),
                            ("Thalassemia", 1, 3),
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

            if st.button("Parkinson's Test Result"):
                user_input = [fo, fhi, flo, Jitter_percent, Jitter_Abs,
                              RAP, PPQ, DDP, Shimmer, Shimmer_dB, APQ3, APQ5,
                              APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE]

                if '' in user_input:
                    st.warning('Please fill in all fields before predicting.')
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

                            if parkinsons_prediction[0] == 1:
                                parkinsons_diagnosis = "The person has Parkinson's disease"
                                log_prediction('Parkinsons', parkinsons_diagnosis, 'High', inputs_dict)
                            else:
                                parkinsons_diagnosis = "The person does not have Parkinson's disease"
                                log_prediction('Parkinsons', parkinsons_diagnosis, 'Low', inputs_dict)

                            st.success(parkinsons_diagnosis)
                    except ValueError:
                        st.error('Please enter valid numeric values in all fields.')


# ---------------------------------------------------------------------
# Previous Records Page
# ---------------------------------------------------------------------
if selected == 'Previous Records':

    st.title('Previous Records')
    st.write("Your full prediction history, saved to your account so it's here even after you log out.")

    records = get_user_predictions(st.session_state.user_id)

    if not records:
        st.info("No predictions yet. Head to **Disease Prediction** to run your first test.")
    else:
        # Flatten each record: the prediction summary plus every clinical
        # input that was entered for it (BMI, Glucose, Pregnancies... for
        # Diabetes; age, cp, chol... for Heart Disease; fo, jitter... for
        # Parkinson's). Different diseases have different parameters, so
        # columns that don't apply to a given row are simply left blank.
        flat_rows = []
        for r in records:
            row = {
                'Condition': r['condition'],
                'Result': r['result'],
                'Risk': r['risk'],
                'Date & Time': r['timestamp'],
            }
            row.update(r['inputs'])
            flat_rows.append(row)

        df_full = pd.DataFrame(flat_rows)
        summary_cols = ['Condition', 'Result', 'Risk', 'Date & Time']

        col1, col2 = st.columns(2)
        with col1:
            condition_filter = st.multiselect(
                'Filter by condition',
                options=sorted(df_full['Condition'].unique()),
                default=sorted(df_full['Condition'].unique()),
            )
        with col2:
            risk_filter = st.multiselect(
                'Filter by risk level',
                options=sorted(df_full['Risk'].unique()),
                default=sorted(df_full['Risk'].unique()),
            )

        filtered = df_full[
            df_full['Condition'].isin(condition_filter)
            & df_full['Risk'].isin(risk_filter)
        ]

        show_inputs = st.checkbox(
            'Show all input parameters in the table (BMI, Glucose, Pregnancies, etc.)'
        )

        st.markdown(f"**{len(filtered)}** record(s) found.")

        st.dataframe(
            filtered if show_inputs else filtered[summary_cols],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            '⬇️ Download full history as CSV (includes all input parameters)',
            data=filtered.to_csv(index=False),
            file_name='prediction_history_full.csv',
            mime='text/csv',
        )

        st.markdown('---')
        with st.expander('⚠️ Danger zone'):
            st.warning('This permanently deletes all of your saved prediction history. This cannot be undone.')
            if st.button('Clear all my records'):
                clear_user_predictions(st.session_state.user_id)
                st.session_state.history = []
                st.success('Your prediction history has been cleared.')
                st.rerun()


# ---------------------------------------------------------------------
# AI Chatbot Page
# ---------------------------------------------------------------------
if selected == 'AI Chatbot':
    render_ai_assistant_page()


# ---------------------------------------------------------------------
# Find a Specialist Page
# ---------------------------------------------------------------------
if selected == 'Find a Specialist':
    st.title('Find a Specialist')
    st.write(
        "If a prediction came back **High Risk**, it's a good idea to "
        "follow up with the right kind of doctor. Here's a quick guide:"
    )

    specialists = {
        'Diabetes': 'Endocrinologist',
        'Heart Disease': 'Cardiologist',
        'Parkinsons': 'Neurologist',
    }
    for condition, specialist in specialists.items():
        st.markdown(f"- **{condition}** → {specialist}")

    st.info(
        "This is a placeholder page — plug in a real directory, clinic "
        "locator API, or contact list here when you're ready."
    )
