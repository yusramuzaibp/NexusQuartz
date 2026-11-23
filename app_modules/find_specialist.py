
import streamlit as st
from urllib.parse import quote_plus

from specialists_data import SPECIALISTS


def show_find_specialist():

    st.title("Find a Specialist")

    st.write(
        "Find specialists based on the disease and your preferred location."
    )

    # Custom glassmorphism card styling
    st.markdown("""
    <style>
    div[class*="st-key-doctor_card_"] {
        background: rgba(255, 255, 255, 0.62);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.85);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 5px 20px rgba(0, 70, 100, 0.07);
        transition: all 0.25s ease;
    }

    div[class*="st-key-doctor_card_"]:hover {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid rgba(0, 150, 180, 0.35);
        box-shadow: 0 8px 25px rgba(0, 70, 100, 0.12);
        transform: translateY(-3px);
    }

    div[class*="st-key-doctor_card_"] h3 {
        color: #06465a;
    }

    div[class*="st-key-doctor_card_"] p {
        color: #345866;
    }
    </style>
    """, unsafe_allow_html=True)

    # Disease selection
    disease = st.selectbox(
        "Select Disease",
        ["Diabetes", "Heart Disease", "Parkinsons"]
    )

    # City selection
    city = st.selectbox(
        "Select City",
        ["Bengaluru", "Mysuru", "Chennai", "Hyderabad"]
    )

    # Filter specialists
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

    # Display specialist cards in two columns
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

                    st.markdown(
                        f"### {doctor.get('name', 'Specialist')}"
                    )

                    st.caption(
                        doctor.get("specialization", "Specialist")
                    )

                    st.divider()

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
                        st.markdown(f"**Experience:** {experience}")

                    qualification = doctor.get("qualification")
                    if qualification:
                        st.markdown(
                            f"**Qualification:** {qualification}"
                        )

                    phone = doctor.get("phone")
                    if phone:
                        st.markdown(f"**Contact:** {phone}")

                    st.write("")

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
