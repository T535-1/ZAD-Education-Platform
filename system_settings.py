# -*- coding: utf-8 -*-
"""
System Settings Panel - ZAD Education Platform
Super Developer control panel for platform administration
"""

import streamlit as st
import os
from datetime import datetime
from pathlib import Path

from core.i18n import get_text
from models import SessionLocal, User, School, Subscription


def show_system_settings():
    """
    Super Developer System Settings Panel
    Only accessible to users with 'God Mode' (username: Taha)
    """
    st.title("⚙️ System Settings | إعدادات النظام")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px;
                border: 1px solid #0f3460;">
        <h3 style="margin: 0; color: #e94560;">🔧 Super Developer Control Panel</h3>
        <p style="margin: 10px 0 0 0; opacity: 0.8;">
            Full system control and configuration
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different settings
    tabs = st.tabs([
        "📊 System Status",
        "👥 User Management", 
        "🏫 School Settings",
        "🔐 Security",
        "🗄️ Database",
        "📝 Logs"
    ])
    
    # Tab 1: System Status
    with tabs[0]:
        show_system_status()
    
    # Tab 2: User Management
    with tabs[1]:
        show_user_management()
    
    # Tab 3: School Settings
    with tabs[2]:
        show_school_settings()
    
    # Tab 4: Security
    with tabs[3]:
        show_security_settings()
    
    # Tab 5: Database
    with tabs[4]:
        show_database_settings()
    
    # Tab 6: Logs
    with tabs[5]:
        show_logs()


def show_system_status():
    """Display system status and metrics"""
    st.subheader("📊 System Status | حالة النظام")
    
    col1, col2, col3, col4 = st.columns(4)
    
    session = SessionLocal()
    try:
        users_count = session.query(User).count()
        schools_count = session.query(School).count()
        active_subs = session.query(Subscription).filter(Subscription.is_active == True).count()
    finally:
        session.close()
    
    with col1:
        st.metric("👥 Total Users", users_count)
    with col2:
        st.metric("🏫 Total Schools", schools_count)
    with col3:
        st.metric("✅ Active Subscriptions", active_subs)
    with col4:
        st.metric("🟢 System Status", "Online")
    
    st.markdown("---")
    
    # System Info
    st.subheader("ℹ️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Platform:** ZAD Education Platform  
        **Version:** 1.0.0  
        **Environment:** Development  
        **Database:** SQLite  
        """)
    
    with col2:
        st.markdown(f"""
        **Server Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
        **Python Version:** {os.sys.version.split()[0]}  
        **Working Directory:** {os.getcwd()}  
        """)


def show_user_management():
    """User management interface"""
    st.subheader("👥 User Management | إدارة المستخدمين")
    
    session = SessionLocal()
    try:
        users = session.query(User).all()
        
        if users:
            # Display users table
            user_data = []
            for user in users:
                user_data.append({
                    "ID": user.id,
                    "Username": user.username,
                    "Role": user.role,
                    "Active": "✅" if user.is_active else "❌",
                    "Created": user.created_at.strftime('%Y-%m-%d') if user.created_at else "N/A"
                })
            
            st.dataframe(user_data, use_container_width=True)
        else:
            st.info("No users found")
        
        # Add new user form
        st.markdown("---")
        st.subheader("➕ Add New User")
        
        with st.form("add_user_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_username = st.text_input("Username")
            with col2:
                new_password = st.text_input("Password", type="password")
            with col3:
                new_role = st.selectbox("Role", ["student", "teacher", "admin"])
            
            if st.form_submit_button("Create User", use_container_width=True):
                if new_username and new_password:
                    try:
                        from core.auth import hash_password
                        school = session.query(School).first()
                        
                        new_user = User(
                            username=new_username,
                            hashed_password=hash_password(new_password),
                            role=new_role,
                            school_id=school.id if school else 1,
                            is_active=True
                        )
                        session.add(new_user)
                        session.commit()
                        st.success(f"✅ User '{new_username}' created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please fill all fields")
    finally:
        session.close()


def show_school_settings():
    """School settings interface"""
    st.subheader("🏫 School Settings | إعدادات المدرسة")
    
    session = SessionLocal()
    try:
        schools = session.query(School).all()
        
        if schools:
            for school in schools:
                with st.expander(f"📍 {school.name}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {school.id}")
                        st.write(f"**Created:** {school.created_at.strftime('%Y-%m-%d') if school.created_at else 'N/A'}")
                    
                    with col2:
                        # Get subscription
                        sub = session.query(Subscription).filter(
                            Subscription.school_id == school.id
                        ).first()
                        
                        if sub:
                            st.write(f"**Plan:** {sub.subscription_plan.title()}")
                            st.write(f"**Active:** {'✅ Yes' if sub.is_active else '❌ No'}")
        else:
            st.info("No schools found")
    finally:
        session.close()


def show_security_settings():
    """Security settings"""
    st.subheader("🔐 Security Settings | إعدادات الأمان")
    
    st.warning("⚠️ Security settings should be handled via environment variables (.env file)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔑 Password Policy
        - Minimum 8 characters
        - Must contain uppercase
        - Must contain lowercase
        - Must contain number
        """)
    
    with col2:
        st.markdown("""
        ### 🛡️ Rate Limiting
        - Login: 5 attempts / 5 min
        - API: 100 requests / min
        - Lockout: 15 minutes
        """)
    
    st.markdown("---")
    st.subheader("🔒 Session Management")
    
    if st.button("🚪 Force Logout All Users", type="secondary"):
        st.info("This feature requires session store implementation (Redis)")


def show_database_settings():
    """Database management"""
    st.subheader("🗄️ Database Management | إدارة قاعدة البيانات")
    
    # Database info
    db_file = Path("zad_edu.db")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Database Type", "SQLite")
    with col2:
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            st.metric("Database Size", f"{size_mb:.2f} MB")
        else:
            st.metric("Database Size", "N/A")
    with col3:
        st.metric("Status", "🟢 Connected")
    
    st.markdown("---")
    
    # Database actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Backup Database", use_container_width=True):
            try:
                import shutil
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy("zad_edu.db", backup_name)
                st.success(f"✅ Backup created: {backup_name}")
            except Exception as e:
                st.error(f"Backup failed: {e}")
    
    with col2:
        if st.button("📊 Run Migrations", use_container_width=True):
            st.info("Run: alembic upgrade head")
    
    with col3:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache cleared!")


def show_logs():
    """Display system logs"""
    st.subheader("📝 System Logs | سجلات النظام")
    
    log_file = Path("logs/zad_edu.log")
    
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()[-100:]  # Last 100 lines
            
            st.text_area("Recent Logs", value="".join(logs), height=400)
            
            if st.button("📥 Download Full Log"):
                st.download_button(
                    "Download",
                    data=open(log_file, 'r').read(),
                    file_name="zad_edu.log",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"Error reading logs: {e}")
    else:
        st.info("📭 No log file found. Logs will appear here once the system starts logging.")
        
        # Create sample log display
        st.code("""
[2025-12-22 03:30:00] INFO - ZAD Education Platform started
[2025-12-22 03:30:01] INFO - Database connection established
[2025-12-22 03:30:02] INFO - User 'Taha' logged in (God Mode)
        """)
