import streamlit as st
from core.i18n import get_direction, get_align


def load_css():
    """تحميل التصميم والخطوط بشكل نظيف ومخفي"""
    direction = get_direction()
    align = get_align()

    # روابط الخطوط (تجوال للعربية + روبوتو للإنجليزية)
    # نضعها في متغير واحد
    fonts_html = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Tajawal:wght@400;500;700;900&display=swap" rel="stylesheet">
    """

    # حقن روابط الخطوط في الهيدر (مخفي)
    st.markdown(fonts_html, unsafe_allow_html=True)

    # تحديد الخط المناسب
    font_family = "'Tajawal', sans-serif"

    # تنسيقات CSS (مخفية)
    st.markdown(f"""
    <style>
        /* إجبار استخدام الخط في كل مكان */
        html, body, [class*="css"] {{
            font-family: {font_family} !important;
            direction: {direction};
        }}

        /* إخفاء الأكواد والتعليقات الزائدة */
        .element-container:has(code), .stMarkdown p {{
            font-family: {font_family} !important;
        }}

        /* تصميم كرت تسجيل الدخول */
        .stTextInput, .stForm {{
            border-radius: 15px;
        }}

        /* تنسيق الأزرار */
        .stButton button {{
            width: 100%;
            border-radius: 10px;
            font-weight: bold;
            font-family: {font_family} !important;
        }}

        /* إخفاء القوائم الافتراضية المزعجة */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


def apply_3d_style():
    """Alias for load_css - applies styling to the page"""
    load_css()