# -*- coding: utf-8 -*-
"""
ZAD Education Platform - Internationalization | منصة زاد - الترجمة
===================================================================
Bilingual support (Arabic/English) with session-based language switching.
"""

import streamlit as st

# =============================================================================
# TRANSLATIONS DICTIONARY
# =============================================================================

TRANSLATIONS = {
    # Login Page
    "app_title": {
        "en": "🎓 ZAD Education Platform",
        "ar": "🎓 منصة زاد التعليمية"
    },
    "login": {
        "en": "Login",
        "ar": "تسجيل الدخول"
    },
    "email": {
        "en": "Email",
        "ar": "البريد الإلكتروني"
    },
    "password": {
        "en": "Password",
        "ar": "كلمة المرور"
    },
    "login_button": {
        "en": "🔐 Login",
        "ar": "🔐 دخول"
    },
    "demo_credentials": {
        "en": "🔑 Demo Credentials",
        "ar": "🔑 بيانات تجريبية"
    },
    "welcome": {
        "en": "Welcome",
        "ar": "مرحباً"
    },
    "logout": {
        "en": "🚪 Logout",
        "ar": "🚪 خروج"
    },
    
    # Roles
    "role": {
        "en": "Role",
        "ar": "الدور"
    },
    "super_admin": {
        "en": "Super Admin",
        "ar": "المشرف العام"
    },
    "school_admin": {
        "en": "School Admin",
        "ar": "مشرف المدرسة"
    },
    "teacher": {
        "en": "Teacher",
        "ar": "معلم"
    },
    "student": {
        "en": "Student",
        "ar": "طالب"
    },
    "parent": {
        "en": "Parent",
        "ar": "ولي الأمر"
    },
    
    # Admin Dashboard
    "admin_dashboard": {
        "en": "🛡️ Super Admin Dashboard",
        "ar": "🛡️ لوحة المشرف العام"
    },
    "schools": {
        "en": "🏫 Schools",
        "ar": "🏫 المدارس"
    },
    "users": {
        "en": "👥 Users & Master Key",
        "ar": "👥 المستخدمين والمفتاح الرئيسي"
    },
    "statistics": {
        "en": "📊 Statistics",
        "ar": "📊 الإحصائيات"
    },
    "create_school": {
        "en": "➕ Create New School",
        "ar": "➕ إنشاء مدرسة جديدة"
    },
    "existing_schools": {
        "en": "📋 Existing Schools",
        "ar": "📋 المدارس الحالية"
    },
    
    # Teacher Dashboard
    "teacher_dashboard": {
        "en": "👨‍🏫 Teacher Dashboard",
        "ar": "👨‍🏫 لوحة المعلم"
    },
    "vision_grader": {
        "en": "📷 AI Vision Grader",
        "ar": "📷 المصحح الذكي"
    },
    "library": {
        "en": "📚 PDF Library",
        "ar": "📚 المكتبة الرقمية"
    },
    "online_classes": {
        "en": "🎥 Online Classes",
        "ar": "🎥 الحصص الأونلاين"
    },
    
    # Student Dashboard
    "student_dashboard": {
        "en": "🎓 My Dashboard",
        "ar": "🎓 لوحتي"
    },
    "my_grades": {
        "en": "📊 My Grades",
        "ar": "📊 درجاتي"
    },
    "resources": {
        "en": "📚 Resources",
        "ar": "📚 المصادر"
    },
    "upcoming_classes": {
        "en": "🎥 Upcoming Classes",
        "ar": "🎥 الحصص القادمة"
    },
    
    # Parent Dashboard
    "parent_dashboard": {
        "en": "👨‍👩‍👧 Parent Dashboard",
        "ar": "👨‍👩‍👧 لوحة ولي الأمر"
    },
    "my_children": {
        "en": "👧 My Children",
        "ar": "👧 أبنائي"
    },
    "child_grades": {
        "en": "📊 Child's Grades",
        "ar": "📊 درجات الطفل"
    },
    
    # Common
    "save": {
        "en": "💾 Save",
        "ar": "💾 حفظ"
    },
    "cancel": {
        "en": "❌ Cancel",
        "ar": "❌ إلغاء"
    },
    "delete": {
        "en": "🗑️ Delete",
        "ar": "🗑️ حذف"
    },
    "search": {
        "en": "🔍 Search",
        "ar": "🔍 بحث"
    },
    "no_data": {
        "en": "No data found",
        "ar": "لا توجد بيانات"
    },
    "success": {
        "en": "Success!",
        "ar": "تم بنجاح!"
    },
    "error": {
        "en": "Error!",
        "ar": "خطأ!"
    },
    
    # Impersonation
    "impersonation_mode": {
        "en": "🎭 Impersonation Mode",
        "ar": "🎭 وضع انتحال الهوية"
    },
    "exit_impersonation": {
        "en": "🔴 Exit Impersonation",
        "ar": "🔴 الخروج من الانتحال"
    },
    "login_as": {
        "en": "🎭 Login As",
        "ar": "🎭 الدخول كـ"
    },
    "reset_password": {
        "en": "🔐 Reset Password",
        "ar": "🔐 إعادة تعيين كلمة المرور"
    },
    
    # Language
    "language": {
        "en": "🌐 Language",
        "ar": "🌐 اللغة"
    },
    "english": {
        "en": "English",
        "ar": "English"
    },
    "arabic": {
        "en": "العربية",
        "ar": "العربية"
    },
    
    # Error Messages (for existing pages)
    "brain_error_auth": {
        "en": "⚠️ Please login to access this feature.",
        "ar": "⚠️ يرجى تسجيل الدخول للوصول لهذه الميزة."
    },
    "brain_error_role": {
        "en": "⚠️ You don't have permission to access this feature.",
        "ar": "⚠️ ليس لديك صلاحية للوصول لهذه الميزة."
    },
    "brain_loading": {
        "en": "Loading...",
        "ar": "جاري التحميل..."
    },
    "brain_success": {
        "en": "✅ Success!",
        "ar": "✅ تم بنجاح!"
    },
    
    # Educational Games
    "games_title": {
        "en": "🎮 Educational Games",
        "ar": "🎮 الألعاب التعليمية"
    },
    "games_start": {
        "en": "Start Game",
        "ar": "ابدأ اللعبة"
    },
    
    # WhatsApp
    "whatsapp_title": {
        "en": "📱 WhatsApp Connect",
        "ar": "📱 ربط الواتساب"
    },
    
    # Early Warning
    "early_warning_title": {
        "en": "⚠️ Early Warning System",
        "ar": "⚠️ نظام الإنذار المبكر"
    },
    
    # Voice
    "voice_title": {
        "en": "🎤 ZAD Voice",
        "ar": "🎤 صوت زاد"
    },
    
    # Generic
    "loading": {
        "en": "Loading...",
        "ar": "جاري التحميل..."
    },
    "submit": {
        "en": "Submit",
        "ar": "إرسال"
    },
    "back": {
        "en": "Back",
        "ar": "رجوع"
    },
    "next": {
        "en": "Next",
        "ar": "التالي"
    },
    "confirm": {
        "en": "Confirm",
        "ar": "تأكيد"
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_language() -> str:
    """Get current language from session state."""
    return st.session_state.get('language', 'ar')  # Default Arabic


def set_language(lang: str):
    """Set language in session state."""
    st.session_state['language'] = lang


def t(key: str) -> str:
    """
    Translate key to current language.
    Usage: t("login") -> "تسجيل الدخول" (if Arabic)
    """
    lang = get_language()
    
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get('en', key))
    
    return key


def render_language_toggle():
    """Render language toggle button in sidebar."""
    
    current_lang = get_language()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "🇬🇧 EN",
            use_container_width=True,
            type="primary" if current_lang == 'en' else "secondary"
        ):
            set_language('en')
            st.rerun()
    
    with col2:
        if st.button(
            "🇸🇦 عربي",
            use_container_width=True,
            type="primary" if current_lang == 'ar' else "secondary"
        ):
            set_language('ar')
            st.rerun()


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

def get_text(key: str, lang: str = None) -> str:
    """
    Backward compatible get_text function.
    Accepts optional lang parameter for existing code.
    Usage: get_text('login') or get_text('login', 'ar')
    """
    if lang is None:
        lang = get_language()
    
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get('en', key))
    
    return key


def get_direction() -> str:
    """Get text direction based on current language (RTL for Arabic)."""
    lang = get_language()
    return "rtl" if lang == "ar" else "ltr"


def get_align() -> str:
    """Get text alignment based on current language."""
    lang = get_language()
    return "right" if lang == "ar" else "left"
