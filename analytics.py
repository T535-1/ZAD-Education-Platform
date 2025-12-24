# -*- coding: utf-8 -*-
"""
Analytics & Early Warning Engine
================================
Analyzes student performance and generates intervention plans using AI.
"""

import os
import json
import streamlit as st
from models import get_db_session, User

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AnalyticsEngine:
    """AI-powered student analytics and early warning system."""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def get_at_risk_students(self, school_id: int) -> list:
        """
        Identify students at risk of academic failure.
        
        In a real implementation, this would analyze:
        - Grade trends
        - Attendance patterns
        - Assignment submission rates
        - Engagement metrics
        
        Args:
            school_id: The school ID to analyze
            
        Returns:
            List of at-risk student dictionaries
        """
        session = get_db_session()
        try:
            # Get students from database
            students = session.query(User).filter(
                User.school_id == school_id,
                User.role == 'student'
            ).all()
            
            at_risk = []
            
            # Analyze each student (simplified logic)
            for student in students:
                # In real app, calculate risk based on actual data
                # For now, return demo data structure
                risk_data = self._analyze_student_risk(student)
                if risk_data:
                    at_risk.append(risk_data)
            
            # If no real students, return demo data
            if not at_risk:
                return self._get_demo_at_risk_students()
            
            return at_risk
            
        except Exception as e:
            st.warning(f"Analytics Error: {e}")
            return self._get_demo_at_risk_students()
        finally:
            session.close()
    
    def _analyze_student_risk(self, student) -> dict:
        """Analyze individual student risk level."""
        # Placeholder - in production, this would analyze real data
        return None
    
    def _get_demo_at_risk_students(self) -> list:
        """Return demo at-risk students for testing."""
        return [
            {
                "id": 1,
                "name": "أحمد محمد",
                "risk": "High",
                "reason": "غياب متكرر (5 أيام) + انخفاض الدرجات بنسبة 20%"
            },
            {
                "id": 2,
                "name": "فاطمة علي",
                "risk": "Medium",
                "reason": "تأخر في تسليم 3 واجبات متتالية"
            },
            {
                "id": 3,
                "name": "عمر خالد",
                "risk": "Low",
                "reason": "انخفاض طفيف في المشاركة الصفية"
            }
        ]
    
    def generate_intervention_plan(self, student_name: str, reason: str, lang: str = "ar") -> str:
        """
        Generate an AI-powered intervention plan for at-risk student.
        
        Args:
            student_name: Name of the student
            reason: Reason for being at risk
            lang: Language code
            
        Returns:
            Intervention plan as string
        """
        if not self.model:
            return self._get_demo_intervention_plan(student_name, reason, lang)
        
        try:
            if lang == "ar":
                prompt = f"""
                أنت مستشار تربوي خبير. اكتب خطة تدخل مختصرة للطالب:
                
                الطالب: {student_name}
                المشكلة: {reason}
                
                اكتب خطة من 3-5 نقاط عملية يمكن للمعلم تنفيذها.
                """
            else:
                prompt = f"""
                You are an expert educational counselor. Write a brief intervention plan:
                
                Student: {student_name}
                Issue: {reason}
                
                Write 3-5 actionable steps the teacher can implement.
                """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return self._get_demo_intervention_plan(student_name, reason, lang)
    
    def _get_demo_intervention_plan(self, student_name: str, reason: str, lang: str) -> str:
        """Return demo intervention plan when API is unavailable."""
        if lang == "ar":
            return f"""
📋 خطة التدخل للطالب {student_name}

1. **التواصل مع ولي الأمر** - اجتماع عاجل لمناقشة الوضع
2. **جلسة دعم فردية** - لقاء أسبوعي مع المعلم المرشد
3. **تعديل الواجبات** - تقسيم المهام الكبيرة إلى أجزاء صغيرة
4. **نظام المكافآت** - تحفيز إيجابي عند الإنجاز
5. **متابعة يومية** - تقرير قصير نهاية كل يوم

⚠️ هذه خطة تجريبية - قم بإعداد مفتاح API لخطط مخصصة
"""
        else:
            return f"""
📋 Intervention Plan for {student_name}

1. **Parent Contact** - Urgent meeting to discuss the situation
2. **Individual Support** - Weekly session with counselor
3. **Assignment Modification** - Break large tasks into smaller parts
4. **Reward System** - Positive reinforcement for achievements
5. **Daily Check-in** - Brief end-of-day progress report

⚠️ This is a demo plan - Configure API key for customized plans
"""
    
    def get_class_analytics(self, classroom_id: int) -> dict:
        """Get analytics summary for a classroom."""
        return {
            "average_grade": 78.5,
            "attendance_rate": 92.3,
            "assignment_completion": 85.0,
            "at_risk_count": 3,
            "top_performers": 5
        }
    
    def get_trend_data(self, student_id: int, metric: str = "grades") -> list:
        """Get trend data for visualization."""
        # Demo data for charts
        return [
            {"month": "سبتمبر", "value": 75},
            {"month": "أكتوبر", "value": 72},
            {"month": "نوفمبر", "value": 68},
            {"month": "ديسمبر", "value": 65}
        ]


# Singleton instance
analytics_engine = AnalyticsEngine()
