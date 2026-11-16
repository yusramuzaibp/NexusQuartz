
import streamlit as st
import base64
from pathlib import Path

from auth.authentication import (
    create_user,
    login_user,
    validate_password,
)

from database.database import get_user_predictions


def show_auth_page():

    # ================= BACKGROUND IMAGE =================

    image_path = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "login_bg.png"
    )

    with open(image_path, "rb") as image_file:
        bg_base64 = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    # ================= CUSTOM STYLING =================

    css = f"""
    <style>

    /* ================= PAGE BACKGROUND ================= */

    .stApp {{
        background-image:
            linear-gradient(
                rgba(5, 45, 65, 0.12),
                rgba(5, 45, 65, 0.12)
            ),
            url("data:image/png;base64,{bg_base64}");

        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    [data-testid="stAppViewContainer"] .main .block-container {{
        max-width: 1250px;
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }}

    /* ================= LEFT BRANDING CARD ================= */

    .hero-card {{
        background: linear-gradient(
            145deg,
            #BFECEF,
            #DDF3F4
        );

        padding: 40px 30px;
        border-radius: 22px;
        min-height: 480px;
        margin-top: 25px;

        border: 1px solid rgba(255,255,255,0.8);

        box-shadow:
            0 12px 35px rgba(5,45,65,0.15);
    }}

    .hero-card h1 {{
        color: #07566B;
        font-size: 31px;
        line-height: 1.3;
        font-weight: 700;
    }}

    .hero-card p {{
        color: #36525F;
        font-size: 16px;
        line-height: 1.8;
    }}

    .hero-tag {{
        display: inline-block;
        background: rgba(255,255,255,0.65);
        padding: 10px 15px;
        border-radius: 20px;
        color: #07566B;
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 25px;
    }}

    .feature-item {{
        color: #07566B;
        font-size: 15px;
        font-weight: 600;
        margin-top: 22px;
    }}

    /* ================= RIGHT LOGIN CARD ================= */

    .st-key-login-panel {{
        background: rgba(239,247,250,0.96);
        border: 1px solid rgba(255,255,255,0.9);
        border-radius: 22px;
        padding: 28px 30px;
        margin-top: 25px;

        box-shadow:
            0 12px 35px rgba(5,45,65,0.20);

        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }}

    /* ================= LOGIN HEADINGS ================= */

    .st-key-login-panel h2,
    .st-key-login-panel h3 {{
        color: #07566B !important;
    }}

    /* ================= INPUT FIELDS ================= */

    .st-key-login-panel div[data-testid="stTextInput"] input {{
        border-radius: 10px;
        min-height: 44px;
        background-color: #FFFFFF;
        border: 1px solid #D5E5EA;
    }}

    .st-key-login-panel div[data-testid="stTextInput"] input:focus {{
        border-color: #087E8B;
        box-shadow: 0 0 0 1px #087E8B;
    }}

    /* ================= LOGIN BUTTON ================= */

    .st-key-login-panel div[data-testid="stButton"] button {{
        background-color: #087E8B;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        min-height: 46px;
        font-weight: 700;
        transition: all 0.2s ease;
    }}

    .st-key-login-panel div[data-testid="stButton"] button:hover {{
        background-color: #07566B;
        color: #FFFFFF;
        transform: translateY(-2px);
    }}

    /* ================= LOGIN / SIGNUP TABS ================= */

    div[data-testid="stTabs"] button[role="tab"] {{
        color: #36525F !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        color: #07566B !important;
    }}

    div[data-testid="stTabs"] button[role="tab"]:hover {{
        color: #087E8B !important;
    }}

    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
        background-color: #087E8B !important;
        border-bottom-color: #087E8B !important;
    }}

    div[data-testid="stTabs"] [data-baseweb="tab-border"] {{
        background-color: #D5E5EA !important;
    }}

    /* ================= RESPONSIVE DESIGN ================= */

    @media (max-width: 768px) {{

        .hero-card {{
            min-height: auto;
            padding: 28px 22px;
            margin-top: 10px;
        }}

        .hero-card h1 {{
            font-size: 26px;
        }}

        .st-key-login-panel {{
            margin-top: 10px;
            padding: 20px;
        }}
    }}

    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    # ================= MAIN PAGE LAYOUT =================

    left_col, right_col = st.columns(
        [1.05, 1],
        gap="large"
    )

    # ================= LEFT BRANDING SECTION =================

    with left_col:

        st.html("""
            <div class="hero-card">

                <div class="hero-tag">
                    🩺 Multiple Disease Prediction
                </div>

                <h1>
                    Your Health.<br>
                    Our Intelligence.
                </h1>

                <p>
                    Welcome to the Multiple Disease Prediction System.
                    Use intelligent machine learning technology to
                    explore health insights and manage your
                    prediction records.
                </p>

                <div class="feature-item">
                    🧠 &nbsp; AI-Powered Disease Prediction
                </div>

                <div class="feature-item">
                    📊 &nbsp; Personal Health Reports
                </div>

                <div class="feature-item">
                    💬 &nbsp; AI Health Assistant
                </div>

                <div class="feature-item">
                    👨‍⚕️ &nbsp; Specialist Discovery
                </div>

            </div>
        """)

    # ================= RIGHT LOGIN SECTION =================

    with right_col:

        with st.container(key="login-panel"):

            st.html("""
                <div style="padding: 5px 5px 10px 5px;">

                    <h2 style="
                        color:#07566B;
                        margin-bottom:5px;
                    ">
                        Welcome Back
                    </h2>

                    <p style="
                        color:#36525F;
                        font-size:15px;
                    ">
                        Sign in or create an account to continue.
                    </p>

                </div>
            """)

            login_tab, signup_tab = st.tabs(
                ["🔐 Login", "📝 Sign Up"]
            )

            # ================= LOGIN =================

            with login_tab:

                st.subheader("Login to Your Account")

                email = st.text_input(
                    "Email",
                    placeholder="Enter your email",
                    key="login_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password"
                )

                if st.button(
                    "🔐 Login",
                    use_container_width=True
                ):

                    if not email or not password:

                        st.warning(
                            "⚠️ Please enter your email and password."
                        )

                    else:

                        try:

                            user = login_user(email, password)

                            if user:

                                st.session_state.logged_in = True
                                st.session_state.user_id = user[0]
                                st.session_state.user_name = user[1]
                                st.session_state.user_role = user[3]

                                st.session_state.history = (
                                    get_user_predictions(user[0])
                                )

                                st.success("✅ Login successful!")
                                st.rerun()

                            else:

                                st.error(
                                    "❌ Invalid email or password."
                                )

                        except Exception as e:

                            st.error(f"Login failed: {e}")

            # ================= SIGNUP =================

            with signup_tab:

                st.subheader("Create Your Account")

                name = st.text_input(
                    "Full Name",
                    placeholder="Enter your name",
                    key="signup_name"
                )

                email = st.text_input(
                    "Email",
                    placeholder="Enter your email",
                    key="signup_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a password",
                    key="signup_password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Confirm your password",
                    key="confirm_password"
                )

                st.caption(
                    "Password must contain 8+ characters, "
                    "uppercase, lowercase, number and special character."
                )

                if st.button(
                    "📝 Create Account",
                    use_container_width=True
                ):

                    if (
                        not name
                        or not email
                        or not password
                        or not confirm_password
                    ):

                        st.warning(
                            "⚠️ Please fill in all fields."
                        )

                    elif password != confirm_password:

                        st.error("❌ Passwords do not match.")

                    else:

                        password_errors = validate_password(password)

                        if password_errors:

                            st.error(
                                "❌ Your password does not meet the requirements."
                            )

                            st.markdown(
                                "**Please fix the following:**"
                            )

                            for error in password_errors:
                                st.write(f"• {error}")

                        else:

                            try:

                                result = create_user(
                                    name,
                                    email,
                                    password
                                )

                                if result:

                                    st.success(
                                        "✅ Account created successfully!"
                                    )

                                    st.info(
                                        "You can now go to the Login tab and log in."
                                    )

                                else:

                                    st.error(
                                        "❌ An account with this email already exists."
                                    )

                            except ValueError as e:

                                st.error(str(e))

                            except Exception as e:

                                st.error(
                                    f"Unable to create your account: {e}"
                                )
