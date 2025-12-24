# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Teacher Tools | منصة زاد - أدوات المعلم
================================================================
Unified view for teachers to manage:
1. PDF Library / Resources (Upload PDFs, links for students)
2. Online Classes / Zoom Sessions (Schedule classes)

DATABASE WRITE FLOW:
- Resource: Saved to `resources` table with teacher_id, school_id
- OnlineSession: Saved to `online_sessions` table with teacher_id, school_id
"""

import streamlit as st
import datetime
from models import get_db_session, Resource, OnlineSession


def show_teacher_tools():
    """Main entry point for Teacher Tools."""
    
    role = st.session_state.get('role')
    school_id = st.session_state.get('school_id')
    teacher_id = st.session_state.get('user_id')
    teacher_name = st.session_state.get('user_name')
    
    # Access check
    if role != 'teacher':
        st.error("❌ Access Denied. Teachers only.")
        return
    
    st.title("🛠️ Teacher Tools | أدوات المعلم")
    st.caption(f"Welcome, {teacher_name} | مرحباً، {teacher_name}")
    
    # Tab navigation
    tab1, tab2 = st.tabs([
        "📚 PDF Library | المكتبة الرقمية",
        "🎥 Online Classes | الفصول الأونلاين"
    ])
    
    with tab1:
        _render_library_tab(teacher_id, school_id)
    
    with tab2:
        _render_online_classes_tab(teacher_id, school_id)


# =============================================================================
# TAB 1: PDF LIBRARY / RESOURCES
# =============================================================================

def _render_library_tab(teacher_id: int, school_id: int):
    """Upload and manage PDF resources."""
    
    st.subheader("📚 PDF Library | المكتبة الرقمية")
    
    col1, col2 = st.columns([1, 1])
    
    # ----------------------------
    # UPLOAD NEW RESOURCE
    # ----------------------------
    with col1:
        st.markdown("### ➕ Add New Resource | إضافة مورد جديد")
        
        with st.form("upload_resource_form", clear_on_submit=True):
            title = st.text_input(
                "Resource Title | عنوان المورد",
                placeholder="e.g., Math Chapter 5 Notes"
            )
            
            subject = st.selectbox(
                "Subject | المادة",
                options=[
                    "Mathematics | الرياضيات",
                    "Arabic | اللغة العربية",
                    "English | اللغة الإنجليزية",
                    "Science | العلوم",
                    "History | التاريخ",
                    "Geography | الجغرافيا",
                    "Islamic Studies | الدراسات الإسلامية",
                    "Art | الفنون",
                    "General | عام"
                ]
            )
            
            grade_level = st.selectbox(
                "Grade Level | المستوى الدراسي",
                options=[
                    "Grade 1-3 | الصف 1-3",
                    "Grade 4-6 | الصف 4-6",
                    "Grade 7-9 | الصف 7-9",
                    "Grade 10-12 | الصف 10-12",
                    "University | جامعي",
                    "All Levels | كل المستويات"
                ]
            )
            
            resource_type = st.radio(
                "Resource Type | نوع المورد",
                options=["🔗 URL / Link", "📄 File Path"],
                horizontal=True
            )
            
            if resource_type == "🔗 URL / Link":
                url = st.text_input(
                    "Resource URL | رابط المورد",
                    placeholder="https://drive.google.com/..."
                )
                file_path = None
            else:
                file_path = st.text_input(
                    "File Path | مسار الملف",
                    placeholder="/resources/math_notes.pdf"
                )
                url = None
            
            description = st.text_area(
                "Description | وصف المورد",
                placeholder="Brief description of the resource...",
                height=80
            )
            
            if st.form_submit_button("💾 Save Resource | حفظ المورد", use_container_width=True):
                if title and subject:
                    _save_resource(
                        teacher_id, school_id,
                        title, subject.split(" |")[0],
                        grade_level.split(" |")[0],
                        url, file_path, description
                    )
                else:
                    st.error("❌ Title and Subject are required!")
    
    # ----------------------------
    # VIEW EXISTING RESOURCES
    # ----------------------------
    with col2:
        st.markdown("### 📋 My Resources | مواردي")
        
        session = get_db_session()
        try:
            resources = session.query(Resource).filter(
                Resource.teacher_id == teacher_id
            ).order_by(Resource.uploaded_at.desc()).all()
            
            if resources:
                for res in resources:
                    with st.expander(f"📄 {res.title}"):
                        st.write(f"**Subject:** {res.subject}")
                        st.write(f"**Level:** {res.grade_level or 'N/A'}")
                        
                        if res.url:
                            st.markdown(f"🔗 [Open Link]({res.url})")
                        elif res.file_path:
                            st.write(f"📁 Path: `{res.file_path}`")
                        
                        if res.description:
                            st.caption(res.description)
                        
                        st.caption(f"📅 Uploaded: {res.uploaded_at.strftime('%Y-%m-%d')}")
                        
                        # Delete button
                        if st.button(f"🗑️ Delete", key=f"del_res_{res.id}"):
                            _delete_resource(res.id)
            else:
                st.info("No resources yet. Add your first resource!")
        
        finally:
            session.close()


def _save_resource(teacher_id, school_id, title, subject, grade_level, url, file_path, description):
    """Save resource to database."""
    
    session = get_db_session()
    
    try:
        new_resource = Resource(
            title=title,
            subject=subject,
            grade_level=grade_level,
            url=url,
            file_path=file_path,
            description=description,
            teacher_id=teacher_id,
            school_id=school_id,
            uploaded_at=datetime.datetime.utcnow()
        )
        
        session.add(new_resource)
        session.commit()
        
        st.success(f"✅ Resource '{title}' saved successfully!")
    
    except Exception as e:
        session.rollback()
        st.error(f"❌ Error: {e}")
    
    finally:
        session.close()


def _delete_resource(resource_id: int):
    """
    Delete resource from database.
    SECURITY: Only delete if resource belongs to current teacher AND school.
    """
    
    # Get current user context for security check
    school_id = st.session_state.get('school_id')
    teacher_id = st.session_state.get('user_id')
    
    session = get_db_session()
    
    try:
        # SECURITY FIX: Verify ownership before deletion
        resource = session.query(Resource).filter(
            Resource.id == resource_id,
            Resource.school_id == school_id,
            Resource.teacher_id == teacher_id
        ).first()
        
        if resource:
            session.delete(resource)
            session.commit()
            st.success("✅ Resource deleted!")
            st.rerun()
        else:
            st.error("❌ Resource not found or access denied.")
    
    except Exception as e:
        session.rollback()
        st.error(f"❌ Error: {e}")
    
    finally:
        session.close()


# =============================================================================
# TAB 2: ONLINE CLASSES / ZOOM SESSIONS
# =============================================================================

def _render_online_classes_tab(teacher_id: int, school_id: int):
    """Schedule and manage online classes."""
    
    st.subheader("🎥 Online Classes | الفصول الأونلاين")
    
    col1, col2 = st.columns([1, 1])
    
    # ----------------------------
    # SCHEDULE NEW CLASS
    # ----------------------------
    with col1:
        st.markdown("### ➕ Schedule New Class | جدولة حصة جديدة")
        
        with st.form("schedule_class_form", clear_on_submit=True):
            title = st.text_input(
                "Class Topic | عنوان الحصة",
                placeholder="e.g., Algebra Review Session"
            )
            
            subject = st.selectbox(
                "Subject | المادة",
                options=[
                    "Mathematics | الرياضيات",
                    "Arabic | اللغة العربية",
                    "English | اللغة الإنجليزية",
                    "Science | العلوم",
                    "History | التاريخ",
                    "Other | أخرى"
                ]
            )
            
            # Date and Time
            col_date, col_time = st.columns(2)
            
            with col_date:
                session_date = st.date_input(
                    "Date | التاريخ",
                    value=datetime.date.today() + datetime.timedelta(days=1),
                    min_value=datetime.date.today()
                )
            
            with col_time:
                session_time = st.time_input(
                    "Time | الوقت",
                    value=datetime.time(10, 0)  # Default 10:00 AM
                )
            
            duration = st.number_input(
                "Duration (minutes) | المدة بالدقائق",
                min_value=15,
                max_value=180,
                value=60,
                step=15
            )
            
            zoom_link = st.text_input(
                "Zoom/Meet Link | رابط الاجتماع",
                placeholder="https://zoom.us/j/..."
            )
            
            description = st.text_area(
                "Description | وصف الحصة",
                placeholder="What will be covered in this session...",
                height=80
            )
            
            if st.form_submit_button("📅 Schedule Class | جدولة الحصة", use_container_width=True):
                if title and zoom_link:
                    # Combine date and time
                    scheduled_datetime = datetime.datetime.combine(session_date, session_time)
                    
                    _save_online_session(
                        teacher_id, school_id,
                        title, subject.split(" |")[0],
                        zoom_link, scheduled_datetime,
                        duration, description
                    )
                else:
                    st.error("❌ Topic and Zoom link are required!")
    
    # ----------------------------
    # VIEW SCHEDULED CLASSES
    # ----------------------------
    with col2:
        st.markdown("### 📋 My Scheduled Classes | حصصي المجدولة")
        
        session = get_db_session()
        
        try:
            # Get future sessions only
            now = datetime.datetime.utcnow()
            sessions = session.query(OnlineSession).filter(
                OnlineSession.teacher_id == teacher_id,
                OnlineSession.scheduled_time >= now
            ).order_by(OnlineSession.scheduled_time.asc()).all()
            
            if sessions:
                for sess in sessions:
                    time_until = sess.scheduled_time - now
                    hours_until = time_until.total_seconds() / 3600
                    
                    # Status indicator
                    if hours_until < 1:
                        status = "🔴 Starting Soon!"
                    elif hours_until < 24:
                        status = "🟡 Today"
                    else:
                        status = "🟢 Upcoming"
                    
                    with st.expander(f"{status} {sess.title}"):
                        st.write(f"**Subject:** {sess.subject}")
                        st.write(f"**When:** {sess.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Duration:** {sess.duration_minutes} minutes")
                        
                        st.markdown(f"🔗 **[Join Zoom]({sess.zoom_link})**")
                        
                        if sess.description:
                            st.caption(sess.description)
                        
                        # Delete button
                        if st.button(f"🗑️ Cancel Class", key=f"del_sess_{sess.id}"):
                            _delete_online_session(sess.id)
            else:
                st.info("No upcoming classes. Schedule one!")
            
            # Past sessions
            st.markdown("---")
            st.caption("📜 Past Sessions:")
            
            past_sessions = session.query(OnlineSession).filter(
                OnlineSession.teacher_id == teacher_id,
                OnlineSession.scheduled_time < now
            ).order_by(OnlineSession.scheduled_time.desc()).limit(5).all()
            
            for past in past_sessions:
                st.caption(f"✅ {past.title} - {past.scheduled_time.strftime('%Y-%m-%d')}")
        
        finally:
            session.close()


def _save_online_session(teacher_id, school_id, title, subject, zoom_link, scheduled_time, duration, description):
    """Save online session to database."""
    
    session = get_db_session()
    
    try:
        new_session = OnlineSession(
            title=title,
            subject=subject,
            zoom_link=zoom_link,
            scheduled_time=scheduled_time,
            duration_minutes=duration,
            description=description,
            teacher_id=teacher_id,
            school_id=school_id,
            is_active=True,
            created_at=datetime.datetime.utcnow()
        )
        
        session.add(new_session)
        session.commit()
        
        st.success(f"✅ Class '{title}' scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M')}!")
    
    except Exception as e:
        session.rollback()
        st.error(f"❌ Error: {e}")
    
    finally:
        session.close()


def _delete_online_session(session_id: int):
    """
    Delete online session from database.
    SECURITY: Only delete if session belongs to current teacher AND school.
    """
    
    # Get current user context for security check
    school_id = st.session_state.get('school_id')
    teacher_id = st.session_state.get('user_id')
    
    db_session = get_db_session()
    
    try:
        # SECURITY FIX: Verify ownership before deletion
        online_session = db_session.query(OnlineSession).filter(
            OnlineSession.id == session_id,
            OnlineSession.school_id == school_id,
            OnlineSession.teacher_id == teacher_id
        ).first()
        
        if online_session:
            db_session.delete(online_session)
            db_session.commit()
            st.success("✅ Class cancelled!")
            st.rerun()
        else:
            st.error("❌ Session not found or access denied.")
    
    except Exception as e:
        db_session.rollback()
        st.error(f"❌ Error: {e}")
    
    finally:
        db_session.close()
