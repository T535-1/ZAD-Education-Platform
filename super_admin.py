# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Unified Super Admin Dashboard
=======================================================
لوحة المشرف العام الموحدة - God Mode

Features (5 Tabs):
- Tab 1: Schools Management (Create + Admin User)
- Tab 2: Users & Master Key (Search, Reset, Impersonate)
- Tab 3: Bulk Import (CSV/Excel)
- Tab 4: Audit Log (Activity Tracking)
- Tab 5: System Stats
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from werkzeug.security import generate_password_hash

from core.i18n import get_text
from core.database import get_db_session
from models import User, School, Subscription, Grade
from core.audit import log_action, AuditActions, get_audit_logs, format_audit_log_for_display
from core.notifications import notify_password_reset
from core.auth import hash_password


# ============================================================================
# SECURITY CHECK
# ============================================================================

def is_super_admin() -> bool:
    """Check if current user has super admin access."""
    username = st.session_state.get("username", "").lower()
    user_role = st.session_state.get("user_role", "")
    
    if username in ["taha", "admin"] or user_role in ["god_mode", "super_admin", "admin"]:
        return True
    return False


# ============================================================================
# MAIN UNIFIED DASHBOARD
# ============================================================================

def show_super_admin_dashboard():
    """
    Unified Super Admin Dashboard - All Features Combined
    لوحة المشرف العام الموحدة - جميع الميزات في مكان واحد
    """
    
    if not is_super_admin():
        st.error("🚫 Access Denied | الوصول مرفوض")
        st.warning("This dashboard is only accessible to Super Admins.")
        return
    
    st.title("🛡️ Super Admin Dashboard | لوحة المشرف العام")
    
    # Header with gradient
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px 20px; border-radius: 12px; color: white; margin-bottom: 20px;">
        <h4 style="margin: 0;">God Mode - Full System Control</h4>
        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">
            إدارة كاملة للمنصة والمدارس والمستخدمين
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 5 Unified Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏫 Schools | المدارس",
        "👤 Users & Master Key",
        "📥 Bulk Import | الاستيراد",
        "📋 Audit Log | السجل",
        "📊 Stats | الإحصائيات"
    ])
    
    with tab1:
        _render_schools_tab()
    
    with tab2:
        _render_users_tab()
    
    with tab3:
        _render_import_tab()
    
    with tab4:
        _render_audit_tab()
    
    with tab5:
        _render_stats_tab()


# ============================================================================
# TAB 1: SCHOOLS MANAGEMENT
# ============================================================================

