import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components

# ================= NAVIGATION STYLES =================

NAVIGATION_STYLES = {
    "container": {
        "padding": "5px",
        "background-color": "#F4FBFC",
        "border-radius": "12px",
    },
    "icon": {
        "color": "#07566B",
        "font-size": "17px",
    },
    "nav-link": {
        "font-size": "14px",
        "text-align": "left",
        "margin": "3px 0",
        "padding": "9px 12px",
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


# ================= SHOW NAVIGATION =================

def show_navigation():

    with st.sidebar:

        # ================= USER DETAILS =================

        user_name = st.session_state.get("user_name", "User")

        initials = "".join(
            word[0].upper()
            for word in user_name.split()
            if word
        )[:2]

        user_role = st.session_state.get("user_role", "user")

        # ================= SIDEBAR CSS =================

        st.markdown(
            f"""
            <style>

            section[data-testid="stSidebar"] {{
                height: 100vh;
            }}

            section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
                height: 100vh;
                overflow-y: auto !important;
                overflow-x: hidden !important;
            }}

            section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
                gap: 0.35rem;
            }}

            /* Profile card */
            .st-key-sidebar_profile_button button {{
                height: 70px;
                min-height: 70px;
                background: #FFFFFF;
                border: 1px solid #D5E8EB;
                border-radius: 14px;
                color: #183D49;
                text-align: left;
                padding: 8px 12px;
                display: flex;
                align-items: center;
                white-space: pre-line;
                font-size: 14px;
                font-weight: 600;
            }}

            .st-key-sidebar_profile_button button::before {{
                content: "{initials}";
                width: 42px;
                height: 42px;
                min-width: 42px;
                border-radius: 50%;
                background: #BFECEF;
                color: #07566B;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                font-weight: 700;
                margin-right: 12px;
            }}

            .st-key-sidebar_profile_button button:hover {{
                background: #EAF8F9;
                border-color: #75C9D1;
                color: #07566B;
            }}

            /* Logout button */
            .st-key-sidebar_logout_button button {{
                height: 36px;
                min-height: 36px;
                background: transparent;
                border: none;
                color: #55717A;
                text-align: left;
                padding: 5px 12px;
                font-size: 14px;
            }}

            .st-key-sidebar_logout_button button:hover {{
                background: #FDECEC;
                color: #B42318;
            }}

            /* Footer */
            .st-key-sidebar_footer {{
                position: sticky;
                bottom: 0;
                z-index: 999;
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                outline: none !important;
                padding: 6px 0;
                flex-shrink: 0;
            }}

            /* Navigation heading */
            section[data-testid="stSidebar"] h2 {{
                font-size: 13px !important;
                font-weight: 500 !important;
                color: #55717A !important;
                margin-top: 0 !important;
                margin-left: 10px !important;
            }}

            </style>
            """,
            unsafe_allow_html=True,
        )

        # ================= USER MENU ITEMS =================

        if user_role == "admin":

            menu_items = [
                "Admin Dashboard",
                "Manage Users",
                "All Prediction Records",
            ]

            icons = [
                "speedometer2",
                "people",
                "clipboard-data",
            ]

        else:

            menu_items = [
                "Dashboard",
                "Disease Prediction",
                "Patient Reports",
                "AI Chatbot",
                "Find a Specialist",
            ]

            icons = [
                "speedometer2",
                "clipboard2-pulse",
                "person-vcard",
                "chat-dots",
                "geo-alt",
            ]

        if "last_menu_page" not in st.session_state:
            st.session_state.last_menu_page = menu_items[0]

        if st.session_state.last_menu_page not in menu_items:
            st.session_state.last_menu_page = menu_items[0]


        # ================= APPLICATION BRANDING =================

        components.html(
            """
            <!DOCTYPE html>
            <html>
            <body style="margin:0; padding:5px; background:transparent;
                         font-family:Arial,sans-serif;">

                <div style="display:flex; align-items:center; gap:10px;">

                    <svg width="48" height="48" viewBox="0 0 100 100"
                         xmlns="http://www.w3.org/2000/svg">

                        <polygon
                            points="50,5 90,27 90,73 50,95 10,73 10,27"
                            fill="none"
                            stroke="#0796A5"
                            stroke-width="7"
                            stroke-linejoin="round"/>

                        <polyline
                            points="18,52 34,52 43,32 56,70 67,45 80,45"
                            fill="none"
                            stroke="#0796A5"
                            stroke-width="6"
                            stroke-linecap="round"
                            stroke-linejoin="round"/>
                    </svg>

                    <div>
                        <div style="font-size:23px; font-weight:800;
                                    color:#07566B; white-space:nowrap;">
                            Nexus Quartz
                        </div>

                    </div>

                </div>
            </body>
            </html>
            """,
            height=70,
            scrolling=False
        )

        # ================= NAVIGATION MENU =================

        selected = option_menu(
            "Multiple Disease Prediction System",
            menu_items,
            icons=icons,
            default_index=menu_items.index(
                st.session_state.last_menu_page
            ),
            key="user_navigation",
            styles=NAVIGATION_STYLES,
        )

        if selected != st.session_state.last_menu_page:

            st.session_state.last_menu_page = selected
            st.session_state.show_profile = False

        # ================= BOTTOM PROFILE SECTION =================

        with st.container(key="sidebar_footer"):

            st.divider()

            # ================= PROFILE CARD =================

            if st.button(
                f"{user_name}\nView Profile  ›",
                key="sidebar_profile_button",
                use_container_width=True,
            ):
                st.session_state.show_profile = True

            # ================= LOGOUT BUTTON =================

            if st.button(
                "↪   Logout",
                key="sidebar_logout_button",
                use_container_width=True,
            ):

                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.user_name = ""
                st.session_state.user_email = ""
                st.session_state.user_role = "user"
                st.session_state.show_profile = False
                st.session_state.profile_action = None

                st.rerun()

        # ================= PROFILE PAGE =================

        if st.session_state.get("show_profile", False):
            return "Profile"

    return selected
