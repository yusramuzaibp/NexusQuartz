import streamlit as st
import base64
import secrets
import hashlib
import hmac
import time
from pathlib import Path
import streamlit.components.v1 as components
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

from auth.authentication import (
    create_user,
    login_user,
    validate_password,
    reset_password,
    email_exists
)

from database.database import get_user_predictions

# ================= GMAIL OTP DELIVERY =================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def send_reset_otp(receiver_email, otp):

    sender_email = os.getenv("SMTP_EMAIL")
    app_password = os.getenv("SMTP_APP_PASSWORD")

    if not sender_email or not app_password:
        raise ValueError("Gmail SMTP credentials are missing from .env")

    message = EmailMessage()

    message["Subject"] = "Nexus Quartz - Password Reset OTP"
    message["From"] = sender_email
    message["To"] = receiver_email

    message.set_content(
        f"""
Hello,

We received a request to reset your Nexus Quartz account password.

Your OTP is: {otp}

This OTP is valid for 2 minutes.

If you did not request this password reset, please ignore this email.

Regards,
Nexus Quartz Team
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:

        server.login(
            sender_email,
            app_password.replace(" ", "")
        )

        server.send_message(message)

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
            rgba(191, 236, 239, 0.75),
            rgba(221, 243, 244, 0.75)
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
    /* ================= NEXUS QUARTZ LOGO ================= */

    .nexus-brand {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 28px;
    }}

    .nexus-logo {{
        width: 58px;
        height: 58px;
        flex-shrink: 0;
    }}

    .nexus-brand-name {{
        color: #07566B;
        font-size: 27px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }}
    .nexus-hexagon {{
        width: 58px;
        height: 58px;
        background: #087E8B;
        clip-path: polygon(
            50% 0%,
            95% 25%,
            95% 75%,
            50% 100%,
            5% 75%,
            5% 25%
        );
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }}

    .nexus-heartbeat {{
        width: 45px;
        height: 30px;
    }}

    .nexus-heartbeat svg {{
        width: 100%;
        height: 100%;
    }}

    .feature-item {{
        color: #07566B;
        font-size: 15px;
        font-weight: 600;
        margin-top: 22px;
    }}

    /* ================= RIGHT LOGIN CARD ================= */

    .st-key-login-panel {{
        background: rgba(239,247,250,0.75);
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
        background-color: #35A6B2;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        min-height: 46px;
        font-weight: 700;
        transition: all 0.2s ease;
    }}

    .st-key-login-panel div[data-testid="stButton"] button:hover {{
        background-color: #258D9A;
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

        components.html(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        background: transparent;
                        font-family: Arial, sans-serif;
                    }

                    .hero-card {
                        background: linear-gradient(
                            145deg,
                            rgba(191, 236, 239, 0.75),
                            rgba(221, 243, 244, 0.75)
                        );
                        padding: 40px 30px;
                        border-radius: 22px;
                        min-height: 480px;
                        margin-top: 25px;
                        box-sizing: border-box;
                        border: 1px solid rgba(255,255,255,0.8);
                        box-shadow: 0 12px 35px rgba(5,45,65,0.15);
                    }

                    .nexus-brand {
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        margin-bottom: 28px;
                    }

                    .brand-name {
                        font-size: 27px;
                        font-weight: 800;
                        color: #07566B;
                        white-space: nowrap;
                    }

                    h1 {
                        color: #07566B;
                        font-size: 31px;
                        line-height: 1.3;
                        font-weight: 700;
                    }

                    p {
                        color: #36525F;
                        font-size: 16px;
                        line-height: 1.8;
                    }

                    .tagline {
                        font-style: italic;
                        font-size: 19px;
                    }

                    .feature-item {
                        color: #07566B;
                        font-size: 15px;
                        font-weight: 600;
                        margin-top: 22px;
                    }
                </style>
            </head>

            <body>

                <div class="hero-card">

                    <!-- NEXUS QUARTZ LOGO -->

                    <div class="nexus-brand">

                        <svg width="48" height="48"
                             viewBox="0 0 100 100"
                             xmlns="http://www.w3.org/2000/svg">

                            <polygon
                                points="50,5 90,27 90,73 50,95 10,73 10,27"
                                fill="none"
                                stroke="#07566B"
                                stroke-width="7"
                                stroke-linejoin="round"/>

                            <polyline
                                points="18,52 34,52 43,32 56,70 67,45 80,45"
                                fill="none"
                                stroke="#07566B"
                                stroke-width="6"
                                stroke-linecap="round"
                                stroke-linejoin="round"/>

                        </svg>

                        <div class="brand-name">
                            Nexus Quartz
                        </div>

                    </div>

                    <h1>🩺 Multiple Disease Prediction</h1>

                    <p class="tagline">
                        Your Health. Our Intelligence.
                    </p>

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

            </body>
            </html>
            """,
            height=570,
            scrolling=False
        )

    # ================= RIGHT LOGIN SECTION =================

    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"

    with right_col:

        with st.container(key="login-panel"):

            # ================= LOGIN VIEW =================

            if st.session_state.auth_view == "login":

                st.html("""
                    <div style="padding: 5px 0 15px 0;">
                        <div style="color:#087E8B; font-weight:700;">
                            🔒 SECURE LOGIN
                        </div>
                        <h2 style="color:#07566B; margin-top:8px;">
                            Welcome back
                        </h2>
                        <p style="color:#36525F;">
                            Enter your credentials to access your health dashboard.
                        </p>
                    </div>
                """)

                email = st.text_input(
                    "Email address",
                    placeholder="Enter your email",
                    key="login_email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password"
                )

                _, forgot_col = st.columns([2, 1])

                with forgot_col:
                    if st.button(
                        "Forgot password?",
                        key="open_forgot_password"
                    ):
                        st.session_state.auth_view = "reset"
                        st.rerun()

                if st.button(
                    "Sign In",
                    use_container_width=True,
                    key="login_button"
                ):

                    if not email or not password:
                        st.warning(
                            "Please enter your email and password."
                        )

                    else:
                        try:
                            user = login_user(email, password)

                            if (
                                isinstance(user, dict)
                                and "account_status" in user
                            ):
                                st.error(
                                    f"Your account is currently "
                                    f"{user['account_status']}. "
                                    "Please contact the administrator."
                                )

                            elif user:
                                st.session_state.logged_in = True
                                st.session_state.user_id = user[0]
                                st.session_state.user_name = user[1]
                                st.session_state.user_email = user[2]
                                st.session_state.user_role = user[3]
                                
                                st.session_state.history = (
                                    get_user_predictions(user[0])
                                )

                                st.success("Login successful!")
                                st.rerun()

                            else:
                                st.error(
                                    "Invalid email or password."
                                )

                        except Exception as e:
                            st.error(f"Login failed: {e}")

                st.markdown(
                    "<div style='text-align:center; margin-top:20px; "
                    "color:#36525F;'>"
                    "Don't have an account?</div>",
                    unsafe_allow_html=True
                )

                if st.button(
                    "Create account",
                    use_container_width=True,
                    key="open_signup"
                ):
                    st.session_state.auth_view = "signup"
                    st.rerun()

            # ================= SIGNUP VIEW =================

            elif st.session_state.auth_view == "signup":

                st.html("""
                    <div style="padding: 5px 0 15px 0;">
                        <div style="color:#087E8B; font-weight:700;">
                            ✨ JOIN US
                        </div>
                        <h2 style="color:#07566B; margin-top:8px;">
                            Create your account
                        </h2>
                        <p style="color:#36525F;">
                            Get started with your personal health dashboard.
                        </p>
                    </div>
                """)

                if st.button(
                    "← Back to Login",
                    key="signup_back"
                ):
                    st.session_state.auth_view = "login"
                    st.rerun()

                name = st.text_input(
                    "Full Name",
                    placeholder="Enter your name",
                    key="signup_name"
                )

                email = st.text_input(
                    "Email address",
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
                    "Create Account",
                    use_container_width=True,
                    key="signup_button"
                ):

                    if (
                        not name
                        or not email
                        or not password
                        or not confirm_password
                    ):
                        st.warning("Please fill in all fields.")

                    elif password != confirm_password:
                        st.error("Passwords do not match.")

                    else:
                        password_errors = validate_password(password)

                        if password_errors:
                            st.error(
                                "Your password does not meet the requirements."
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
                                        "Account created successfully!"
                                    )
                                    st.session_state.auth_view = "login"
                                    st.rerun()

                                else:
                                    st.error(
                                        "An account with this email "
                                        "already exists."
                                    )

                            except ValueError as e:
                                st.error(str(e))

                            except Exception as e:
                                st.error(
                                    f"Unable to create your account: {e}"
                                )

            # ================= FORGOT PASSWORD VIEW =================

            elif st.session_state.auth_view == "reset":

                st.html("""
                    <div style="padding: 5px 0 15px 0;">
                        <div style="color:#087E8B; font-weight:700;">
                            🔑 ACCOUNT RECOVERY
                        </div>
                        <h2 style="color:#07566B; margin-top:8px;">
                            Reset your password
                        </h2>
                        <p style="color:#36525F;">
                            Verify your account and create a new password.
                        </p>
                    </div>
                """)

                if st.button(
                    "← Back to Login",
                    key="reset_back"
                ):
                    st.session_state.auth_view = "login"
                    st.rerun()

                reset_email = st.text_input(
                    "Registered Email",
                    placeholder="Enter your registered email",
                    key="reset_email"
                )

                # ================= GENERATE OTP =================

                if st.button(
                    "Generate OTP",
                    use_container_width=True,
                    key="generate_otp"
                ):

                    last_sent = st.session_state.get(
                        "reset_otp_last_sent", 0
                    )

                    remaining = 60 - (time.time() - last_sent)

                    if remaining > 0:
                        st.warning(
                            f"Please wait {int(remaining) + 1} seconds "
                            "before requesting another OTP."
                        )

                    elif not reset_email:
                        st.warning(
                            "Please enter your registered email."
                        )

                    elif not email_exists(reset_email):
                        st.error(
                            "No account found with this email."
                        )

                    else:
                        otp = f"{secrets.randbelow(1000000):06d}"
                        recipient_email = reset_email.strip().lower()

                        try:
                            # Send OTP to the user's registered email
                            send_reset_otp(recipient_email, otp)
                            st.session_state.reset_otp_last_sent = time.time()

                            # Store OTP hash after successful email delivery
                            st.session_state.reset_otp_hash = (
                                hashlib.sha256(otp.encode()).hexdigest()
                            )

                            st.session_state.reset_otp_email = (
                                recipient_email
                            )

                            st.session_state.reset_otp_expiry = (
                                time.time() + 120
                            )

                            st.session_state.reset_otp_attempts = 0
                            st.session_state.reset_otp_verified = False

                            st.session_state.pop(
                                "dev_reset_otp",
                                None
                            )

                            st.success(
                                "OTP sent successfully! "
                                "Please check your registered email."
                            )

                            st.caption(
                                "Your OTP is valid for 2 minutes."
                            )

                        except Exception:
                            st.error(
                                "Unable to send OTP. Please try again "
                                "or check your email configuration."
                            )
                # ================= VERIFY OTP =================

                if st.session_state.get("reset_otp_hash"):

                    st.divider()
                    st.subheader("Verify OTP")

                    entered_otp = st.text_input(
                        "Enter 6-digit OTP",
                        max_chars=6,
                        key="entered_reset_otp"
                    )

                    if st.button(
                        "Verify OTP",
                        use_container_width=True,
                        key="verify_otp"
                    ):

                        if not entered_otp:
                            st.warning("Please enter the OTP.")

                        elif time.time() > st.session_state.reset_otp_expiry:
                            st.error(
                                "OTP expired. Generate a new one."
                            )

                        elif st.session_state.reset_otp_attempts >= 5:
                            st.error(
                                "Too many incorrect attempts. "
                                "Generate a new OTP."
                            )

                        else:
                            entered_hash = hashlib.sha256(
                                entered_otp.encode()
                            ).hexdigest()

                            if hmac.compare_digest(
                                entered_hash,
                                st.session_state.reset_otp_hash
                            ):
                                st.session_state.reset_otp_verified = True
                                st.success(
                                    "OTP verified successfully!"
                                )

                            else:
                                st.session_state.reset_otp_attempts += 1
                                st.error(
                                    "Incorrect OTP. Please try again."
                                )

                # ================= CREATE NEW PASSWORD =================

                if st.session_state.get(
                    "reset_otp_verified",
                    False
                ):

                    if time.time() > st.session_state.reset_otp_expiry:

                        st.session_state.reset_otp_verified = False
                        st.error(
                            "OTP expired. Generate a new one."
                        )

                    else:

                        st.divider()
                        st.subheader("Create New Password")

                        new_password = st.text_input(
                            "New Password",
                            type="password",
                            key="new_reset_password"
                        )

                        confirm_password = st.text_input(
                            "Confirm New Password",
                            type="password",
                            key="confirm_reset_password"
                        )

                        if st.button(
                            "Reset Password",
                            use_container_width=True,
                            key="reset_password_button"
                        ):

                            if (
                                not new_password
                                or not confirm_password
                            ):
                                st.warning(
                                    "Please fill in both password fields."
                                )

                            elif new_password != confirm_password:
                                st.error("Passwords do not match.")

                            else:
                                errors = validate_password(new_password)

                                if errors:
                                    for error in errors:
                                        st.warning(error)

                                else:
                                    try:
                                        success = reset_password(
                                            st.session_state.reset_otp_email,
                                            new_password
                                        )

                                        if success:
                                            st.success(
                                                "Password reset successfully!"
                                            )

                                            for key in [
                                                "reset_otp_hash",
                                                "reset_otp_email",
                                                "reset_otp_expiry",
                                                "reset_otp_attempts",
                                                "reset_otp_verified",
                                                "dev_reset_otp",
                                                "entered_reset_otp",
                                                "new_reset_password",
                                                "confirm_reset_password"
                                            ]:
                                                st.session_state.pop(
                                                    key,
                                                    None
                                                )

                                            st.session_state.auth_view = "login"
                                            st.rerun()

                                        else:
                                            st.error(
                                                "Unable to reset password."
                                            )

                                    except Exception as e:
                                        st.error(
                                            f"Password reset failed: {e}"
                                        )
