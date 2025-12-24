
import streamlit as st
import pandas as pd
import plotly.express as px
from core.i18n import get_text
from core.style import load_css

def show_teacher_dashboard():
    """
    Teacher Dashboard View
    Supports RTL/LTR based on selected language
    """
    
    load_css()
    
    # Mock Data
    stats = {
        "classes": 5,
        "students": 142,
        "avg_grade": 88
    }

    # --- Header Section ---
    st.markdown(f"## 👨‍🏫 {get_text('welcome')} - {st.session_state.get('username', 'Teacher')}")
    st.markdown("---")

    # --- Metrics Row ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=get_text("total_classes"),
            value=stats["classes"],
            delta="2 " + get_text("new")
        )
    with col2:
        st.metric(
            label=get_text("active_students"),
            value=stats["students"],
            delta="5% ⬆️"
        )
    with col3:
        st.metric(
            label=get_text("avg_performance"),
            value=f"{stats['avg_grade']}%",
            delta="1.2% ⬆️"
        )

    st.write("") # Spacer

    # --- Main Tabs ---
    tab1, tab2, tab3 = st.tabs([
        f"📊 {get_text('dashboard')}", 
        f"🤖 {get_text('ai_tools')}", 
        f"📅 {get_text('schedule')}"
    ])

    # --- TAB 1: Overview & Analytics ---
    with tab1:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader(get_text("student_performance"))
            df = pd.DataFrame({
                'Grade': ['A', 'B', 'C', 'D', 'F'],
                'Count': [40, 65, 25, 10, 2]
            })
            fig = px.bar(df, x='Grade', y='Count', color='Count', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader(get_text("quick_alerts"))
            st.info("📝 3 assignments pending review")
            st.warning("⚠️ Student 'Ahmed' absent for 3 days")
            st.success("✅ Weekly plan approved")

    # --- TAB 2: AI Productivity Tools ---
    with tab2:
        st.markdown(f"### 🚀 {get_text('ai_tools')}")
        
        tc1, tc2, tc3 = st.columns(3)
        
        with tc1:
            st.markdown("<div style='padding:20px; border:1px solid #ddd; border-radius:10px; text-align:center; cursor: pointer;'><h3>📝</h3><h4>Lesson Planner</h4><p>مولد خطط الدروس</p></div>", unsafe_allow_html=True)
            if st.button("Start Planning", key="btn_plan", use_container_width=True):
                st.toast("Redirecting to planner...", icon="⏳")

        with tc2:
            st.markdown("<div style='padding:20px; border:1px solid #ddd; border-radius:10px; text-align:center; cursor: pointer;'><h3>👁️</h3><h4>Vision Grader</h4><p>المصحح البصري الآلي</p></div>", unsafe_allow_html=True)
            if st.button("Open Grader", key="btn_grade", use_container_width=True):
                 st.toast("Activating camera...", icon="📸")

        with tc3:
            st.markdown("<div style='padding:20px; border:1px solid #ddd; border-radius:10px; text-align:center; cursor: pointer;'><h3>🗣️</h3><h4>Voice Cloning</h4><p>التوأم الصوتي الرقمي</p></div>", unsafe_allow_html=True)
            if st.button("Clone Voice", key="btn_voice", use_container_width=True):
                 st.toast("This feature is available in the Pro version", icon="⭐")

    # --- TAB 3: Schedule ---
    with tab3:
        schedule_data = {
            "الحصة": ["الأولى", "الثانية", "الثالثة", "الرابعة"],
            "المادة": ["رياضيات", "رياضيات", "فراغ", "علوم بيانات"],
            "الفصل": ["4/A", "5/B", "-", "11/C"]
        }
        if st.session_state.get("language", "ar") == "en":
            schedule_data = {
                "Period": ["First", "Second", "Third", "Fourth"],
                "Subject": ["Math", "Math", "Break", "Data Science"],
                "Class": ["4/A", "5/B", "-", "11/C"]
            }
        st.table(pd.DataFrame(schedule_data))
