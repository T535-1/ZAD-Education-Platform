# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Main Application | منصة زاد - التطبيق الرئيسي
======================================================================
Main entry point with:
1. Language Toggle (Arabic/English) - زر تبديل اللغة
2. Role-based Dashboards (Admin, Teacher, Student, Parent)
3. Impersonation Exit

ROLES:
- super_admin / school_admin: Full admin dashboard
- teacher: Vision Grader, Library, Online Classes
- student: Grades, Resources, Upcoming Classes
- parent: View children's grades
"""

import streamlit as st
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

# Configure Streamlit page (MUST be first)
st.set_page_config(
    page_title="ZAD | منصة زاد التعليمية",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

from models import get_db_session, User, Grade, Resource, OnlineSession, init_db, Base, engine
from core.i18n import t, get_language, set_language, render_language_toggle


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def create_default_super_admin():
    """Create default super admin if not exists."""
    session = get_db_session()
    try:
        admin = session.query(User).filter(User.email == "admin@zad.edu").first()
        if not admin:
            admin = User(
                email="admin@zad.edu",
                full_name="Super Admin",
                hashed_password=generate_password_hash("admin123"),
                role="super_admin",
                is_active=True,
                school_id=None
            )
            session.add(admin)
            session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main application entry point."""
    
    # Initialize database (once)
    if 'db_initialized' not in st.session_state:
        init_db()
        create_default_super_admin()
        st.session_state['db_initialized'] = True
    
    # Check authentication
    if not st.session_state.get('logged_in'):
        show_login_page()
    else:
        show_main_application()


# =============================================================================
# LOGIN PAGE
# =============================================================================

def show_login_page():
    """Display the login page with language toggle."""
    
    # Language toggle at top
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col3:
            render_language_toggle()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"# {t('app_title')}")
        st.markdown(f"### {t('login')}")
        
        with st.form("login_form"):
            email = st.text_input(
                t("email"),
                placeholder="admin@zad.edu"
            )
            password = st.text_input(
                t("password"),
                type="password",
                placeholder="••••••••"
            )
            
            login_submitted = st.form_submit_button(t("login_button"), use_container_width=True)
            
            if login_submitted and email and password:
                authenticate_user(email, password)
        
        with st.expander(t("demo_credentials")):
            st.code("""
Super Admin:
  Email: admin@zad.edu
  Password: admin123
            """)


def authenticate_user(email: str, password: str):
    """Authenticate user and set session state."""
    session = get_db_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        
        if user and check_password_hash(user.hashed_password, password):
            st.session_state['logged_in'] = True
            st.session_state['user_id'] = user.id
            st.session_state['user_name'] = user.full_name
            st.session_state['email'] = user.email
            st.session_state['role'] = user.role
            st.session_state['school_id'] = user.school_id
            st.session_state['is_impersonating'] = False
            st.success(f"✅ {t('welcome')}, {user.full_name}!")
            st.rerun()
        else:
            st.error("❌ Invalid email or password!")
    finally:
        session.close()


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def show_main_application():
    """Display main app based on role."""
    
    role = st.session_state.get('role')
    user_name = st.session_state.get('user_name')
    is_impersonating = st.session_state.get('is_impersonating', False)
    
    # =========================================================================
    # SIDEBAR
    # =========================================================================
    with st.sidebar:
        # LANGUAGE TOGGLE AT TOP
        st.markdown(f"### 🌐 {t('language')}")
        render_language_toggle()
        st.markdown("---")
        
        # Welcome
        st.markdown(f"### 👋 {t('welcome')}, {user_name}")
        st.caption(f"{t('role')}: `{t(role)}`")
        
        # IMPERSONATION EXIT (Very prominent)
        if is_impersonating:
            st.markdown("---")
            st.error(f"🎭 **{t('impersonation_mode')}**")
            if st.button(t("exit_impersonation"), type="primary", use_container_width=True):
                _exit_impersonation()
                st.rerun()
            st.markdown("---")
        
        # ROLE-BASED MENU
        st.markdown(f"### 📋 {t('role')} Menu")
        
        if role in ['super_admin', 'school_admin', 'admin']:
            menu = st.radio(
                "Admin Menu",
                options=[
                    t("schools"),
                    t("users"),
                    t("statistics")
                ],
                label_visibility="collapsed"
            )
            st.session_state['admin_menu'] = menu
        
        elif role == 'teacher':
            menu = st.radio(
                "Teacher Menu",
                options=[
                    t("vision_grader"),
                    t("library"),
                    t("online_classes")
                ],
                label_visibility="collapsed"
            )
            st.session_state['teacher_menu'] = menu
        
        elif role == 'student':
            menu = st.radio(
                "Student Menu",
                options=[
                    t("my_grades"),
                    t("resources"),
                    t("upcoming_classes")
                ],
                label_visibility="collapsed"
            )
            st.session_state['student_menu'] = menu
        
        elif role == 'parent':
            menu = st.radio(
                "Parent Menu",
                options=[
                    t("my_children"),
                    t("child_grades")
                ],
                label_visibility="collapsed"
            )
            st.session_state['parent_menu'] = menu
        
        st.markdown("---")
        if st.button(t("logout"), use_container_width=True):
            _logout()
            st.rerun()
    
    # =========================================================================
    # MAIN CONTENT ROUTING
    # =========================================================================
    
    if role in ['super_admin', 'school_admin', 'admin']:
        _show_admin_view()
    elif role == 'teacher':
        _show_teacher_view()
    elif role == 'student':
        _show_student_view()
    elif role == 'parent':
        _show_parent_view()
    else:
        st.error(f"❌ Unknown role: {role}")


