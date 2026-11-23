import streamlit as st
from html import escape
import base64
from pathlib import Path

from database.database import get_connection
from auth.authentication import (
    verify_password,
    hash_password,
    validate_password,
)


def show_profile():
    # ================= USER DETAILS =================

    user_id = st.session_state.get("user_id")
    user_name = st.session_state.get("user_name", "User")
    user_email = st.session_state.get("user_email", "")
    user_role = st.session_state.get("user_role", "user")

    initials = "".join(
        word[0].upper()
        for word in user_name.split()
        if word
    )[:2] or "U"

    safe_name = escape(user_name)
    safe_email = escape(user_email)
        # ================= PROFILE BANNER BACKGROUND IMAGE =================

    profile_image_path = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "pfp.png"
    )

    profile_background_style = ""

    if profile_image_path.exists():

        with open(profile_image_path, "rb") as image_file:
            profile_image_data = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        profile_background_style = f"""
            background-image:
                linear-gradient(
                    rgba(244, 251, 252, 0.35),
                    rgba(221, 248, 250, 0.35)
                ),
                url('data:image/png;base64,{profile_image_data}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        """

    role_display = (
        "Administrator" if user_role == "admin"
        else "Standard User"
    )

    # ================= ACCOUNT STATUS =================

    account_status = "Active"

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT status
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
                )

                result = cursor.fetchone()

                if result and result[0]:
                    account_status = str(result[0]).capitalize()

    except Exception:
        account_status = "Active"

    # ================= PAGE STYLING =================

    st.html("""
    <style>
        .profile-heading {
            color: #07566B;
            font-size: 32px;
            font-weight: 750;
            margin-bottom: 5px;
        }

        .profile-subheading {
            color: #55717A;
            font-size: 14px;
            margin-bottom: 22px;
        }

        .profile-banner {
            background: linear-gradient(
                120deg,
                #F4FBFC,
                #DDF8FA
            );
            border: 1px solid #C8E9ED;
            border-radius: 18px;
            padding: 30px;
            margin: 15px 0 25px 0;
            display: flex;
            align-items: center;
            gap: 25px;
        }

        .profile-avatar {
            width: 110px;
            height: 110px;
            min-width: 110px;
            border-radius: 50%;
            background: #A8E9EF;
            color: #07566B;
            font-size: 48px;
            font-weight: 750;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .profile-name {
            color: #07566B;
            font-size: 30px;
            font-weight: 750;
            margin-bottom: 5px;
        }

        .profile-email {
            color: #183D49;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
        }

        .profile-role {
            display: inline-block;
            background: #BFECEF;
            color: #07566B;
            padding: 7px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 650;
        }

        .profile-card {
            background: #FFFFFF;
            border: 1px solid #DCE8EC;
            border-radius: 17px;
            padding: 24px;
            margin-bottom: 22px;
        }

        .profile-card-title {
            color: #07566B;
            font-size: 21px;
            font-weight: 700;
            padding-bottom: 15px;
            border-bottom: 1px solid #DCE8EC;
            margin-bottom: 15px;
        }

        .profile-info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 5px;
            gap: 15px;
        }

        .profile-info-label {
            color: #55717A;
            font-size: 15px;
        }

        .profile-info-value {
            color: #263D49;
            font-size: 15px;
            font-weight: 600;
            text-align: right;
            overflow-wrap: anywhere;
        }

        .profile-status {
            background: #DDF8ED;
            color: #087B51;
            border-radius: 20px;
            padding: 6px 14px;
            font-weight: 650;
            font-size: 13px;
        }

        .profile-security-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 15px;
            padding: 8px 0;
        }

        .profile-password-title {
            color: #07566B;
            font-size: 17px;
            font-weight: 650;
        }

        .profile-password-subtitle {
            color: #55717A;
            font-size: 13px;
            margin-top: 4px;
        }

        @media (max-width: 600px) {
            .profile-banner {
                padding: 20px;
                gap: 15px;
            }

            .profile-avatar {
                width: 75px;
                height: 75px;
                min-width: 75px;
                font-size: 32px;
            }

            .profile-name {
                font-size: 22px;
            }

            .profile-card {
                padding: 17px;
            }
        }
    </style>
    """)

    # ================= PAGE HEADER =================

    st.markdown(
        '<div class="profile-heading">My Profile</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="profile-subheading">'
        'Manage your account details and preferences.'
        '</div>',
        unsafe_allow_html=True
    )

    # ================= ACTIVE STATUS =================

    status_color = (
        "#087B51"
        if account_status.lower() == "active"
        else "#B45309"
    )

    status_background = (
        "#DDF8ED"
        if account_status.lower() == "active"
        else "#FEF3C7"
    )

    st.html(f"""
    <div style="
        display:flex;
        justify-content:flex-end;
        margin-bottom:10px;
    ">
        <span style="
            background:{status_background};
            color:{status_color};
            padding:8px 17px;
            border-radius:22px;
            font-weight:650;
            font-size:14px;
        ">
            ● &nbsp; {escape(account_status)}
        </span>
    </div>
    """)

    # ================= PROFILE BANNER =================

    st.html(f"""
    <div class="profile-banner" style="{profile_background_style}">
        <div class="profile-avatar">
            {escape(initials)}
        </div>

        <div>
            <div class="profile-name">
                {safe_name}
            </div>

            <div class="profile-email">
                {safe_email}
            </div>

            <span class="profile-role">
                {escape(role_display)}
            </span>
        </div>
    </div>
    """)

    # ================= PERSONAL INFORMATION =================

    st.html(f"""
    <div class="profile-card">

        <div class="profile-card-title">
            👤 &nbsp; Personal Information
        </div>

        <div class="profile-info-row">
            <span class="profile-info-label">
                Full Name
            </span>

            <span class="profile-info-value">
                {safe_name}
            </span>
        </div>

        <div class="profile-info-row">
            <span class="profile-info-label">
                Email
            </span>

            <span class="profile-info-value">
                {safe_email}
            </span>
        </div>

        <div class="profile-info-row">
            <span class="profile-info-label">
                Account Status
            </span>

            <span class="profile-status">
                {escape(account_status)}
            </span>
        </div>

    </div>
    """)

    # ================= EDIT PROFILE BUTTON =================

    edit_col, empty_col = st.columns([1, 2])

    with edit_col:
        if st.button(
            "✏️ Edit Profile",
            use_container_width=True,
            key="profile_edit_button"
        ):
            st.session_state.profile_action = "edit"

    # ================= EDIT PROFILE FORM =================

    if st.session_state.get("profile_action") == "edit":

        st.subheader("Edit Profile")

        with st.form("edit_profile_form"):

            new_name = st.text_input(
                "Full Name",
                value=user_name
            )

            save_profile = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if save_profile:

                new_name = new_name.strip()

                if not new_name:
                    st.error("Name cannot be empty.")

                elif len(new_name) > 100:
                    st.error("Name must be 100 characters or fewer.")

                else:

                    try:
                        with get_connection() as conn:
                            with conn.cursor() as cursor:

                                cursor.execute(
                                    """
                                    UPDATE users
                                    SET name = %s
                                    WHERE id = %s
                                    """,
                                    (new_name, user_id)
                                )

                        st.session_state.user_name = new_name
                        st.session_state.profile_action = None

                        st.success("Profile updated successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(
                            f"Unable to update profile: {e}"
                        )

    # ================= SECURITY / PASSWORD =================

    st.html("""
    <div class="profile-card">

        <div class="profile-card-title">
            🔒 &nbsp; Security
        </div>

        <div class="profile-security-row">

            <div>
                <div class="profile-password-title">
                    Password
                </div>

                <div class="profile-password-subtitle">
                    Keep your account secure
                </div>
            </div>

        </div>

    </div>
    """)

    password_col, empty_col = st.columns([1, 2])

    with password_col:

        if st.button(
            "🔑 Change Password",
            use_container_width=True,
            key="profile_password_button"
        ):
            st.session_state.profile_action = "password"


    # ================= CHANGE PASSWORD FORM =================

    if st.session_state.get("profile_action") == "password":

        st.subheader("Change Password")

        with st.form("change_password_form"):

            current_password = st.text_input(
                "Current Password",
                type="password"
            )

            new_password = st.text_input(
                "New Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm New Password",
                type="password"
            )

            update_password = st.form_submit_button(
                "Update Password",
                use_container_width=True
            )

            if update_password:

                if not current_password or not new_password or not confirm_password:
                    st.error("Please fill in all password fields.")

                elif new_password != confirm_password:
                    st.error("New passwords do not match.")

                else:

                    try:
                        password_updated = False

                        with get_connection() as conn:
                            with conn.cursor() as cursor:

                                cursor.execute(
                                    """
                                    SELECT password
                                    FROM users
                                    WHERE id = %s
                                    """,
                                    (user_id,)
                                )

                                result = cursor.fetchone()

                                if not result:
                                    st.error("User account not found.")

                                elif not verify_password(
                                    current_password,
                                    result[0]
                                ):
                                    st.error("Current password is incorrect.")

                                else:

                                    errors = validate_password(new_password)

                                    if errors:
                                        for error in errors:
                                            st.error(error)

                                    else:

                                        new_hash = hash_password(new_password)

                                        cursor.execute(
                                            """
                                            UPDATE users
                                            SET password = %s
                                            WHERE id = %s
                                            """,
                                            (new_hash, user_id)
                                        )

                                        conn.commit()
                                        password_updated = True

                        if password_updated:

                            st.session_state.profile_action = None

                            st.success("Password changed successfully!")

                            st.rerun()

                    except Exception as e:
                        st.error(f"Unable to change password: {e}")

    # ================= LOGOUT =================
    st.divider()
    if st.button(
        "🚪 Logout",
        use_container_width=True,
        key="profile_logout",
        type="secondary"
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.session_state.user_role = "user"
        st.session_state.show_profile = False
        st.session_state.profile_action = None

        st.rerun()