def _render_schools_tab():
    """School management with admin user creation."""
    st.subheader("🏫 School Management | إدارة المدارس")
    
    # --- Create New School ---
    with st.expander("➕ Create New School | إنشاء مدرسة جديدة", expanded=True):
        with st.form("create_school_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                school_name = st.text_input("School Name | اسم المدرسة", placeholder="Modern Academy")
                admin_username = st.text_input("Admin Username | اسم مستخدم المدير", placeholder="school_admin")
            
            with col2:
                plan_type = st.selectbox(
                    "Plan | الخطة",
                    options=["free", "pro", "enterprise"],
                    format_func=lambda x: {"free": "🆓 Free", "pro": "⭐ Pro", "enterprise": "🏆 Enterprise"}[x]
                )
                admin_password = st.text_input("Admin Password | كلمة المرور", type="password", value="123456")
            
            if st.form_submit_button("➕ Create School | إنشاء", type="primary", use_container_width=True):
                if school_name and admin_username:
                    _create_school(school_name, plan_type, admin_username, admin_password)
                else:
                    st.warning("⚠️ Fill all fields!")
    
    st.markdown("---")
    
    # --- Schools Table ---
    st.subheader("📋 Existing Schools | المدارس الحالية")
    
    session = get_db_session()
    try:
        schools = session.query(School).all()
        
        if schools:
            data = []
            for s in schools:
                user_count = session.query(User).filter(User.school_id == s.id).count()
                sub = session.query(Subscription).filter(Subscription.school_id == s.id).first()
                data.append({
                    "ID": s.id,
                    "Name | الاسم": s.name,
                    "Plan | الخطة": s.subscription_plan or (sub.subscription_plan if sub else "N/A"),
                    "Users | المستخدمين": user_count,
                    "Created | تاريخ": s.created_at.strftime('%Y-%m-%d') if s.created_at else "N/A"
                })
            
            st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No schools yet. Create one above!")
    finally:
        session.close()


def _create_school(name: str, plan: str, admin_username: str, admin_password: str):
    """Create school with admin user."""
    session = get_db_session()
    
    try:
        if session.query(School).filter(School.name == name).first():
            st.error("❌ School name already exists!")
            return
        
        if session.query(User).filter(User.username == admin_username).first():
            st.error("❌ Username already exists!")
            return
        
        # Create school
        new_school = School(name=name, subscription_plan=plan)
        session.add(new_school)
        session.flush()
        
        # Create subscription
        subscription = Subscription(
            subscription_plan=plan,
            is_active=True,
            school_id=new_school.id
        )
        session.add(subscription)
        
        # Create admin user
        admin = User(
            username=admin_username,
            hashed_password=hash_password(admin_password),
            full_name=f"Admin - {name}",
            role='admin',
            school_id=new_school.id,
            is_active=True
        )
        session.add(admin)
        session.commit()
        
        log_action(
            action=AuditActions.SCHOOL_CREATE,
            user_id=st.session_state.get('user_id'),
            target_type='school',
            target_id=new_school.id,
            details=f"Created school: {name} with admin: {admin_username}"
        )
        
        st.success(f"✅ School '{name}' created with admin '{admin_username}'!")
        st.rerun()
        
    except Exception as e:
        session.rollback()
        st.error(f"❌ Error: {e}")
    finally:
        session.close()


# ============================================================================
# TAB 2: USERS & MASTER KEY
# ============================================================================

def _render_users_tab():
    """Users search, password reset, and impersonation."""
    st.subheader("👤 Users & Master Key | المستخدمين والمفتاح الرئيسي")
    
    search_query = st.text_input("🔍 Search by Email/Username/Name", placeholder="Enter to search...")
    
    session = get_db_session()
    try:
        if search_query:
            users = session.query(User).filter(
                (User.email.ilike(f"%{search_query}%")) |
                (User.username.ilike(f"%{search_query}%")) |
                (User.full_name.ilike(f"%{search_query}%"))
            ).limit(20).all()
        else:
            users = session.query(User).limit(50).all()
        
        if not users:
            st.info("No users found.")
            return
        
        st.markdown("---")
        
        for user in users:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    role_emoji = {'super_admin': '🛡️', 'admin': '🏫', 'teacher': '👨‍🏫', 'student': '🎓', 'parent': '👨‍👩‍👧'}.get(user.role, '👤')
                    school_name = user.school.name if user.school else "System"
                    st.markdown(f"**{role_emoji} {user.full_name or user.username}**")
                    st.caption(f"@{user.username} | 🏫 {school_name}")
                
                with col2:
                    st.markdown(f"`{user.role}`")
                    st.caption(f"ID: {user.id}")
                
                with col3:
                    if st.button("🔑 Reset", key=f"reset_{user.id}"):
                        st.session_state[f"show_reset_{user.id}"] = True
                    
                    if st.session_state.get(f"show_reset_{user.id}"):
                        new_pwd = st.text_input("New Password", type="password", key=f"pwd_{user.id}")
                        if st.button("✅ Confirm", key=f"confirm_{user.id}"):
                            if new_pwd and len(new_pwd) >= 6:
                                _reset_password(user.id, new_pwd)
                                st.session_state[f"show_reset_{user.id}"] = False
                                st.rerun()
                
                with col4:
                    if user.id != st.session_state.get('user_id'):
                        if st.button("🎭 Login As", key=f"imp_{user.id}"):
                            _impersonate_user(user)
                            st.rerun()
                
                st.markdown("---")
    finally:
        session.close()


def _reset_password(user_id: int, new_password: str):
    """Reset user password."""
    session = get_db_session()
    try:
        user = session.query(User).get(user_id)
        if user:
            user.hashed_password = hash_password(new_password)
            session.commit()
            
            log_action(
                action=AuditActions.PASSWORD_RESET,
                user_id=st.session_state.get('user_id'),
                target_type='user',
                target_id=user_id,
                details=f"Password reset for {user.username}"
            )
            notify_password_reset(user_id)
            st.success(f"✅ Password reset for {user.username}")
    except Exception as e:
        session.rollback()
        st.error(f"❌ Error: {e}")
    finally:
        session.close()


def _impersonate_user(user):
    """Impersonate a user."""
    st.session_state['original_user_id'] = st.session_state.get('user_id')
    st.session_state['original_role'] = st.session_state.get('user_role')
    st.session_state['original_username'] = st.session_state.get('username')
    st.session_state['is_impersonating'] = True
    
    st.session_state['user_id'] = user.id
    st.session_state['user_role'] = user.role
    st.session_state['username'] = user.username
    st.session_state['school_id'] = user.school_id
    
    log_action(
        action=AuditActions.IMPERSONATE_START,
        user_id=st.session_state.get('original_user_id'),
        target_type='user',
        target_id=user.id,
        details=f"Impersonating {user.username}"
    )
    st.success(f"🎭 Now logged in as: {user.username}")


# ============================================================================
# TAB 3: BULK IMPORT
# ============================================================================

def _render_import_tab():
    """Bulk data import."""
    st.subheader("📥 Bulk Import | الاستيراد الجماعي")
    
    session = get_db_session()
    schools = session.query(School).all()
    session.close()
    
    if not schools:
        st.warning("⚠️ Create a school first.")
        return
    
    school_opts = {f"{s.name}": s.id for s in schools}
    selected_school = st.selectbox("🏫 Target School", list(school_opts.keys()))
    school_id = school_opts[selected_school]
    
    import_type = st.radio("Import Type", ["👤 Users", "📝 Grades"], horizontal=True)
    
    # Template download
    with st.expander("📋 Download Template"):
        if import_type.startswith("👤"):
            template = "username,email,full_name,role,password\nstudent1,s1@school.edu,Ahmed Ali,student,123456"
            st.download_button("📥 User Template", template, "users_template.csv", "text/csv")
        else:
            template = "student_email,subject,score,max_score,feedback\ns1@school.edu,Math,85,100,Good work"
            st.download_button("📥 Grades Template", template, "grades_template.csv", "text/csv")
    
    uploaded = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
    
    if uploaded:
        try:
            df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
            st.dataframe(df, use_container_width=True)
            
            if st.button("🚀 Import", type="primary", use_container_width=True):
                if import_type.startswith("👤"):
                    result = _import_users(df, school_id)
                    st.success(f"✅ Imported {result['success']} users! Skipped: {result['skipped']}")
                else:
                    st.info("Grade import coming soon!")
        except Exception as e:
            st.error(f"❌ Error: {e}")


def _import_users(df: pd.DataFrame, school_id: int) -> dict:
    """Import users from DataFrame."""
    session = get_db_session()
    result = {'success': 0, 'skipped': 0, 'errors': []}
    
    try:
        for idx, row in df.iterrows():
            username = str(row.get('username', '')).strip()
            email = str(row.get('email', '')).strip()
            full_name = str(row.get('full_name', '')).strip()
            role = str(row.get('role', 'student')).strip().lower()
            password = str(row.get('password', '123456')).strip()
            
            if session.query(User).filter((User.email == email) | (User.username == username)).first():
                result['skipped'] += 1
                continue
            
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=hash_password(password),
                role=role,
                school_id=school_id,
                is_active=True
            )
            session.add(new_user)
            result['success'] += 1
        
        session.commit()
        
        log_action(
            action=AuditActions.BULK_IMPORT,
            user_id=st.session_state.get('user_id'),
            details=f"Imported {result['success']} users"
        )
        
    except Exception as e:
        session.rollback()
        result['errors'].append(str(e))
    finally:
        session.close()
    
    return result


