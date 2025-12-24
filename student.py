# -*- coding: utf-8 -*-
"""
Student Dashboard - Unified Module
===================================
ZAD Education Platform | منصة زاد التعليمية

This module combines all student-facing functionality:
- Dashboard overview
- AI Tutor with RAG
- Adaptive Learning Path
- Progress tracking
"""

import streamlit as st
import os
from core.i18n import get_text


def show_student_dashboard():
    """
    Main student dashboard with all features in tabs.
    """
    st.header(f"🎓 {get_text('student_hub', 'Student Hub')}")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📊 {get_text('dashboard', 'Dashboard')}",
        f"🤖 {get_text('ai_tutor', 'AI Tutor')}",
        f"📈 {get_text('adaptive_learning_path', 'Adaptive Learning')}",
        f"📉 {get_text('my_progress', 'My Progress')}"
    ])

    with tab1:
        _show_overview()
    
    with tab2:
        _show_ai_tutor()
    
    with tab3:
        _show_adaptive_learning()
    
    with tab4:
        _show_progress()


def _show_overview():
    """Dashboard overview tab."""
    st.subheader(get_text('overview', 'Overview'))
    st.info(get_text('student_welcome_message', 'Welcome to your personal learning space!'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(get_text('my_courses', 'My Courses'))
        courses = ["الرياضيات - Mathematics", "العلوم - Science", "اللغة العربية - Arabic"]
        for course in courses:
            st.write(f"📚 {course}")

    with col2:
        st.subheader(get_text('upcoming_deadlines', 'Upcoming Deadlines'))
        st.warning("📝 اختبار الرياضيات - غداً | Math Quiz - Tomorrow")
        st.success("✅ مشروع AI - تم التسليم | AI Project - Submitted")


def _show_ai_tutor():
    """AI Tutor with RAG functionality."""
    st.subheader(f"🤖 {get_text('ai_tutor', 'AI Tutor')}")
    
    if 'user_id' not in st.session_state:
        st.warning("يرجى تسجيل الدخول - Please log in")
        return

    # Import ZAD persona
    try:
        from core.zad_persona import get_persona_prompt, ZAD_PERSONALITY
        st.info(ZAD_PERSONALITY.get("greeting_ar", "مرحباً!"))
    except ImportError:
        pass

    # Initialize or get API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.warning(get_text('api_key_missing', 'API key not configured. Using demo mode.'))
    
    # File uploader for curriculum
    with st.expander("📄 " + get_text('upload_curriculum', 'Upload Curriculum Documents')):
        uploaded_files = st.file_uploader(
            get_text('upload_curriculum_desc', 'Upload PDF or DOCX files'),
            type=['pdf', 'docx'],
            accept_multiple_files=True,
            key="curriculum_upload"
        )
        
        if uploaded_files:
            with st.spinner(get_text('processing', 'Processing...')):
                try:
                    from core.rag_engine import RAGChatBot
                    school_id = st.session_state.get('school_id', 'default')
                    rag_bot = RAGChatBot(api_key=api_key, school_id=school_id)
                    
                    temp_dir = "temp_docs"
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    file_paths = []
                    for f in uploaded_files:
                        path = os.path.join(temp_dir, f.name)
                        with open(path, "wb") as out:
                            out.write(f.getvalue())
                        file_paths.append(path)
                    
                    rag_bot.ingest_documents(file_paths)
                    st.success(get_text('upload_success', 'Documents processed!'))
                except Exception as e:
                    st.error(f"Error: {e}")

    # Chat interface
    if "student_messages" not in st.session_state:
        st.session_state.student_messages = []

    # Display chat history
    for msg in st.session_state.student_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input(get_text('ask_question', 'Ask a question...')):
        st.session_state.student_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner(get_text('brain_thinking', 'Thinking...')):
                # Try RAG first, fallback to demo
                try:
                    from core.rag_engine import RAGChatBot
                    school_id = st.session_state.get('school_id', 'default')
                    rag_bot = RAGChatBot(api_key=api_key, school_id=school_id)
                    chain = rag_bot.get_conversational_chain()
                    
                    if chain:
                        response = chain({"question": prompt})
                        answer = response.get('answer', 'No answer available.')
                    else:
                        answer = _demo_response(prompt)
                except Exception:
                    answer = _demo_response(prompt)
                
                st.markdown(answer)
                st.session_state.student_messages.append({"role": "assistant", "content": answer})


def _show_adaptive_learning():
    """Adaptive learning path generator."""
    st.subheader(get_text('generate_path_header', 'Generate Your Learning Path'))
    
    topic = st.text_input(
        get_text('adaptive_topic_label', "Enter a topic (e.g., 'Calculus')"),
        key="adaptive_topic"
    )
    
    if st.button(get_text('adaptive_generate_btn', 'Generate Path'), type="primary", use_container_width=True):
        if not topic:
            st.warning(get_text('enter_topic', 'Please enter a topic.'))
        else:
            with st.spinner(get_text('brain_thinking', 'AI is designing your path...')):
                path = f"""
#### 🎯 Learning Path for: {topic}

**الخطوة 1: الأساسيات | Step 1: Basics**
- 📺 Watch: Introduction to {topic}
- ✍️ Quiz: Basic Concepts

**الخطوة 2: المستوى المتوسط | Step 2: Intermediate**
- 📋 Prerequisite: Score > 80% on Basic Quiz
- 🎮 Activity: Interactive simulation

**الخطوة 3: التطبيقات المتقدمة | Step 3: Advanced**
- 🏆 Project: Apply {topic} to a real problem
"""
                st.markdown(path)
                st.progress(0.33)
                st.caption(get_text('progress_hint', 'Complete steps to unlock the next level!'))


def _show_progress():
    """Progress tracking and visualization."""
    st.subheader(get_text('my_progress', 'My Progress'))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 " + get_text('overall_average', 'Average'), "85%", "+5%")
    with col2:
        st.metric("✅ " + get_text('completed_courses', 'Completed'), "3/5")
    with col3:
        st.metric("🏆 " + get_text('badges', 'Badges'), "7")
    
    st.markdown("---")
    
    # Progress bars
    st.write("**" + get_text('course_progress', 'Course Progress') + ":**")
    
    progress_data = [
        ("الرياضيات - Mathematics", 0.85),
        ("العلوم - Science", 0.72),
        ("اللغة العربية - Arabic", 0.90),
    ]
    
    for course, progress in progress_data:
        st.write(f"📚 {course}")
        st.progress(progress)


def _demo_response(question: str) -> str:
    """Generate a demo Socratic response."""
    responses = {
        "ar": f"""
🎓 **سؤال رائع!**

بدلاً من إعطائك الإجابة مباشرة، دعني أساعدك على التفكير:

1. ما الذي تعرفه بالفعل عن هذا الموضوع؟
2. ما هي الخطوة الأولى التي يمكنك البدء بها؟
3. هل يمكنك ربط هذا بشيء تعلمته سابقاً؟

💡 **تلميح:** حاول تقسيم السؤال إلى أجزاء أصغر.
        """,
        "en": f"""
🎓 **Great question!**

Instead of giving you the answer directly, let me help you think:

1. What do you already know about this topic?
2. What's the first step you could take?
3. Can you connect this to something you've learned before?

💡 **Hint:** Try breaking the question into smaller parts.
        """
    }
    
    # Detect language
    lang = "ar" if any('\u0600' <= c <= '\u06FF' for c in question) else "en"
    return responses[lang]
