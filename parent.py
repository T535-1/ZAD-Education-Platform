# -*- coding: utf-8 -*-
"""
Parent Dashboard Module - Simplified Version
Provides read-only view of children's information
Compatible with ZAD Education Platform | منصة زاد التعليمية
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from core.database import get_db_session
from core.i18n import get_text
from models import User


def show_parent_dashboard():
    """
    Main parent dashboard showing basic information.

    This is a simplified version that works with the current database schema.
    For full parent functionality with ParentChild relationships,
    additional database models need to be configured.
    """
    st.title("👨‍👩‍👧 " + get_text("parent_dashboard", "Parent Portal"))

    # Get current user info from session
    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username")
    school_id = st.session_state.get("school_id")

    if not user_id or not school_id:
        st.error("يرجى تسجيل الدخول - Please log in")
        return

    session = get_db_session()

    try:
        # Welcome message
        st.markdown(f"### مرحباً {username} - Welcome {username}")
        st.info(
            "🔹 هذه اللوحة توفر لك إمكانية متابعة أداء أطفالك الأكاديمي.\n\n"
            "🔹 This dashboard allows you to monitor your children's academic performance."
        )

        st.markdown("---")

        # Quick stats
        st.subheader("📊 نظرة عامة - Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Count students in the same school (this is a placeholder)
            students_count = session.query(User).filter(
                User.school_id == school_id,
                User.role == 'student'
            ).count()
            st.metric("طلاب المدرسة - School Students", students_count)

        with col2:
            teachers_count = session.query(User).filter(
                User.school_id == school_id,
                User.role == 'teacher'
            ).count()
            st.metric("المعلمون - Teachers", teachers_count)

        with col3:
            st.metric("الحضور العام - Overall Attendance", "95%")

        with col4:
            st.metric("المتوسط العام - Overall Average", "85%")

        st.markdown("---")

        # Information sections
        tab1, tab2, tab3 = st.tabs([
            "📚 المقررات - Courses",
            "📝 الدرجات - Grades",
            "📅 الحضور - Attendance"
        ])

        with tab1:
            show_courses_info()

        with tab2:
            show_grades_info()

        with tab3:
            show_attendance_info()

        # Important notices
        st.markdown("---")
        st.subheader("📢 إشعارات مهمة - Important Notices")

        col1, col2 = st.columns(2)

        with col1:
            st.info("✅ **تم تسليم الواجب المنزلي** - Homework submitted")
            st.success("🎉 **درجة ممتازة في الرياضيات** - Excellent grade in Math")

        with col2:
            st.warning("⏰ **موعد تسليم قادم** - Upcoming deadline")
            st.info("📅 **اجتماع أولياء أمور يوم الخميس** - Parent meeting on Thursday")

        # Contact section
        st.markdown("---")
        st.subheader("📞 التواصل - Contact")

        st.write(
            "لأي استفسارات أو طلبات، يرجى التواصل مع إدارة المدرسة.\n\n"
            "For any inquiries or requests, please contact the school administration."
        )

        if st.button("📧 إرسال رسالة للإدارة - Send Message to Admin"):
            st.info("سيتم فتح نموذج التواصل قريباً - Contact form coming soon")

    except Exception as e:
        st.error(f"خطأ - Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

    finally:
        session.close()


def show_courses_info():
    """Display courses information"""
    st.markdown("### 📚 المقررات الدراسية - Academic Courses")

    # Sample data - replace with actual database queries
    courses_data = {
        "المقرر - Course": ["الرياضيات - Math", "العلوم - Science", "اللغة العربية - Arabic", "اللغة الإنجليزية - English"],
        "المعلم - Teacher": ["أ. محمد", "أ. فاطمة", "أ. أحمد", "Ms. Sarah"],
        "التقدم - Progress": ["85%", "90%", "78%", "92%"],
        "الحالة - Status": ["✅ نشط", "✅ نشط", "✅ نشط", "✅ نشط"]
    }

    df = pd.DataFrame(courses_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.info("💡 لعرض تفاصيل أكثر عن كل مقرر، يرجى التواصل مع المعلم المختص.")


def show_grades_info():
    """Display grades information"""
    st.markdown("### 📝 الدرجات والتقييمات - Grades & Assessments")

    # Sample data
    grades_data = {
        "الواجب - Assignment": [
            "اختبار الفصل الأول - Chapter 1 Test",
            "مشروع البحث - Research Project",
            "الواجب المنزلي - Homework",
            "اختبار منتصف الفصل - Midterm Exam"
        ],
        "المادة - Subject": ["الرياضيات", "العلوم", "اللغة العربية", "اللغة الإنجليزية"],
        "الدرجة - Grade": ["45/50", "38/40", "28/30", "88/100"],
        "النسبة - Percentage": ["90%", "95%", "93%", "88%"],
        "التاريخ - Date": ["2025-11-25", "2025-11-22", "2025-11-20", "2025-11-18"]
    }

    df = pd.DataFrame(grades_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي الواجبات - Total Assignments", "4")
    with col2:
        st.metric("المتوسط - Average", "91.5%")
    with col3:
        st.metric("أعلى درجة - Highest", "95%")

    if st.button("📥 تصدير التقرير - Export Report"):
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="⬇️ تحميل ملف CSV - Download CSV",
            data=csv,
            file_name=f"grades_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def show_attendance_info():
    """Display attendance information"""
    st.markdown("### 📅 سجل الحضور - Attendance Record")

    # Sample data
    attendance_data = {
        "التاريخ - Date": ["2025-11-30", "2025-11-29", "2025-11-28", "2025-11-27", "2025-11-26"],
        "الحالة - Status": ["✅ حاضر", "✅ حاضر", "⏰ متأخر", "✅ حاضر", "✅ حاضر"],
        "الحصة - Period": ["1-4", "1-4", "1-4", "1-4", "1-4"],
        "ملاحظات - Notes": ["-", "-", "تأخر 10 دقائق", "-", "-"]
    }

    df = pd.DataFrame(attendance_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Attendance statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("نسبة الحضور - Attendance Rate", "95%")
    with col2:
        st.metric("✅ حاضر - Present", "19")
    with col3:
        st.metric("❌ غائب - Absent", "0")
    with col4:
        st.metric("⏰ متأخر - Late", "1")

    # Attendance chart (placeholder)
    st.progress(0.95)
    st.caption("معدل الحضور الشهري: 95% - Monthly attendance rate: 95%")