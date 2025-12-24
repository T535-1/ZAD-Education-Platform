# -*- coding: utf-8 -*-
"""
ZAD Education Platform - AI Vision Grader | منصة زاد - المصحح الذكي
===================================================================
Teacher tool for grading student work using AI-powered image analysis.

FLOW:
1. Teacher uploads an image of student work (PNG, JPG, PDF screenshot)
2. AI analyzes the image and suggests a score + feedback
3. Teacher selects student from dropdown (filtered by school)
4. Teacher confirms/edits score and feedback
5. Form submission SAVES the Grade record to the database

DATABASE SAVE LOGIC:
- Creates a new Grade record in the `grades` table
- Links to: student_id, school_id (from session), teacher (implicit)
- Records: score, max_score, subject, feedback, graded_at
"""

import streamlit as st
import datetime
from models import get_db_session, User, Grade


def show_vision_grader():
    """Main entry point for Vision Grader view."""
    
    role = st.session_state.get('role')
    school_id = st.session_state.get('school_id')
    
    # Access check
    if role != 'teacher':
        st.error("❌ Access Denied. Teachers only.")
        return
    
    st.title("📷 AI Vision Grader | المصحح الذكي بالذكاء الاصطناعي")
    st.caption("Upload student work for AI-powered grading | ارفع عمل الطالب للتصحيح الذكي")
    
    # Two-column layout
    col1, col2 = st.columns([1, 1])
    
    # ==========================================================================
    # COLUMN 1: IMAGE UPLOAD & AI ANALYSIS
    # ==========================================================================
    with col1:
        st.subheader("📤 Upload Student Work | رفع عمل الطالب")
        
        uploaded_file = st.file_uploader(
            "Choose an image file | اختر صورة",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Upload a photo of student homework, exam, or assignment"
        )
        
        if uploaded_file:
            # Display image
            st.image(uploaded_file, caption="Uploaded Image | الصورة المرفوعة", use_container_width=True)
            
            # Subject selection
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
                    "Other | أخرى"
                ]
            )
            
            max_score = st.number_input(
                "Max Score | الدرجة الكاملة",
                min_value=10,
                max_value=100,
                value=100,
                step=10
            )
            
            # AI Analysis Button
            if st.button("🤖 Analyze with AI | تحليل بالذكاء الاصطناعي", use_container_width=True):
                with st.spinner("AI is analyzing the image... | جاري التحليل..."):
                    # Mock AI response (replace with real AI integration)
                    ai_result = _mock_ai_analysis(uploaded_file, max_score)
                    
                    # Store in session for the form
                    st.session_state['ai_suggested_score'] = ai_result['score']
                    st.session_state['ai_suggested_feedback'] = ai_result['feedback']
                    st.session_state['ai_analysis_done'] = True
                    st.session_state['selected_subject'] = subject
                    st.session_state['max_score'] = max_score
                
                st.success(f"✅ AI Analysis Complete! Suggested Score: {ai_result['score']}/{max_score}")
        
        else:
            st.info("📷 Please upload an image to begin AI grading.")
    
    # ==========================================================================
    # COLUMN 2: GRADING FORM (After AI Analysis)
    # ==========================================================================
    with col2:
        st.subheader("📝 Save Grade | حفظ الدرجة")
        
        if st.session_state.get('ai_analysis_done'):
            _render_grading_form(school_id)
        else:
            st.info("⏳ Complete AI analysis first to save the grade.")


def _mock_ai_analysis(uploaded_file, max_score: int) -> dict:
    """
    MOCK AI ANALYSIS
    Replace this with real AI integration (OpenAI GPT-4V, Google Gemini, etc.)
    
    Returns:
        dict: {'score': float, 'feedback': str}
    """
    
    import random
    
    # Simulate AI thinking
    import time
    time.sleep(1.5)  # Simulate API call delay
    
    # Generate realistic-looking mock results
    base_score = random.uniform(0.6, 0.95)
    suggested_score = round(base_score * max_score, 1)
    
    feedback_options = [
        "Excellent work! Clear handwriting and correct calculations. Keep it up! | عمل ممتاز! خط واضح وحسابات صحيحة. استمر!",
        "Good effort. Some minor errors in steps 2 and 4. Review the formulas. | جهد جيد. بعض الأخطاء البسيطة في الخطوات 2 و 4. راجع القوانين.",
        "Needs improvement. Missing several steps. Please practice more. | يحتاج تحسين. هناك خطوات ناقصة. الرجاء الممارسة أكثر.",
        "Very good! Shows understanding of concepts but needs neater presentation. | جيد جداً! يظهر فهم المفاهيم لكن يحتاج ترتيب أفضل.",
        "Outstanding performance! All answers correct with clear methodology. | أداء استثنائي! جميع الإجابات صحيحة مع منهجية واضحة."
    ]
    
    return {
        'score': suggested_score,
        'feedback': random.choice(feedback_options)
    }


