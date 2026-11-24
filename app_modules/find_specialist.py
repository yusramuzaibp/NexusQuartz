
import streamlit as st
from urllib.parse import quote_plus
from html import escape

from specialists_data import SPECIALISTS


def show_find_specialist():

    st.title("Find a Specialist")

    st.write(
        "Find specialists based on the disease and your preferred location."
    )

    # ================= CUSTOM CARD STYLING =================

    st.markdown("""
    <style>

    /* Main doctor card */
    div[class*="st-key-doctor_card_"] {
        background: #FFFFFF;
        border: 1px solid rgba(0, 70, 100, 0.12);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 5px 20px rgba(0, 70, 100, 0.07);
        transition: all 0.25s ease;
        overflow: hidden;
    }

    div[class*="st-key-doctor_card_"]:hover {
        box-shadow: 0 8px 25px rgba(0, 70, 100, 0.12);
        transform: translateY(-3px);
    }

    /* Disease-specific header backgrounds */

    .diabetes-header {
        background: #E5F3E9;
    }

    .heart-header {
        background: #E8F1FA;
    }

    .parkinsons-header {
        background: #E3D7F2;
    }

    /* Common doctor header styling */

    .doctor-header {
        padding: 18px 20px;
        margin: -20px -20px 0 -20px;
        border-radius: 18px 18px 0 0;
        box-sizing: border-box;
    }

    .doctor-header h3 {
        color: #173D32 !important;
        margin: 0;
        font-size: 21px;
        font-weight: 700;
    }

    .doctor-header p {
        color: #345866 !important;
        margin: 5px 0 0 0;
        font-size: 14px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ================= DISEASE SELECTION =================

    disease = st.selectbox(
        "Select Disease",
        ["Diabetes", "Heart Disease", "Parkinsons"]
    )

    # ================= CITY SELECTION =================

    city = st.selectbox(
        "Select City",
        ["Bengaluru", "Mysuru", "Chennai", "Hyderabad"]
    )

    # ================= FILTER SPECIALISTS =================

    filtered_specialists = [
        doctor for doctor in SPECIALISTS
        if doctor.get("verified") is True
        and doctor.get("disease", "").casefold() == disease.casefold()
        and city.casefold() == doctor.get("city", "").casefold()
    ]

    st.divider()

    st.subheader("Available Specialists")

    if not filtered_specialists:
        st.info(
            "No verified specialists found for this selection. "
            "Try another disease or city."
        )
        return

    # ================= DISPLAY SPECIALIST CARDS =================

    for start in range(0, len(filtered_specialists), 2):

        card_columns = st.columns(2)

        for index, (doctor, column) in enumerate(
            zip(filtered_specialists[start:start + 2], card_columns)
        ):

            with column:

                card_key = (
                    f"doctor_card_{start}_{index}_"
                    f"{doctor.get('name', 'specialist').replace(' ', '_')}"
                )

                with st.container(
                    border=False,
                    key=card_key
                ):

                    # Select header background based on disease

                    if doctor.get("disease", "").casefold() == "diabetes":
                        header_class = "diabetes-header"

                    elif doctor.get("disease", "").casefold() == "heart disease":
                        header_class = "heart-header"

                    else:
                        header_class = "parkinsons-header"

                    # Doctor card header
                    doctor_name = escape(str(doctor.get('name') or 'Specialist'))
                    doctor_specialization = escape(str(doctor.get('specialization') or 'Specialist'))
                    st.markdown(
                        f"""
                        <div class="doctor-header {header_class}">
                            <h3>{doctor_name}</h3>
                            <p>{doctor_specialization}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.divider()

                    # ================= DOCTOR DETAILS =================

                    st.markdown(
                        f"**Hospital**  \n"
                        f"{doctor.get('hospital') or 'Not available'}"
                    )

                    st.markdown(
                        f"**Location**  \n"
                        f"{doctor.get('address') or doctor.get('city', 'Not available')}"
                    )

                    experience = doctor.get("experience")

                    if experience:
                        st.markdown(
                            f"**Experience:** {experience}"
                        )

                    qualification = doctor.get("qualification")

                    if qualification:
                        st.markdown(
                            f"**Qualification:** {qualification}"
                        )

                    phone = doctor.get("phone")

                    if phone:
                        st.markdown(
                            f"**Contact:** {phone}"
                        )

                    st.write("")

                    # ================= MAPS LINK =================

                    maps_query = quote_plus(
                        f"{doctor.get('hospital', '')} "
                        f"{doctor.get('address') or ''} "
                        f"{doctor.get('city', '')}"
                    )

                    action_columns = st.columns(2)

                    website = doctor.get("website")

                    with action_columns[0]:

                        if website:
                            st.link_button(
                                "Hospital Website",
                                website,
                                use_container_width=True
                            )

                    with action_columns[1]:

                        st.link_button(
                            "Google Maps",
                            f"https://www.google.com/maps/search/?api=1&query={maps_query}",
                            use_container_width=True
                        )