# =============================================================================
# ADMIN VIEW
# =============================================================================

def _show_admin_view():
    """Admin dashboard view."""
    from views.admin import show_admin_dashboard
    show_admin_dashboard()


# =============================================================================
# TEACHER VIEW
# =============================================================================

def _show_teacher_view():
    """Teacher view with multiple tools."""
    menu = st.session_state.get('teacher_menu', t("vision_grader"))
    
    if t("vision_grader") in menu:
        from views.vision_grader import show_vision_grader
        show_vision_grader()
    else:
        from views.teacher_tools import show_teacher_tools
        show_teacher_tools()


# =============================================================================
# STUDENT VIEW
# =============================================================================

def _show_student_view():
    """Student dashboard with grades, resources, classes."""
    menu = st.session_state.get('student_menu', t("my_grades"))
    
    st.title(t("student_dashboard"))
    
    if t("my_grades") in menu:
        _show_student_grades()
    elif t("resources") in menu:
        _show_student_resources()
    elif t("upcoming_classes") in menu:
        _show_student_classes()


def _show_student_grades():
    """Student grades view."""
    student_id = st.session_state.get('user_id')
    session = get_db_session()
    
    try:
        grades = session.query(Grade).filter(Grade.student_id == student_id).order_by(Grade.graded_at.desc()).all()
        
        if grades:
            for grade in grades:
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    st.markdown(f"**📚 {grade.subject}**")
                with col2:
                    pct = (grade.score / grade.max_score) * 100
                    st.metric("", f"{grade.score:.1f}/{grade.max_score}", f"{pct:.0f}%")
                with col3:
                    if grade.feedback:
                        st.caption(f"💬 {grade.feedback[:60]}...")
                st.markdown("---")
        else:
            st.info(t("no_data"))
    finally:
        session.close()


def _show_student_resources():
    """Student resources view."""
    school_id = st.session_state.get('school_id')
    session = get_db_session()
    
    try:
        resources = session.query(Resource).filter(Resource.school_id == school_id).all()
        
        if resources:
            for res in resources:
                with st.expander(f"📄 {res.title}"):
                    st.write(f"**Subject:** {res.subject}")
                    if res.url:
                        st.markdown(f"🔗 [Open]({res.url})")
        else:
            st.info(t("no_data"))
    finally:
        session.close()


def _show_student_classes():
    """Student upcoming classes view."""
    school_id = st.session_state.get('school_id')
    now = datetime.datetime.utcnow()
    session = get_db_session()
    
    try:
        classes = session.query(OnlineSession).filter(
            OnlineSession.school_id == school_id,
            OnlineSession.scheduled_time >= now
        ).order_by(OnlineSession.scheduled_time.asc()).all()
        
        if classes:
            for cls in classes:
                st.markdown(f"### 🎥 {cls.title}")
                st.write(f"**When:** {cls.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                st.markdown(f"🔗 [Join]({cls.zoom_link})")
                st.markdown("---")
        else:
            st.info(t("no_data"))
    finally:
        session.close()


# =============================================================================
# PARENT VIEW (SECURED!)
# =============================================================================

def _show_parent_view():
    """Parent dashboard to view ONLY their own children's grades."""
    st.title(t("parent_dashboard"))
    
    parent_id = st.session_state.get('user_id')
    
    st.subheader(t("my_children"))
    
    # Import ParentChild for proper access control
    from models import ParentChild
    
    session = get_db_session()
    
    try:
        # SECURITY FIX: Only get children linked to this parent
        parent_child_links = session.query(ParentChild).filter(
            ParentChild.parent_id == parent_id
        ).all()
        
        if not parent_child_links:
            st.info("👨‍👩‍👧 No children linked to your account. Please contact school admin.")
            st.caption("لم يتم ربط أي أطفال بحسابك. يرجى التواصل مع مشرف المدرسة.")
            return
        
        # Get child IDs safely
        child_ids = [link.child_id for link in parent_child_links]
        
        # Fetch only linked children
        students = session.query(User).filter(
            User.id.in_(child_ids),
            User.role == 'student'
        ).all()
        
        if students:
            selected_child = st.selectbox(
                t("my_children"),
                options=[s.full_name for s in students]
            )
            
            selected_student = next((s for s in students if s.full_name == selected_child), None)
            
            if selected_student:
                st.subheader(f"{t('child_grades')}: {selected_student.full_name}")
                
                grades = session.query(Grade).filter(Grade.student_id == selected_student.id).all()
                
                if grades:
                    for grade in grades:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**📚 {grade.subject}**")
                        with col2:
                            pct = (grade.score / grade.max_score) * 100
                            st.metric("", f"{grade.score:.1f}/{grade.max_score}", f"{pct:.0f}%")
                        st.markdown("---")
                else:
                    st.info(t("no_data"))
        else:
            st.info(t("no_data"))
    
    finally:
        session.close()


# =============================================================================
# SESSION HELPERS
# =============================================================================

def _exit_impersonation():
    """Exit impersonation and restore admin session."""
    st.session_state['user_id'] = st.session_state.get('original_user_id')
    st.session_state['role'] = st.session_state.get('original_role')
    st.session_state['user_name'] = st.session_state.get('original_user_name')
    st.session_state['school_id'] = st.session_state.get('original_school_id')
    st.session_state['is_impersonating'] = False
    
    for key in ['original_user_id', 'original_role', 'original_user_name', 'original_school_id']:
        if key in st.session_state:
            del st.session_state[key]


def _logout():
    """Clear all session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    main()