def _render_grading_form(school_id: int):
    """
    GRADING FORM
    Allows teacher to select student, edit AI suggestions, and save to database.
    
    DATABASE SAVE LOGIC:
    - Creates Grade record with student_id, school_id, score, max_score, subject, feedback
    - Commits to database on form submission
    """
    
    session = get_db_session()
    
    try:
        # -------------------------------------------------------
        # FETCH STUDENTS (Filtered by teacher's school)
        # -------------------------------------------------------
        students = session.query(User).filter(
            User.school_id == school_id,
            User.role == 'student',
            User.is_active == True
        ).order_by(User.full_name).all()
        
        if not students:
            st.warning("⚠️ No students found in your school. Please add students first.")
            return
        
        # Create dropdown options
        student_options = {f"{s.full_name} ({s.email})": s.id for s in students}
        
        # -------------------------------------------------------
        # GRADING FORM
        # -------------------------------------------------------
        with st.form("grading_form", clear_on_submit=True):
            st.markdown("### 🎯 Confirm Grade Details | تأكيد تفاصيل الدرجة")
            
            # Student Selection
            selected_student = st.selectbox(
                "Select Student | اختر الطالب",
                options=list(student_options.keys()),
                help="Select the student to assign this grade to"
            )
            
            # Score (pre-filled with AI suggestion)
            ai_score = st.session_state.get('ai_suggested_score', 0)
            max_score = st.session_state.get('max_score', 100)
            
            score = st.number_input(
                "Score | الدرجة",
                min_value=0.0,
                max_value=float(max_score),
                value=float(ai_score),
                step=0.5,
                help="Edit if needed"
            )
            
            # Subject (from session)
            subject = st.session_state.get('selected_subject', "General")
            st.text_input("Subject | المادة", value=subject, disabled=True)
            
            # Feedback (pre-filled with AI suggestion)
            ai_feedback = st.session_state.get('ai_suggested_feedback', "")
            feedback = st.text_area(
                "Feedback | التعليق",
                value=ai_feedback,
                height=100,
                help="Edit AI feedback or write your own"
            )
            
            # -------------------------------------------------------
            # SUBMIT BUTTON - SAVE TO DATABASE
            # -------------------------------------------------------
            submitted = st.form_submit_button(
                "💾 Save Grade to Database | حفظ الدرجة",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                student_id = student_options[selected_student]
                
                # Create Grade record
                new_grade = Grade(
                    score=score,
                    max_score=int(max_score),
                    subject=subject.split(" |")[0],  # Take English part for DB
                    feedback=feedback,
                    student_id=student_id,
                    school_id=school_id,
                    graded_at=datetime.datetime.utcnow()
                )
                
                session.add(new_grade)
                session.commit()
                
                # Success message
                st.success(f"✅ Grade saved successfully! | تم حفظ الدرجة بنجاح!")
                st.balloons()
                
                # Clear AI session state for next grading
                for key in ['ai_analysis_done', 'ai_suggested_score', 'ai_suggested_feedback', 'selected_subject', 'max_score']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.info(f"📊 {selected_student} received {score}/{max_score}")
    
    except Exception as e:
        session.rollback()
        st.error(f"❌ Error saving grade: {e}")
    
    finally:
        session.close()


# =============================================================================
# REAL AI INTEGRATION (For Production)
# =============================================================================

def _real_ai_analysis(image_bytes: bytes, max_score: int) -> dict:
    """
    REAL AI INTEGRATION (Production)
    Uses OpenAI GPT-4 Vision or Google Gemini Vision.
    
    Environment Variables:
    - OPENAI_API_KEY: For OpenAI
    - GOOGLE_API_KEY: For Gemini
    
    NOTE: Uncomment and use this function for production.
    """
    
    import os
    
    # Try OpenAI first
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import openai
            import base64
            
            client = openai.OpenAI(api_key=openai_key)
            
            # Encode image
            b64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an educational grading assistant. Analyze student work and provide a score out of {max_score} and constructive feedback in both Arabic and English."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Analyze this student work. Provide: 1) Score out of {max_score}, 2) Brief feedback."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Parse response
            content = response.choices[0].message.content
            # Extract score (simple parsing)
            score = max_score * 0.85  # Default if parsing fails
            
            return {'score': score, 'feedback': content}
        
        except Exception as e:
            st.warning(f"OpenAI error: {e}. Falling back to mock.")
    
    # Fallback to mock
    return _mock_ai_analysis(None, max_score)
