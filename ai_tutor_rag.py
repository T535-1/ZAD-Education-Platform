# -*- coding: utf-8 -*-
"""
AI Tutor with RAG (Retrieval Augmented Generation)
Chat with your curriculum documents using advanced AI
Multi-tenant support with school-level document isolation
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.rag_engine import RAGChatBot
from core.config import config
from core.database import get_db
from models import Document


def show_ai_tutor_rag():
    """Enhanced AI Tutor with RAG capabilities"""

    st.title("🤖 المعلم الذكي - AI Tutor (RAG)")

    # Get current user
    if "user" not in st.session_state:
        st.error("Please login first")
        return

    user = st.session_state.user
    school_id = user.get("school_id", 1)

    # Header with gradient
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <h2 style='margin: 0; color: white;'>💡 مرحباً! أنا معلمك الذكي المتطور</h2>
        <p style='margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.95;'>
            اسألني عن محتوى الكتب والمناهج المرفوعة 📚<br>
            Ask me about your uploaded curriculum materials
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Check API configuration
    if not config.GOOGLE_API_KEY:
        st.error("⚠️ Google API Key not configured. Please set GOOGLE_API_KEY in .env file")
        st.info("Get your API key from: https://makersuite.google.com/app/apikey")
        return

    # Sidebar: Document selection
    with st.sidebar:
        st.subheader("📚 Select Document")

        # Load available documents
        db = next(get_db())
        documents = db.query(Document).filter(Document.school_id == school_id).all()

        if not documents:
            st.warning("📭 No documents uploaded yet")
            st.info("Upload documents from the Teacher Tools > Document Manager section")
            selected_doc = None
        else:
            # Document selector
            doc_options = {f"{doc.filename} ({doc.subject})": doc for doc in documents}

            selected_doc_name = st.selectbox(
                "Choose a document to chat with:",
                options=list(doc_options.keys())
            )

            selected_doc = doc_options[selected_doc_name]

            # Document info
            st.markdown(f"""
            **Subject:** {selected_doc.subject or 'N/A'}
            **Grade:** {selected_doc.grade_level or 'N/A'}
            **Chunks:** {selected_doc.chunk_count}
            **Uploaded:** {selected_doc.uploaded_at.strftime('%Y-%m-%d')}
            """)

        st.divider()

        # Chat controls
        st.subheader("⚙️ Chat Settings")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.rag_chat_history = []
            if "rag_engine" in st.session_state:
                st.session_state.rag_engine.reset_conversation()
            st.rerun()

        if st.button("📥 Export Chat", use_container_width=True):
            export_rag_chat()

        st.divider()

        # Statistics
        st.subheader("📊 Statistics")
        chat_count = len(st.session_state.get("rag_chat_history", []))
        st.metric("Messages", chat_count)

    # ========================================================================
    # MAIN CHAT INTERFACE
    # ========================================================================

    if not selected_doc:
        st.info("👈 Please select a document from the sidebar to start chatting")
        return

    # Initialize RAG engine for selected document
    if "current_doc_id" not in st.session_state or st.session_state.current_doc_id != selected_doc.id:
        st.session_state.current_doc_id = selected_doc.id

        with st.spinner("🔄 Loading document into AI brain..."):
            try:
                # Initialize RAG engine
                rag_engine = RAGChatBot(
                    api_key=config.GOOGLE_API_KEY,
                    school_id=school_id,
                    model_name=config.get_model_for_task("chat")
                )

                # Load vector store
                success = rag_engine.load_existing_vectorstore(selected_doc.id)

                if not success:
                    # Try to create vector store if it doesn't exist
                    success, message, chunk_count = rag_engine.ingest_document(
                        file_path=selected_doc.file_path,
                        subject=selected_doc.subject,
                        grade_level=selected_doc.grade_level
                    )

                    if not success:
                        st.error(f"❌ Failed to load document: {message}")
                        return

                st.session_state.rag_engine = rag_engine
                st.session_state.rag_chat_history = []

                st.success("✅ Document loaded successfully!")

            except Exception as e:
                st.error(f"❌ Error initializing RAG engine: {str(e)}")
                return

    # Initialize chat history
    if "rag_chat_history" not in st.session_state:
        st.session_state.rag_chat_history = []

    # Display chat history
    chat_container = st.container()

    with chat_container:
        if not st.session_state.rag_chat_history:
            # Welcome message
            st.markdown("""
            <div style='background: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;'>
                <strong>👋 Welcome!</strong><br>
                I've loaded the document and I'm ready to answer your questions about it.<br>
                مرحباً! لقد قمت بتحميل المستند وأنا جاهز للإجابة على أسئلتك.
            </div>
            """, unsafe_allow_html=True)

        for message in st.session_state.rag_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # Show sources if available
                if message["role"] == "assistant" and "sources" in message and message["sources"]:
                    with st.expander("📖 View Sources"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"""
                            **Source {i}:** {source.get('source_file', 'Unknown')} (Page {source.get('page', 'N/A')})
                            *{source.get('content', '')}*
                            """)

    # Chat input
    if prompt := st.chat_input("اكتب سؤالك هنا... - Type your question here..."):
        # Add user message
        st.session_state.rag_chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response using RAG
        with st.chat_message("assistant"):
            with st.spinner("🤔 Searching document and thinking..."):
                try:
                    rag_engine = st.session_state.rag_engine

                    # Get response from RAG engine
                    result = rag_engine.chat(prompt)

                    # Display answer
                    st.markdown(result["answer"])

                    # Display sources
                    if result["sources"]:
                        with st.expander("📖 View Sources"):
                            for i, source in enumerate(result["sources"], 1):
                                st.markdown(f"""
                                **Source {i}:** {source.get('source_file', 'Unknown')} (Page {source.get('page', 'N/A')})
                                *{source.get('content', '')}*
                                """)

                    # Add to chat history
                    st.session_state.rag_chat_history.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                        "timestamp": datetime.now()
                    })

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.rag_chat_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now()
                    })

    # Quick question suggestions
    if len(st.session_state.rag_chat_history) == 0:
        st.markdown("---")
        st.subheader("💡 Suggested Questions")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 Summarize this document"):
                st.rerun()

            if st.button("🎯 What are the key concepts?"):
                st.rerun()

        with col2:
            if st.button("📊 Generate practice questions"):
                st.rerun()

            if st.button("🔍 Explain the main topic"):
                st.rerun()


def export_rag_chat():
    """Export RAG chat history"""
    if "rag_chat_history" not in st.session_state or not st.session_state.rag_chat_history:
        st.warning("No chat history to export")
        return

    # Build export content
    export_content = "ZAD | زاد - RAG AI Tutor Chat History\n"
    export_content += f"Document: {st.session_state.get('current_doc_name', 'Unknown')}\n"
    export_content += f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_content += "=" * 70 + "\n\n"

    for msg in st.session_state.rag_chat_history:
        role = "Student" if msg["role"] == "user" else "AI Tutor"
        timestamp = msg.get("timestamp", datetime.now()).strftime("%Y-%m-%d %H:%M:%S")

        export_content += f"[{timestamp}] {role}:\n"
        export_content += f"{msg['content']}\n"

        # Add sources if present
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            export_content += "\nSources:\n"
            for i, source in enumerate(msg["sources"], 1):
                export_content += f"  {i}. {source.get('source_file', 'Unknown')} (Page {source.get('page', 'N/A')})\n"
                export_content += f"     {source.get('content', '')[:100]}...\n"

        export_content += "\n" + "-" * 70 + "\n\n"

    # Create download button
    st.sidebar.download_button(
        label="⬇️ Download Chat History",
        data=export_content.encode('utf-8'),
        file_name=f"rag_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )


# Entry point
if __name__ == "__main__":
    show_ai_tutor_rag()
