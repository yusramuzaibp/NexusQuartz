
import streamlit as st


def show_find_specialist():

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
