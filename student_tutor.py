
import streamlit as st
from core.rag_socratic import SocraticRAG
import os
import tempfile

def show_socratic_tutor():
    """
    Renders the Socratic Tutor page for students, featuring an Arabic UI.
    """
    # --- RTL and Arabic UI Configuration ---
    st.markdown("""
        <style>
            body, .stApp {
                direction: rtl;
            }
            .stButton>button {
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("👨‍🏫 المعلم السقراطي")
    st.caption("تحدث مع كتبك المدرسية ودع الذكاء الاصطناعي يرشدك إلى الإجابة.")

    # --- Authentication and Initialization ---
    if 'user_id' not in st.session_state:
        st.warning("الرجاء تسجيل الدخول لاستخدام هذه الميزة.")
        return

    api_key = os.getenv("GEMINI_API_KEY")
    school_id = st.session_state.get('school_id')

    if not api_key or not school_id:
        st.error("خطأ في الإعدادات. لا يمكن العثور على مفتاح API أو معرّف المدرسة.")
        return

    # Initialize the Socratic RAG engine
    rag_tutor = SocraticRAG(api_key=api_key, school_id=school_id)

    # --- PDF Upload and Ingestion ---
    with st.sidebar:
        st.header("📚 تغذية المعلم بالمعلومات")
        uploaded_pdf = st.file_uploader("ارفع ملف PDF هنا", type=['pdf'])
        
        if uploaded_pdf:
            with st.spinner("...جاري معالجة المستند"):
                # Save the uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                    tmpfile.write(uploaded_pdf.getvalue())
                    pdf_path = tmpfile.name
                
                # Ingest the document
                rag_tutor.ingest_pdf(pdf_path)
                
                # Clean up the temporary file
                os.remove(pdf_path)
                st.success("!تمت معالجة المستند بنجاح")

    # --- Chat Interface ---
    if rag_tutor.vector_store is None:
        st.info("يرجى رفع ملف PDF لبدء جلسة التدريس.")
        return

    if "socratic_messages" not in st.session_state:
        st.session_state.socratic_messages = []

    for message in st.session_state.socratic_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("اطرح سؤالاً حول المستند..."):
        # Display user message
        st.session_state.socratic_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display AI response
        with st.chat_message("assistant"):
            with st.spinner("...أفكر في سؤال إرشادي"):
                socratic_chain = rag_tutor.get_socratic_chain()
                if socratic_chain:
                    response = socratic_chain({"question": prompt})
                    ai_response = response['answer']
                    st.markdown(ai_response)
                    st.session_state.socratic_messages.append({"role": "assistant", "content": ai_response})
                else:
                    st.error("حدث خطأ أثناء تهيئة سلسلة المحادثة.")