# ============================================================================
# TAB 4: AUDIT LOG
# ============================================================================

def _render_audit_tab():
    """Audit log viewer."""
    st.subheader("📋 Audit Log | سجل النشاطات")
    
    col1, col2 = st.columns(2)
    with col1:
        action_filter = st.selectbox("Filter by Action", ["All", "LOGIN", "PASSWORD_RESET", "IMPERSONATE_START", "SCHOOL_CREATE"])
    with col2:
        limit = st.number_input("Max Records", 10, 500, 50)
    
    action = None if action_filter == "All" else action_filter
    logs = get_audit_logs(action=action, limit=limit)
    
    if logs:
        for log in logs:
            fmt = format_audit_log_for_display(log)
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"### {fmt['icon']}")
            with col2:
                st.markdown(f"**{fmt['label']}** | 🕐 {fmt['timestamp']}")
                if fmt['details']:
                    st.caption(fmt['details'][:100])
            st.markdown("---")
    else:
        st.info("No logs found.")


# ============================================================================
# TAB 5: SYSTEM STATS
# ============================================================================

def _render_stats_tab():
    """System statistics."""
    st.subheader("📊 System Statistics | إحصائيات النظام")
    
    session = get_db_session()
    try:
        schools_count = session.query(School).count()
        users_count = session.query(User).count()
        teachers = session.query(User).filter(User.role == 'teacher').count()
        students = session.query(User).filter(User.role == 'student').count()
        grades_count = session.query(Grade).count()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏫 Total Schools", schools_count)
            st.metric("👨‍🏫 Teachers", teachers)
        with col2:
            st.metric("👥 Total Users", users_count)
            st.metric("🎓 Students", students)
        with col3:
            st.metric("📝 Total Grades", grades_count)
        
    finally:
        session.close()


# Backward compatibility
def show_admin_dashboard():
    """Alias for backward compatibility."""
    show_super_admin_dashboard()
