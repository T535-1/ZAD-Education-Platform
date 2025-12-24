
import streamlit as st
from core.rag_engine import RAGChatBot
import os

def show_ai_tutor():
    """
    Renders the AI Tutor page for students.
    """
    st.header("AI Tutor")

    if 'user_id' not in st.session_state:
        st.warning("Please log in to use the AI Tutor.")
        return

    # Initialize RAG chatbot
    api_key = os.getenv("GEMINI_API_KEY")
    school_id = st.session_state.get('school_id')
    if not api_key or not school_id:
        st.error("API key or School ID is not configured.")
        return
        
    rag_bot = RAGChatBot(api_key=api_key, school_id=school_id)
    
    # File uploader for documents
    uploaded_files = st.file_uploader(
        "Upload your curriculum (PDF, DOCX)", 
        type=['pdf', 'docx'], 
        accept_multiple_files=True
    )
    if uploaded_files:
        with st.spinner("Processing documents..."):
            file_paths = []
            for uploaded_file in uploaded_files:
                # Save files temporarily to process them
                temp_dir = "temp_docs"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                path = os.path.join(temp_dir, uploaded_file.name)
                with open(path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                file_paths.append(path)
            
            rag_bot.ingest_documents(file_paths)
            st.success("Documents ingested successfully!")

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your documents"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            chain = rag_bot.get_conversational_chain()
            if chain:
                with st.spinner("Thinking..."):
                    response = chain({"question": prompt})
                    st.markdown(response['answer'])
                    # To display sources:
                    # with st.expander("Sources"):
                    #     for source in response['source_documents']:
                    #         st.write(source.metadata['source'])
            else:
                st.warning("Please upload documents to begin the chat.")
        
        st.session_state.messages.append({"role": "assistant", "content": response['answer']})


def show_my_progress():
    """
    Renders the My Progress page for students.
    """
    st.header("My Progress")
    st.write("Progress tracking and visualizations will be implemented here.")
    # Example of a chart (requires plotly)
    # import plotly.express as px
    # fig = px.line(x=[1, 2, 3], y=[1, 3, 2], title="Your Progress")
    # st.plotly_chart(fig, use_container_width=True)
