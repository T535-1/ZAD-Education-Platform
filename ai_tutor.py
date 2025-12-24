# -*- coding: utf-8 -*-
"""
AI Tutor Module
Provides an intelligent tutoring assistant using Gemini/OpenAI API
Supports Arabic and English, with session-persistent chat history
"""

import streamlit as st
import os
from datetime import datetime


def show_ai_tutor():
    """AI Tutor chat interface with API key configuration"""
    st.title("🤖 المعلم الذكي - AI Tutor")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;">
        <h3>مرحباً! أنا معلمك الذكي 👋</h3>
        <p>يمكنني مساعدتك في:</p>
        <ul>
            <li>📚 شرح المفاهيم الدراسية</li>
            <li>✏️ حل المسائل الرياضية</li>
            <li>🔬 تبسيط المواضيع العلمية</li>
            <li>📝 المساعدة في الواجبات</li>
            <li>🌍 الإجابة على أسئلتك التعليمية</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # API Key Configuration
    api_provider = configure_api_key()

    if not api_provider:
        st.warning("⚠️ يرجى إدخال مفتاح API لبدء الدردشة - Please enter an API key to start chatting")
        return

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "tutor_context" not in st.session_state:
        st.session_state.tutor_context = """
أنت معلم ذكي متخصص في التعليم. دورك هو:
1. شرح المفاهيم بطريقة بسيطة ومفهومة
2. استخدام أمثلة عملية وواقعية
3. تشجيع التفكير النقدي
4. طرح أسئلة توضيحية لفهم احتياجات الطالب
5. التحلي بالصبر والإيجابية

You are an intelligent educational tutor. Your role is to:
1. Explain concepts in a simple and understandable way
2. Use practical, real-world examples
3. Encourage critical thinking
4. Ask clarifying questions to understand student needs
5. Be patient and positive
"""

    # Display chat history
    st.subheader("💬 المحادثة - Chat")

    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("اكتب سؤالك هنا... - Type your question here..."):
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 جاري التفكير... - Thinking..."):
                try:
                    response = get_ai_response(
                        prompt,
                        api_provider,
                        st.session_state.get("api_key"),
                        st.session_state.chat_history
                    )

                    st.markdown(response)

                    # Add assistant message to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now()
                    })

                except Exception as e:
                    error_msg = f"❌ خطأ - Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now()
                    })

    # Sidebar controls
    with st.sidebar:
        st.subheader("⚙️ إعدادات المحادثة - Chat Settings")

        if st.button("🗑️ مسح المحادثة - Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

        if st.button("📥 تصدير المحادثة - Export Chat"):
            export_chat()

        st.divider()

        st.subheader("📊 إحصائيات - Statistics")
        st.metric("عدد الرسائل - Messages", len(st.session_state.chat_history))

        user_messages = len([m for m in st.session_state.chat_history if m["role"] == "user"])
        st.metric("أسئلتي - My Questions", user_messages)


def configure_api_key():
    """Configure API key for AI service"""
    st.sidebar.subheader("🔑 إعدادات API - API Settings")

    # Check for existing API key in environment or session
    existing_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

    if existing_key and "api_key" not in st.session_state:
        st.session_state.api_key = existing_key
        st.session_state.api_provider = "gemini" if "GEMINI_API_KEY" in os.environ else "openai"

    # Provider selection
    api_provider = st.sidebar.selectbox(
        "اختر المزود - Select Provider",
        options=["Gemini (Google)", "OpenAI (ChatGPT)"],
        index=0
    )

    provider_key = "gemini" if "Gemini" in api_provider else "openai"

    # API Key input
    api_key = st.sidebar.text_input(
        "مفتاح API - API Key",
        type="password",
        value=st.session_state.get("api_key", ""),
        help="أدخل مفتاح API الخاص بك - Enter your API key"
    )

    if api_key:
        st.session_state.api_key = api_key
        st.session_state.api_provider = provider_key
        st.sidebar.success(f"✅ متصل - Connected to {api_provider}")
        return provider_key

    if "api_key" in st.session_state and st.session_state.api_key:
        st.sidebar.success(f"✅ متصل - Connected to {api_provider}")
        return provider_key

    st.sidebar.info("""
    **كيفية الحصول على مفتاح API:**

    **Gemini API:**
    1. اذهب إلى [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. قم بإنشاء مفتاح API جديد
    3. انسخ المفتاح والصقه أعلاه

    **OpenAI API:**
    1. اذهب إلى [OpenAI Platform](https://platform.openai.com/api-keys)
    2. قم بإنشاء مفتاح API جديد
    3. انسخ المفتاح والصقه أعلاه
    """)

    return None


def get_ai_response(prompt, provider, api_key, chat_history):
    """Get AI response from selected provider"""

    if provider == "gemini":
        return get_gemini_response(prompt, api_key, chat_history)
    elif provider == "openai":
        return get_openai_response(prompt, api_key, chat_history)
    else:
        return "❌ Provider not supported"


def get_gemini_response(prompt, api_key, chat_history):
    """Get response from Gemini API"""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        # Build conversation history
        messages = []

        # Add system context
        messages.append({
            "role": "user",
            "parts": [st.session_state.tutor_context]
        })

        messages.append({
            "role": "model",
            "parts": ["فهمت دوري كمعلم ذكي. أنا جاهز لمساعدتك! - I understand my role as an AI tutor. I'm ready to help you!"]
        })

        # Add chat history (last 10 messages for context)
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

        for msg in recent_history:
            if msg["role"] == "user":
                messages.append({
                    "role": "user",
                    "parts": [msg["content"]]
                })
            elif msg["role"] == "assistant":
                messages.append({
                    "role": "model",
                    "parts": [msg["content"]]
                })

        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Generate response
        chat = model.start_chat(history=messages[:-1])  # Exclude the current prompt
        response = chat.send_message(prompt)

        return response.text

    except ImportError:
        return "❌ يرجى تثبيت مكتبة google-generativeai: pip install google-generativeai"
    except Exception as e:
        return f"❌ خطأ في الاتصال بـ Gemini: {str(e)}"


def get_openai_response(prompt, api_key, chat_history):
    """Get response from OpenAI API"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # Build messages array
        messages = [
            {"role": "system", "content": st.session_state.tutor_context}
        ]

        # Add chat history (last 10 messages)
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history

        for msg in recent_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })

        # Generate response
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo" for lower cost
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content

    except ImportError:
        return "❌ يرجى تثبيت مكتبة openai: pip install openai"
    except Exception as e:
        return f"❌ خطأ في الاتصال بـ OpenAI: {str(e)}"


def export_chat():
    """Export chat history to text file"""
    if not st.session_state.chat_history:
        st.warning("لا توجد محادثة لتصديرها - No chat history to export")
        return

    # Build export content
    export_content = "ZAD | زاد - AI Tutor Chat History\n"
    export_content += f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_content += "=" * 50 + "\n\n"

    for msg in st.session_state.chat_history:
        role = "الطالب - Student" if msg["role"] == "user" else "المعلم الذكي - AI Tutor"
        timestamp = msg.get("timestamp", datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

        export_content += f"[{timestamp}] {role}:\n"
        export_content += f"{msg['content']}\n\n"
        export_content += "-" * 50 + "\n\n"

    # Create download button
    st.sidebar.download_button(
        label="⬇️ تحميل المحادثة - Download Chat",
        data=export_content.encode('utf-8'),
        file_name=f"ai_tutor_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
