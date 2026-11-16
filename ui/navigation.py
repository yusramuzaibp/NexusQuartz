import streamlit as st
from streamlit_option_menu import option_menu


# ================= NAVIGATION STYLES =================

NAVIGATION_STYLES = {
    "container": {
        "padding": "8px",
        "background-color": "#FFFFFF",
        "border-radius": "12px",
    },
    "icon": {
        "color": "#07566B",
        "font-size": "18px",
    },
    "nav-link": {
        "font-size": "15px",
        "text-align": "left",
        "margin": "5px 0",
        "padding": "12px 14px",
        "border-radius": "10px",
        "color": "#36525F",
        "background-color": "#FFFFFF",
        "font-weight": "500",
    },
    "nav-link-selected": {
        "background-color": "#BFECEF",
        "color": "#07566B",
        "font-weight": "700",
    },
}


def show_navigation():

    # ================= SIDEBAR NAVIGATION =================

    with st.sidebar:

        st.markdown(
            f"### 👋 Welcome, **{st.session_state.user_name}**"
        )

        if st.button("🚪 Logout", use_container_width=True):

            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_id = None

            st.rerun()

        st.divider()

        # ================= ROLE-BASED NAVIGATION =================

        user_role = st.session_state.get("user_role", "user")

        if user_role == "admin":

            selected = option_menu(
                "Admin Panel",
                [
                    "Admin Dashboard",
                    "Manage Users",
                    "All Prediction Records",
                ],
                icons=[
                    "speedometer2",
                    "people",
                    "clipboard-data",
                ],
                default_index=0,
                styles=NAVIGATION_STYLES,
            )

        else:

            menu_items = [
                "Dashboard",
                "Disease Prediction",
                "Patient Reports",
                "AI Chatbot",
                "Find a Specialist",
            ]

            default_page = st.session_state.get(
                "page", "Dashboard"
            )

            if default_page not in menu_items:
                default_page = "Dashboard"

            if st.session_state.get("navigate_to_disease", False):

                st.session_state.user_navigation = "Disease Prediction"
                st.session_state.navigate_to_disease = False

            selected = option_menu(
                "Multiple Disease Prediction System",
                menu_items,
                icons=[
                    "speedometer2",
                    "clipboard2-pulse",
                    "person-vcard",
                    "chat-dots",
                    "geo-alt",
                ],
                default_index=menu_items.index(default_page),
                key="user_navigation",
                styles=NAVIGATION_STYLES,
            )

            st.session_state.page = selected

    return selected
