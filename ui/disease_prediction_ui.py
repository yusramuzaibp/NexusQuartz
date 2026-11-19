
import streamlit as st
from pathlib import Path
import base64
import html


def render_disease_selection(disease_info):

    st.title('Select Disease to Predict')
    st.write(
        'Choose a disease category. You will be guided '
        'through the required clinical parameters.'
    )

    cols = st.columns(3)

    # Locate images from the project root
    project_root = Path(__file__).resolve().parent.parent

    image_paths = {
        "Diabetes": project_root / "assets" / "diabetes.png",
        "Heart Disease": project_root / "assets" / "heart.png",
        "Parkinsons": project_root / "assets" / "brain.png"
    }

    for col, (name, info) in zip(cols, disease_info.items()):

        with col:

            image_path = image_paths.get(name)

            if image_path and image_path.exists():

                image_base64 = base64.b64encode(
                    image_path.read_bytes()
                ).decode("utf-8")

                safe_name = html.escape(str(name))
                safe_desc = html.escape(str(info["desc"]))
                safe_params = html.escape(str(info["params"]))

                card_html = f"""
<div style="
    box-sizing: border-box;
    min-height: 290px;
    width: 100%;
    border-radius: 18px;
    overflow: hidden;
    padding: 22px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    background-image:
        linear-gradient(
            to top,
            rgba(5, 25, 40, 0.95),
            rgba(5, 25, 40, 0.10)
        ),
        url('data:image/png;base64,{image_base64}');
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(255,255,255,0.3);
    box-shadow: 0 8px 22px rgba(15, 50, 70, 0.15);
">

    <div style="
        color: white;
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 8px;
    ">{safe_name}</div>

    <div style="
        color: #f1f5f9;
        font-size: 13px;
        line-height: 1.5;
    ">{safe_desc}</div>

    <div style="
        color: #a5f3fc;
        font-size: 13px;
        font-weight: 600;
        margin-top: 12px;
    ">{safe_params} parameters ›</div>

</div>
"""

                st.html(card_html)

            else:
                st.warning(f"Image not found for {name}")

            if st.button(
                f'Select {name}',
                key=f'select_{name}',
                use_container_width=True
            ):
                return name

    return None


def render_disease_form_header(disease_choice):

    st.title(f'{disease_choice} Prediction')
    st.markdown('---')


def render_back_button():

    st.write("")
    return st.button('← Back to disease selection')


def render_patient_details(only_digits, contact_key):

    st.subheader("Patient Details")

    patient_col1, patient_col2 = st.columns(2)

    with patient_col1:

        patient_name = st.text_input("Patient Name")

        patient_age = st.number_input(
            "Patient Age",
            min_value=1,
            max_value=120,
            value=None
        )

    with patient_col2:

        patient_gender = st.selectbox(
            "Gender",
            ["Select Gender", "Male", "Female", "Other"]
        )

    patient_contact = st.text_input(
        "Contact Number",
        max_chars=10,
        help="Enter a valid 10-digit contact number.",
        key=contact_key,
        on_change=only_digits,
        args=(contact_key,)
    )

    return patient_name, patient_age, patient_gender, patient_contact


def render_disease_parameters_header(disease_name):

    st.divider()
    st.subheader(f"{disease_name} Health Parameters")


def render_prediction_button(disease_name):

    return st.button(
        f'{disease_name} Test Result',
        key=f'{disease_name.lower()}_test_result'
    )


def load_css():

    css_path = Path(__file__).parent / "styles.css"

    with open(css_path, "r", encoding="utf-8") as file:
        css = file.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )
