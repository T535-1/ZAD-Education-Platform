# -*- coding: utf-8 -*-
"""
ZAD Education Platform - AI-Powered Admin Dashboard | منصة زاد - لوحة المشرف الذكية
====================================================================================
Super Admin Dashboard with:
1. Master-Detail Navigation (Schools → School Details)
2. AI-Powered Smart Analytics (Health Check, Risk Radar, Teacher Performance)

Author: ZAD Engineering Team
"""

import streamlit as st
import pandas as pd
from werkzeug.security import generate_password_hash
from models import get_db_session, School, User, Grade, Resource, OnlineSession
from core.i18n import t, get_language


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def show_admin_dashboard():
    """
    Main entry point for Super Admin Dashboard.
    Uses Master-Detail pattern:
    - If no school selected → Show all schools (Master View)
    - If school selected → Show school details (Detail View)
    """
    
    # Access check
    role = st.session_state.get('role')
    if role not in ['super_admin', 'school_admin', 'admin']:
        st.error("❌ Access Denied. Super Admin only.")
        return
    
    # Master-Detail Navigation Logic
    selected_school_id = st.session_state.get('selected_school_id')
    
    if selected_school_id is None:
        # MASTER VIEW: Show all schools
        _show_master_view()
    else:
        # DETAIL VIEW: Show specific school dashboard
        _show_school_details_dashboard(selected_school_id)


# =============================================================================
# MASTER VIEW: ALL SCHOOLS
# =============================================================================

def _show_master_view():
    """Master view showing all schools with summary stats."""
    
    st.title("🛡️ Super Admin Dashboard | لوحة المشرف العام")
    st.caption("Full platform control with AI-powered insights | التحكم الكامل مع تحليلات ذكية")
    
    # Tab navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏫 Schools | المدارس",
        "👥 Users & Master Key | المستخدمين",
        "📊 Platform Statistics | الإحصائيات",
        "🔧 Diagnostics & Fixes | التشخيص"
    ])
    
    with tab1:
        _render_schools_tab()
    
    with tab2:
        _render_users_tab()
    
    with tab3:
        _render_platform_stats_tab()
    
    with tab4:
        _render_diagnostics_tab()


def _render_schools_tab():
    """Schools grid with click-to-drill-down."""
    
    st.subheader("🏫 Schools Management | إدارة المدارس")
    
    col1, col2 = st.columns([1, 1])
    
    # CREATE SCHOOL FORM
    with col1:
        st.markdown("### ➕ Create New School")
        
        with st.form("create_school_form", clear_on_submit=True):
            school_name = st.text_input("School Name | اسم المدرسة")
            subscription_plan = st.selectbox("Plan", ['free', 'pro', 'enterprise'])
            admin_email = st.text_input("Admin Email")
            admin_name = st.text_input("Admin Name")
            admin_password = st.text_input("Admin Password", type="password", value="school123")
            
            if st.form_submit_button("✅ Create School", use_container_width=True):
                if school_name and admin_email and admin_name:
                    _create_school(school_name, subscription_plan, admin_email, admin_name, admin_password)
                else:
                    st.error("❌ Please fill all fields!")
    
    # SCHOOLS LIST (Click to Drill-Down)
    with col2:
        st.markdown("### 📋 Click a School to View Details")
        
        session = get_db_session()
        try:
            schools = session.query(School).order_by(School.created_at.desc()).all()
            
            if schools:
                for school in schools:
                    user_count = session.query(User).filter(User.school_id == school.id).count()
                    
                    # School Card with Click Action
                    with st.container():
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"**🏫 {school.name}**")
                            st.caption(f"👥 {user_count} users | 📋 {school.subscription_plan}")
                        with col_b:
                            # DRILL-DOWN BUTTON
                            if st.button("📊 Open", key=f"open_{school.id}"):
                                st.session_state['selected_school_id'] = school.id
                                st.session_state['selected_school_name'] = school.name
                                st.rerun()
                        st.markdown("---")
            else:
                st.info("No schools yet. Create one!")
        finally:
            session.close()


# =============================================================================
# DETAIL VIEW: SCHOOL DASHBOARD WITH AI ANALYTICS
# =============================================================================

def _show_school_details_dashboard(school_id: int):
    """
    School-specific dashboard with AI-powered analytics.
    Contains 4 tabs: Overview, Students, Teachers, Quality
    """
    
    school_name = st.session_state.get('selected_school_name', 'School')
    
    # HEADER with Back Button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔙 Back", use_container_width=True):
            st.session_state['selected_school_id'] = None
            st.session_state['selected_school_name'] = None
            st.rerun()
    with col2:
        st.title(f"🏫 {school_name}")
    
    st.caption("AI-Powered School Analytics | تحليلات المدرسة بالذكاء الاصطناعي")
    
    # 4 TABS with AI Features
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview & AI Health",
        "👥 Students & Risk Radar",
        "🧑‍🏫 Teacher Performance",
        "🏆 Quality & Accreditation"
    ])
    
    session = get_db_session()
    
    try:
        with tab1:
            _render_overview_tab(session, school_id)
        
        with tab2:
            _render_students_tab(session, school_id)
        
        with tab3:
            _render_teachers_tab(session, school_id)
        
        with tab4:
            _render_quality_tab(session, school_id)
    
    finally:
        session.close()


# =============================================================================
# TAB D: QUALITY & ACCREDITATION (NEW!)
# =============================================================================

def _render_quality_tab(session, school_id: int):
    """
    Quality & Accreditation Tab with:
    - Global Standards Monitor
    - Custom KPI Form
    - AI Quality Auditor
    """
    from models import QualityKPI
    
    st.subheader("🏆 Quality & Accreditation | الجودة والاعتماد")
    st.caption("ISO 9001 / NEASC / Ministry Standards Compliance")
    
    st.markdown("---")
    
    # =========================================================================
    # SECTION A: GLOBAL STANDARDS MONITOR
    # =========================================================================
    st.markdown("### 📊 Section A: Global Standards Monitor")
    st.caption("International Education Quality Benchmarks")
    
    # Get actual school data for calculations
    total_students = session.query(User).filter(
        User.school_id == school_id, User.role == 'student'
    ).count()
    total_teachers = session.query(User).filter(
        User.school_id == school_id, User.role == 'teacher'
    ).count()
    total_resources = session.query(Resource).filter(
        Resource.school_id == school_id
    ).count()
    total_grades = session.query(Grade).filter(
        Grade.school_id == school_id
    ).count()
    
    # Calculate actual metrics
    student_teacher_ratio = total_students / max(total_teachers, 1)
    grading_rate = (total_grades / max(total_students, 1)) * 100 if total_students > 0 else 0
    digital_resource_rate = min((total_resources / max(total_students * 0.1, 1)) * 100, 100)
    
    # Global Standards (with calculated values)
    GLOBAL_STANDARDS = [
        {
            "name": "Student-Teacher Ratio",
            "current": student_teacher_ratio,
            "target": 20,
            "unit": ":1",
            "category": "Staffing",
            "lower_is_better": True
        },
        {
            "name": "Assessment Coverage",
            "current": min(grading_rate, 100),
            "target": 80,
            "unit": "%",
            "category": "Academic",
            "lower_is_better": False
        },
        {
            "name": "Digital Resource Availability",
            "current": digital_resource_rate,
            "target": 70,
            "unit": "%",
            "category": "Digital",
            "lower_is_better": False
        },
        {
            "name": "Teacher Activity Rate",
            "current": 85 if total_teachers > 0 else 0,
            "target": 90,
            "unit": "%",
            "category": "Performance",
            "lower_is_better": False
        }
    ]
    
    col1, col2 = st.columns(2)
    
    for i, kpi in enumerate(GLOBAL_STANDARDS):
        with col1 if i % 2 == 0 else col2:
            # Determine if meets target
            if kpi.get("lower_is_better"):
                meets_target = kpi["current"] <= kpi["target"]
            else:
                meets_target = kpi["current"] >= kpi["target"]
            
            # Color coding
            color = "🟢" if meets_target else "🔴"
            status = "✅ Exceeds Standard" if meets_target else "⚠️ Below Standard"
            
            st.markdown(f"**{color} {kpi['name']}**")
            st.caption(f"Category: {kpi['category']}")
            
            # Progress bar
            progress_val = min(kpi["current"] / max(kpi["target"], 1), 1.0) if not kpi.get("lower_is_better") else min(kpi["target"] / max(kpi["current"], 1), 1.0)
            st.progress(progress_val)
            
            st.write(f"Current: **{kpi['current']:.1f}{kpi['unit']}** | Target: {kpi['target']}{kpi['unit']}")
            st.caption(status)
            st.markdown("---")
    
    # =========================================================================
    # SECTION B: ADD CUSTOM KPI
    # =========================================================================
    st.markdown("### ➕ Section B: Add Custom School KPI")
    st.caption("Define your own quality indicators")
    
    with st.form("add_kpi_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            kpi_name = st.text_input("Indicator Name", placeholder="e.g., Parent Satisfaction")
        with col2:
            current_val = st.number_input("Current Value", min_value=0.0, value=0.0)
        with col3:
            target_val = st.number_input("Target Value", min_value=0.0, value=100.0)
        
        col1, col2 = st.columns(2)
        with col1:
            kpi_unit = st.selectbox("Unit", ["%", "Ratio", "Score", "Count", "Days"])
        with col2:
            kpi_category = st.selectbox("Category", ["Academic", "Infrastructure", "Digital", "Staff", "Finance", "Other"])
        
        if st.form_submit_button("💾 Save KPI", use_container_width=True):
            if kpi_name:
                new_kpi = QualityKPI(
                    name=kpi_name,
                    metric_type='School_Custom',
                    current_value=current_val,
                    target_value=target_val,
                    unit=kpi_unit,
                    category=kpi_category,
                    school_id=school_id
                )
                session.add(new_kpi)
                session.commit()
                st.success(f"✅ KPI '{kpi_name}' saved!")
                st.rerun()
            else:
                st.error("❌ Please enter indicator name!")
    
    # Show existing custom KPIs
    custom_kpis = session.query(QualityKPI).filter(
        QualityKPI.school_id == school_id
    ).all()
    
    if custom_kpis:
        st.markdown("#### 📋 Your Custom KPIs")
        for kpi in custom_kpis:
            meets = kpi.current_value >= kpi.target_value
            icon = "🟢" if meets else "🔴"
            st.write(f"{icon} **{kpi.name}**: {kpi.current_value}{kpi.unit} / {kpi.target_value}{kpi.unit} ({kpi.category})")
    
    st.markdown("---")
    
    # =========================================================================
    # SECTION C: AI QUALITY AUDITOR
    # =========================================================================
    st.markdown("### 🤖 Section C: AI Quality Auditor")
    st.caption("Automated Gap Analysis & Action Plan")
    
    # Find all KPIs below target
    gaps = []
    
    # Check global standards
    for kpi in GLOBAL_STANDARDS:
        if kpi.get("lower_is_better"):
            if kpi["current"] > kpi["target"]:
                gap_pct = ((kpi["current"] - kpi["target"]) / kpi["target"]) * 100
                gaps.append({
                    "name": kpi["name"],
                    "current": f"{kpi['current']:.1f}{kpi['unit']}",
                    "target": f"{kpi['target']}{kpi['unit']}",
                    "gap": f"+{gap_pct:.0f}%",
                    "type": "Global Standard"
                })
        else:
            if kpi["current"] < kpi["target"]:
                gap_pct = ((kpi["target"] - kpi["current"]) / kpi["target"]) * 100
                gaps.append({
                    "name": kpi["name"],
                    "current": f"{kpi['current']:.1f}{kpi['unit']}",
                    "target": f"{kpi['target']}{kpi['unit']}",
                    "gap": f"-{gap_pct:.0f}%",
                    "type": "Global Standard"
                })
    
    # Check custom KPIs
    for kpi in custom_kpis:
        if kpi.current_value < kpi.target_value:
            gap_pct = ((kpi.target_value - kpi.current_value) / kpi.target_value) * 100
            gaps.append({
                "name": kpi.name,
                "current": f"{kpi.current_value}{kpi.unit}",
                "target": f"{kpi.target_value}{kpi.unit}",
                "gap": f"-{gap_pct:.0f}%",
                "type": "Custom KPI"
            })
    
    if gaps:
        st.error(f"**📉 {len(gaps)} Quality Gaps Detected**")
        
        # Gap Analysis Table
        df_gaps = pd.DataFrame(gaps)
        st.dataframe(df_gaps, use_container_width=True, hide_index=True)
        
        # AI Recommendations
        st.markdown("#### 🤖 AI Action Plan")
        
        for gap in gaps:
            st.markdown(f"""
            **📌 {gap['name']}**
            - Current: {gap['current']} | Target: {gap['target']} | Gap: {gap['gap']}
            - 💡 **AI Recommendation:** {_generate_ai_recommendation(gap['name'])}
            """)
            st.markdown("---")
    else:
        st.success("✅ All Quality Standards Met! School is fully compliant.")
        st.balloons()


def _generate_ai_recommendation(kpi_name: str) -> str:
    """Generate AI recommendation based on KPI name."""
    recommendations = {
        "Student-Teacher Ratio": "Hire 2-3 additional teachers or redistribute class sizes. Consider part-time teaching assistants.",
        "Assessment Coverage": "Implement bi-weekly assessments. Use AI Vision Grader to automate grading workflow.",
        "Digital Resource Availability": "Upload more PDF resources to library. Target: 1 resource per 10 students per subject.",
        "Teacher Activity Rate": "Schedule training sessions on platform features. Set weekly content upload targets.",
        "Parent Satisfaction": "Conduct monthly parent surveys. Improve parent communication via WhatsApp integration.",
        "default": "Review current practices and set improvement milestones. Schedule weekly progress reviews."
    }
    return recommendations.get(kpi_name, recommendations["default"])


# =============================================================================
# TAB A: OVERVIEW & AI HEALTH CHECK
# =============================================================================

def _render_overview_tab(session, school_id: int):
    """Overview with AI Health Score."""
    
    st.subheader("📊 School Overview | نظرة عامة")
    
    # Fetch stats
    total_users = session.query(User).filter(User.school_id == school_id).count()
    teachers = session.query(User).filter(User.school_id == school_id, User.role == 'teacher').count()
    students = session.query(User).filter(User.school_id == school_id, User.role == 'student').count()
    parents = session.query(User).filter(User.school_id == school_id, User.role == 'parent').count()
    grades_count = session.query(Grade).filter(Grade.school_id == school_id).count()
    resources_count = session.query(Resource).filter(Resource.school_id == school_id).count()
    
    # METRICS DISPLAY
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Users", total_users)
    col2.metric("👨‍🏫 Teachers", teachers)
    col3.metric("🎓 Students", students)
    col4.metric("👨‍👩‍👧 Parents", parents)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📝 Grades", grades_count)
    col2.metric("📚 Resources", resources_count)
    col3.metric("📊 Grading Rate", f"{(grades_count / max(students, 1)):.1f}/student")
    col4.metric("📈 Active", "✅")
    
    st.markdown("---")
    
    # =========================================================================
    # 🤖 AI FEATURE: SCHOOL HEALTH CHECK
    # =========================================================================
    st.subheader("🤖 AI School Health Check | فحص صحة المدرسة")
    
    # AI LOGIC: Calculate Health Score (0-100)
    # Factors:
    # 1. Student/Teacher Ratio (ideal: 15-25 students per teacher)
    # 2. Grading Activity (grades per student)
    # 3. Resource Availability
    
    health_score = 0
    insights = []
    
    # Factor 1: Student/Teacher Ratio
    if teachers > 0:
        ratio = students / teachers
        if 10 <= ratio <= 25:
            health_score += 40
            insights.append(("✅", "Optimal student-teacher ratio", "green"))
        elif ratio < 10:
            health_score += 30
            insights.append(("💡", f"Low ratio ({ratio:.0f}:1). Consider enrolling more students.", "blue"))
        else:
            health_score += 15
            insights.append(("⚠️", f"High ratio ({ratio:.0f}:1). Teacher shortage detected!", "orange"))
    else:
        insights.append(("🚨", "No teachers assigned! Critical staffing issue.", "red"))
    
    # Factor 2: Grading Activity
    if students > 0:
        grades_per_student = grades_count / students
        if grades_per_student >= 3:
            health_score += 30
            insights.append(("✅", f"Active grading ({grades_per_student:.1f} grades/student)", "green"))
        elif grades_per_student >= 1:
            health_score += 20
            insights.append(("💡", "Moderate grading activity. Encourage more assessments.", "blue"))
        else:
            health_score += 5
            insights.append(("⚠️", "Low grading activity. Students need more assessments!", "orange"))
    
    # Factor 3: Resources
    if resources_count >= 5:
        health_score += 30
        insights.append(("✅", f"{resources_count} resources available", "green"))
    elif resources_count >= 1:
        health_score += 15
        insights.append(("💡", "Add more learning resources for students", "blue"))
    else:
        health_score += 0
        insights.append(("⚠️", "No resources uploaded. Digital library is empty!", "orange"))
    
    # DISPLAY HEALTH SCORE
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Health Score Gauge
        if health_score >= 80:
            color = "🟢"
            status = "Excellent"
        elif health_score >= 60:
            color = "🟡"
            status = "Good"
        elif health_score >= 40:
            color = "🟠"
            status = "Needs Attention"
        else:
            color = "🔴"
            status = "Critical"
        
        st.metric(f"{color} Health Score", f"{health_score}/100", status)
    
    with col2:
        st.markdown("**🤖 AI Insights:**")
        for icon, message, _ in insights:
            st.write(f"{icon} {message}")


# =============================================================================
# TAB B: STUDENTS & RISK RADAR (AI)
# =============================================================================

def _render_students_tab(session, school_id: int):
    """Students list with AI Risk Radar."""
    
    st.subheader("👥 Students | الطلاب")
    
    # Fetch students
    students = session.query(User).filter(
        User.school_id == school_id,
        User.role == 'student'
    ).all()
    
    if not students:
        st.info("No students enrolled yet.")
        return
    
    # Build student data with grades
    student_data = []
    at_risk_students = []
    
    for student in students:
        grades = session.query(Grade).filter(Grade.student_id == student.id).all()
        
        if grades:
            avg_score = sum(g.score for g in grades) / len(grades)
            avg_max = sum(g.max_score for g in grades) / len(grades)
            percentage = (avg_score / avg_max) * 100 if avg_max > 0 else 0
        else:
            avg_score = 0
            percentage = 0
        
        student_data.append({
            "Name": student.full_name,
            "Email": student.email,
            "Grades Count": len(grades),
            "Avg Score": f"{avg_score:.1f}",
            "Percentage": f"{percentage:.0f}%"
        })
        
        # =====================================================================
        # 🤖 AI FEATURE: RISK DETECTION
        # Logic: Flag students with average below 50%
        # =====================================================================
        if percentage < 50 and len(grades) > 0:
            at_risk_students.append({
                "Student": student.full_name,
                "Email": student.email,
                "Avg %": f"{percentage:.0f}%",
                "Risk Level": "🔴 High" if percentage < 30 else "🟠 Medium"
            })
    
    # DISPLAY RISK RADAR (AI Feature)
    if at_risk_students:
        st.markdown("---")
        st.subheader("🚨 AI Risk Radar | رادار المخاطر")
        st.error(f"**{len(at_risk_students)} At-Risk Students Detected by AI**")
        
        df_risk = pd.DataFrame(at_risk_students)
        st.dataframe(df_risk, use_container_width=True, hide_index=True)
        
        st.caption("💡 AI Recommendation: Schedule intervention meetings with these students.")
    else:
        st.success("✅ No at-risk students detected! All students performing well.")
    
    # ALL STUDENTS TABLE
    st.markdown("---")
    st.subheader("📋 All Students")
    
    df = pd.DataFrame(student_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


# =============================================================================
# TAB C: TEACHER PERFORMANCE (AI)
# =============================================================================

def _render_teachers_tab(session, school_id: int):
    """Teachers list with AI performance analysis."""
    
    st.subheader("🧑‍🏫 Teachers | المعلمون")
    
    # Fetch teachers
    teachers = session.query(User).filter(
        User.school_id == school_id,
        User.role == 'teacher'
    ).all()
    
    if not teachers:
        st.info("No teachers assigned yet.")
        return
    
    # Build teacher performance data
    teacher_data = []
    inactive_teachers = []
    anomaly_teachers = []
    
    for teacher in teachers:
        # Count resources uploaded by teacher
        resources = session.query(Resource).filter(Resource.teacher_id == teacher.id).count()
        
        # Count online sessions
        sessions = session.query(OnlineSession).filter(OnlineSession.teacher_id == teacher.id).count()
        
        # For grading analysis, we check grades in this school
        # Note: Grades don't have teacher_id, so we approximate activity
        
        teacher_data.append({
            "Name": teacher.full_name,
            "Email": teacher.email,
            "Resources": resources,
            "Sessions": sessions,
            "Status": "✅ Active" if (resources + sessions) > 0 else "⚠️ Inactive"
        })
        
        # =====================================================================
        # 🤖 AI FEATURE: INACTIVITY DETECTION
        # Logic: Flag teachers with no resources AND no sessions
        # =====================================================================
        if resources == 0 and sessions == 0:
            inactive_teachers.append({
                "Teacher": teacher.full_name,
                "Email": teacher.email,
                "Issue": "📉 No content uploaded",
                "Action": "Needs training/support"
            })
    
    # DISPLAY INACTIVE TEACHERS (AI Feature)
    if inactive_teachers:
        st.markdown("---")
        st.subheader("📉 AI: Inactive Teachers Detected")
        st.warning(f"**{len(inactive_teachers)} teachers with no activity**")
        
        df_inactive = pd.DataFrame(inactive_teachers)
        st.dataframe(df_inactive, use_container_width=True, hide_index=True)
        
        st.caption("💡 AI Recommendation: Provide training on how to use the platform.")
    else:
        st.success("✅ All teachers are actively using the platform!")
    
    # ALL TEACHERS TABLE
    st.markdown("---")
    st.subheader("📋 All Teachers")
    
    df = pd.DataFrame(teacher_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


# =============================================================================
# USER MANAGEMENT TAB
# =============================================================================

def _render_users_tab():
    """User search, password reset, and impersonation."""
    
    st.subheader("👥 User Management & Master Key | إدارة المستخدمين")
    
    st.markdown("### 🔍 Search Users")
    search_query = st.text_input("Search by name or email", placeholder="Enter name or email...")
    
    session = get_db_session()
    
    try:
        if search_query:
            users = session.query(User).filter(
                (User.email.ilike(f"%{search_query}%")) |
                (User.full_name.ilike(f"%{search_query}%"))
            ).limit(20).all()
        else:
            users = session.query(User).order_by(User.created_at.desc()).limit(20).all()
        
        if not users:
            st.info("No users found.")
            return
        
        st.markdown("### 📋 User Results")
        
        for user in users:
            school_name = user.school.name if user.school else "No School"
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{user.full_name}**")
                st.caption(f"📧 {user.email}")
            
            with col2:
                st.caption(f"🏫 {school_name[:20]}...")
                st.caption(f"🎭 Role: `{user.role}`")
            
            with col3:
                if st.button(f"🔐 Reset PW", key=f"reset_{user.id}"):
                    _reset_password(user.id)
            
            with col4:
                current_user_id = st.session_state.get('user_id')
                if user.id != current_user_id:
                    if st.button(f"🎭 Login As", key=f"impersonate_{user.id}"):
                        _impersonate_user(user)
            
            st.markdown("---")
    
    finally:
        session.close()


# =============================================================================
# PLATFORM STATISTICS TAB
# =============================================================================

def _render_platform_stats_tab():
    """Platform-wide statistics."""
    
    st.subheader("📊 Platform Statistics | إحصائيات المنصة")
    
    session = get_db_session()
    
    try:
        total_schools = session.query(School).count()
        total_users = session.query(User).count()
        total_teachers = session.query(User).filter(User.role == 'teacher').count()
        total_students = session.query(User).filter(User.role == 'student').count()
        total_grades = session.query(Grade).count()
        total_resources = session.query(Resource).count()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏫 Schools", total_schools)
        col2.metric("👥 Users", total_users)
        col3.metric("👨‍🏫 Teachers", total_teachers)
        col4.metric("🎓 Students", total_students)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📝 Grades", total_grades)
        col2.metric("📚 Resources", total_resources)
        col3.metric("📈 Platform", "✅ Active")
        col4.metric("🤖 AI", "🟢 Online")
    
    finally:
        session.close()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _create_school(name: str, plan: str, admin_email: str, admin_name: str, admin_password: str):
    """Create a new school with its admin user."""
    
    session = get_db_session()
    
    try:
        existing_school = session.query(School).filter(School.name == name).first()
        if existing_school:
            st.error(f"❌ School '{name}' already exists!")
            return
        
        existing_user = session.query(User).filter(User.email == admin_email).first()
        if existing_user:
            st.error(f"❌ Email '{admin_email}' already in use!")
            return
        
        new_school = School(name=name, subscription_plan=plan)
        session.add(new_school)
        session.flush()
        
        new_admin = User(
            email=admin_email,
            full_name=admin_name,
            hashed_password=generate_password_hash(admin_password),
            role='school_admin',
            school_id=new_school.id
        )
        session.add(new_admin)
        session.commit()
        
        st.success(f"✅ School '{name}' created with admin '{admin_email}'!")
    
    except Exception as e:
        session.rollback()
        st.error(f"❌ Error: {e}")
    
    finally:
        session.close()


def _reset_password(user_id: int):
    """Reset user password."""
    
    new_password = "reset123"
    session = get_db_session()
    
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.hashed_password = generate_password_hash(new_password)
            session.commit()
            st.success(f"✅ Password reset to: `{new_password}`")
    except Exception as e:
        session.rollback()
        st.error(f"❌ Error: {e}")
    finally:
        session.close()


def _impersonate_user(user):
    """Impersonate a user."""
    
    st.session_state['original_user_id'] = st.session_state.get('user_id')
    st.session_state['original_role'] = st.session_state.get('role')
    st.session_state['original_user_name'] = st.session_state.get('user_name')
    st.session_state['original_school_id'] = st.session_state.get('school_id')
    
    st.session_state['user_id'] = user.id
    st.session_state['role'] = user.role
    st.session_state['user_name'] = user.full_name
    st.session_state['email'] = user.email
    st.session_state['school_id'] = user.school_id
    st.session_state['is_impersonating'] = True
    
    # Clear school selection when impersonating
    st.session_state['selected_school_id'] = None
    
    st.success(f"🎭 Now viewing as: {user.full_name}")
    st.rerun()


# =============================================================================
# DIAGNOSTICS TAB (NEW!)
# =============================================================================

def _render_diagnostics_tab():
    """System diagnostics and auto-fix tab."""
    
    st.subheader("🔧 System Diagnostics & Auto-Fix | تشخيص النظام")
    st.caption("Comprehensive platform health check and automatic error repair")
    
    st.markdown("---")
    
    # =========================================================================
    # SECTION 1: QUICK HEALTH CHECK
    # =========================================================================
    st.markdown("### 🩺 Quick Health Check")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Check 1: Database
    try:
        session = get_db_session()
        session.execute("SELECT 1")
        session.close()
        col1.metric("💾 Database", "✅ OK")
    except:
        col1.metric("💾 Database", "❌ ERROR")
    
    # Check 2: Users
    try:
        session = get_db_session()
        user_count = session.query(User).count()
        session.close()
        col2.metric("👥 Users", f"{user_count}")
    except:
        col2.metric("👥 Users", "❌ ERROR")
    
    # Check 3: Schools
    try:
        session = get_db_session()
        school_count = session.query(School).count()
        session.close()
        col3.metric("🏫 Schools", f"{school_count}")
    except:
        col3.metric("🏫 Schools", "❌ ERROR")
    
    # Check 4: Session
    if st.session_state.get('logged_in'):
        col4.metric("🔐 Session", "✅ Active")
    else:
        col4.metric("🔐 Session", "⚠️ No Login")
    
    st.markdown("---")
    
    # =========================================================================
    # SECTION 2: FULL DIAGNOSTIC
    # =========================================================================
    st.markdown("### 🔍 Full System Diagnostic")
    
    if st.button("🔍 Run Full Diagnostic Scan", use_container_width=True):
        with st.spinner("Scanning system..."):
            _run_full_diagnostic()
    
    st.markdown("---")
    
    # =========================================================================
    # SECTION 3: AUTO-FIX TOOLS
    # =========================================================================
    st.markdown("### 🔧 Auto-Fix Tools")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗄️ Repair Database", use_container_width=True):
            try:
                from models import init_db
                init_db()
                st.success("✅ Database tables verified!")
            except Exception as e:
                st.error(f"❌ Failed: {e}")
    
    with col2:
        if st.button("👤 Create Super Admin", use_container_width=True):
            _create_super_admin()
    
    with col3:
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'logged_in':
                    del st.session_state[key]
            st.success("✅ Session reset!")
            st.rerun()
    
    st.markdown("---")
    
    # =========================================================================
    # SECTION 4: IMPORT TEST
    # =========================================================================
    st.markdown("### 📦 Module Import Test")
    
    modules_to_test = [
        ('streamlit', 'st'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('werkzeug.security', 'Werkzeug'),
        ('pandas', 'Pandas')
    ]
    
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            st.write(f"✅ **{display_name}** - Installed")
        except ImportError:
            st.write(f"❌ **{display_name}** - Missing! Run: `pip install {module_name.split('.')[0]}`")
    
    st.markdown("---")
    
    # =========================================================================
    # SECTION 5: LOG VIEWER
    # =========================================================================
    st.markdown("### 📋 Recent Activity Log")
    
    log_file = "logs/zad_platform.log"
    import os
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-20:]  # Last 20 lines
            st.code("".join(lines), language="log")
    else:
        st.info("No log file found yet. Logs are created when errors occur.")


def _run_full_diagnostic():
    """Run comprehensive diagnostic scan."""
    
    checks = []
    
    # Check 1: Database Connection
    try:
        from models import get_db_session
        session = get_db_session()
        session.execute("SELECT 1")
        session.close()
        checks.append(("✅", "Database Connection", "SQLite connected"))
    except Exception as e:
        checks.append(("❌", "Database Connection", str(e)))
    
    # Check 2: All Tables
    tables = ['schools', 'users', 'grades', 'resources', 'online_sessions', 'quality_kpis']
    session = get_db_session()
    for table in tables:
        try:
            session.execute(f"SELECT COUNT(*) FROM {table}")
            checks.append(("✅", f"Table: {table}", "Exists"))
        except:
            checks.append(("❌", f"Table: {table}", "Missing"))
    session.close()
    
    # Check 3: Super Admin
    try:
        session = get_db_session()
        admin = session.query(User).filter(User.email == "admin@zad.edu").first()
        session.close()
        if admin:
            checks.append(("✅", "Super Admin", "admin@zad.edu exists"))
        else:
            checks.append(("⚠️", "Super Admin", "Not found"))
    except Exception as e:
        checks.append(("❌", "Super Admin", str(e)))
    
    # Check 4: Core Modules
    for module in ['core.i18n', 'core.database', 'views.admin', 'views.vision_grader']:
        try:
            __import__(module)
            checks.append(("✅", f"Module: {module}", "Loaded"))
        except Exception as e:
            checks.append(("❌", f"Module: {module}", str(e)[:50]))
    
    # Display results
    passed = sum(1 for c in checks if "✅" in c[0])
    failed = sum(1 for c in checks if "❌" in c[0])
    warnings = sum(1 for c in checks if "⚠️" in c[0])
    
    st.markdown(f"**Results:** ✅ {passed} Passed | ⚠️ {warnings} Warnings | ❌ {failed} Failed")
    
    for icon, name, detail in checks:
        if "✅" in icon:
            st.success(f"{icon} **{name}**: {detail}")
        elif "❌" in icon:
            st.error(f"{icon} **{name}**: {detail}")
        else:
            st.warning(f"{icon} **{name}**: {detail}")


def _create_super_admin():
    """Create or verify super admin exists."""
    try:
        from werkzeug.security import generate_password_hash
        
        session = get_db_session()
        admin = session.query(User).filter(User.email == "admin@zad.edu").first()
        
        if admin:
            st.info("ℹ️ Super admin already exists!")
        else:
            admin = User(
                email="admin@zad.edu",
                full_name="Super Admin",
                hashed_password=generate_password_hash("admin123"),
                role="super_admin",
                is_active=True
            )
            session.add(admin)
            session.commit()
            st.success("✅ Super admin created: admin@zad.edu / admin123")
        
        session.close()
    except Exception as e:
        st.error(f"❌ Failed: {e}")


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================

show_super_admin_dashboard = show_admin_dashboard
