
import streamlit as st
from core.i18n import get_text
from core.auth import login, register_user
# CORRECTED: Import get_db_session from its new, correct location
from core.database import get_db_session 
from models import School # We still need the School model for the query

def show_login_form():
    """
    Displays a complete, bilingual login and registration form.
    This function will control the entire screen until the user is authenticated.
    """
    st.title(get_text("app_title"))
    st.markdown(get_text("welcome_message"))

    login_tab, register_tab = st.tabs([get_text("login_tab"), get_text("register_tab")])

    # --- Login Tab ---
    with login_tab:
        with st.form("login_form"):
            username = st.text_input(get_text("username_label"))
            password = st.text_input(get_text("password_label"), type="password")
            submitted = st.form_submit_button(get_text("login_button"))
            
            if submitted:
                if login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    # --- Registration Tab ---
    with register_tab:
        with st.form("register_form"):
            reg_username = st.text_input(get_text("username_label"), key="reg_user")
            reg_password = st.text_input(get_text("password_label"), type="password", key="reg_pass")
            
            # This logic now works because the DB is guaranteed to be initialized by Home.py
            session = get_db_session()
            schools = session.query(School).all()
            session.close()
            
            if not schools:
                # This warning should ideally not appear anymore due to the self-healing startup
                st.warning("No schools available for registration. Please contact support.")
            else:
                school_map = {s.name: s.id for s in schools}
                selected_school_name = st.selectbox(get_text("school_label"), options=list(school_map.keys()))

                reg_submitted = st.form_submit_button(get_text("register_tab"))
                
                if reg_submitted:
                    school_id = school_map[selected_school_name]
                    success, message = register_user(reg_username, reg_password, "student", school_id)
                    if success:
                        st.success("Registration successful! Please log in.")
                    else:
                        st.error(f"Registration failed: {message}")
