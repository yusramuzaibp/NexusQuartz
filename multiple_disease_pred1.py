# -*- coding: utf-8 -*-
import pickle
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu


# ---------------------------------------------------------------------
# loading the saved models
# NOTE: double-check this path matches your actual folder name.
# ---------------------------------------------------------------------
diabetes_model = pickle.load(open('C:/Users/malha/OneDrive/Desktop/Multiple disease Prediction/saved model/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open('C:/Users/malha/OneDrive/Desktop/Multiple disease Prediction/saved model/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open('C:/Users/malha/OneDrive/Desktop/Multiple disease Prediction/saved model/parkinsons_model.sav', 'rb'))


# ---------------------------------------------------------------------
# session state: keeps a running log of predictions for the Dashboard
# (resets when the app restarts — swap for a CSV/DB write if you want
# history to persist across sessions)
# ---------------------------------------------------------------------
if 'history' not in st.session_state:
    st.session_state.history = []  # each entry: {condition, result, risk, timestamp}


def log_prediction(condition, result, risk):
    st.session_state.history.append({
        'condition': condition,
        'result': result,
        'risk': risk,               # 'Low' or 'High'
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })


# ---------------------------------------------------------------------
# sidebar for navigation
# ---------------------------------------------------------------------
with st.sidebar:
    selected = option_menu('Multiple Disease Prediction System',
                            ['Dashboard',
                             'Disease Prediction',
                             'AI chatbot',
                             'Hospital and Specialist'
                             'settings'],
                            icons=['speedometer2', 'clipboard2-pulse', 'chat-dots'],
                            default_index=0)


# ---------------------------------------------------------------------
# Dashboard Page
# ---------------------------------------------------------------------
if selected == 'Dashboard':

    st.title('Dashboard')
    st.write("Here's an overview of your recent prediction activity.")

    history = st.session_state.history
    df = pd.DataFrame(history)

    total = len(history)
    diabetes_count = len(df[df['condition'] == 'Diabetes']) if total else 0
    heart_count = len(df[df['condition'] == 'Heart Disease']) if total else 0
    parkinsons_count = len(df[df['condition'] == 'Parkinsons']) if total else 0
    high_risk_count = len(df[df['risk'] == 'High']) if total else 0

    # ---- stat cards ----
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Predictions', total)
    col2.metric('Diabetes Tests', diabetes_count)
    col3.metric('Heart Disease Tests', heart_count)
    col4.metric('Parkinsons Tests', parkinsons_count)

    st.markdown('---')

    # ---- recent health activity (single self-contained HTML block) ----
    if total:
        recent = df.sort_values('timestamp', ascending=False).head(10)
        table_rows = ""
        for _, row in recent.iterrows():
            try:
                date_str = datetime.strptime(
                    row['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
            except ValueError:
                date_str = row['timestamp']
            pill_class = 'rha-pill-high' if row['risk'] == 'High' else 'rha-pill-low'
            table_rows += (
                f'<tr><td>{row["condition"]}</td><td>{date_str}</td>'
                f'<td><span class="rha-pill {pill_class}">{row["risk"]} Risk</span></td></tr>'
            )
        body_html = (
            '<table class="rha-table"><thead><tr>'
            '<th>Condition</th><th>Date</th><th>Risk</th>'
            f'</tr></thead><tbody>{table_rows}</tbody></table>'
        )
    else:
        body_html = ('<div class="rha-empty">No predictions run yet. '
                     'Go to Disease Prediction to get started.</div>')

    st.markdown(f"""
        <style>
        .rha-card{{background:#fff;border-radius:14px;padding:22px 24px;
                  box-shadow:0 1px 3px rgba(15,23,42,.08); color-scheme:light;}}
        .rha-card, .rha-card *{{color:#0f172a !important;}}
        .rha-header{{display:flex;align-items:center;justify-content:space-between;
                    margin-bottom:14px;}}
        .rha-title{{font-weight:700;font-size:18px;margin:0;}}
        .rha-viewall{{color:#0f766e !important;font-weight:700;font-size:14px;}}
        .rha-table{{width:100%;border-collapse:collapse;font-size:14px;}}
        .rha-table th{{
            text-align:left;padding:10px 12px;background:#f8fafc;
            font-size:12px;letter-spacing:.03em;color:#64748b !important;
            border-bottom:1px solid #e2e8f0;
        }}
        .rha-table td{{padding:12px;border-bottom:1px solid #f1f5f9;}}
        .rha-table tr:last-child td{{border-bottom:none;}}
        .rha-pill{{display:inline-block;padding:4px 12px;border-radius:999px;
                  font-size:12.5px;font-weight:700;white-space:nowrap;}}
        .rha-pill-low{{background:#dcfce7 !important;color:#15803d !important;}}
        .rha-pill-high{{background:#fee2e2 !important;color:#b91c1c !important;}}
        .rha-empty{{color:#64748b !important;font-size:14px;padding:8px 0;}}
        </style>
        <div class="rha-card">
            <div class="rha-header">
                <div class="rha-title">Recent Health Activity</div>
                <div class="rha-viewall">View all</div>
            </div>
            {body_html}
        </div>
    """, unsafe_allow_html=True)


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
                        diab_prediction = diabetes_model.predict([user_input])

                        if diab_prediction[0] == 1:
                            diab_diagnosis = 'The person is Diabetic'
                            log_prediction('Diabetes', diab_diagnosis, 'High')
                        else:
                            diab_diagnosis = 'The person is Not Diabetic'
                            log_prediction('Diabetes', diab_diagnosis, 'Low')

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
                        heart_prediction = heart_disease_model.predict([user_input])

                        if heart_prediction[0] == 1:
                            heart_diagnosis = 'The person has heart disease'
                            log_prediction('Heart Disease', heart_diagnosis, 'High')
                        else:
                            heart_diagnosis = 'The person does not have heart disease'
                            log_prediction('Heart Disease', heart_diagnosis, 'Low')

                        st.success(heart_diagnosis)
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
                        parkinsons_prediction = parkinsons_model.predict([user_input])

                        if parkinsons_prediction[0] == 1:
                            parkinsons_diagnosis = "The person has Parkinson's disease"
                            log_prediction('Parkinsons', parkinsons_diagnosis, 'High')
                        else:
                            parkinsons_diagnosis = "The person does not have Parkinson's disease"
                            log_prediction('Parkinsons', parkinsons_diagnosis, 'Low')

                        st.success(parkinsons_diagnosis)
                    except ValueError:
                        st.error('Please enter valid numeric values in all fields.')
