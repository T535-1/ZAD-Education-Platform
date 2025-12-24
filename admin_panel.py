
import streamlit as st
from models import get_db_session, School, User, Subscription
from core.auth import register_user

def show_admin_panel():
    """
    Renders the admin panel for managing schools, users, and subscriptions.
    Accessible only by users with an 'admin' role.
    """
    st.header("Admin Panel")

    if st.session_state.get('user_role') != 'admin':
        st.error("You do not have permission to access this page.")
        return

    session = get_db_session()

    # --- School Management ---
    st.subheader("Manage Schools")
    school_name = st.text_input("New School Name")
    if st.button("Add School"):
        if school_name:
            new_school = School(name=school_name)
            session.add(new_school)
            session.commit()
            st.success(f"School '{school_name}' added.")
            st.rerun()
        else:
            st.warning("Please enter a school name.")

    schools = session.query(School).all()
    st.write("Existing Schools:")
    for school in schools:
        st.write(f"- {school.name} (ID: {school.id})")

    # --- User Management ---
    st.subheader("Manage Users")
    with st.form("new_user_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["student", "teacher", "admin"])
        school_id = st.selectbox("School", [s.id for s in schools], format_func=lambda id: next(s.name for s in schools if s.id == id))
        submitted = st.form_submit_button("Create User")
        if submitted:
            success, message = register_user(username, password, role, school_id)
            if success:
                st.success(message)
            else:
                st.error(message)

    # --- Subscription Management ---
    st.subheader("Manage Subscriptions")
    # This is a simplified view. A real implementation would involve a payment gateway.
    all_schools = session.query(School).all()
    selected_school_sub = st.selectbox("Select School to Update Subscription", all_schools, format_func=lambda s: s.name)
    if selected_school_sub:
        tier = st.selectbox("Subscription Tier", ["free", "pro"], index=0 if selected_school_sub.subscription and selected_school_sub.subscription.tier == 'free' else 1)
        if st.button("Update Subscription"):
            # Create a new subscription or update existing one
            if not selected_school_sub.subscription:
                new_sub = Subscription(tier=tier)
                selected_school_sub.subscription = new_sub
                session.add(new_sub)
            else:
                selected_school_sub.subscription.tier = tier
            session.commit()
            st.success(f"Subscription for '{selected_school_sub.name}' updated to '{tier}'.")

    session.close()
