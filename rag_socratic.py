
import os
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader

class SocraticRAG:
    """
    A RAG (Retrieval-Augmented Generation) class that uses a Socratic method
    prompt to guide students towards answers instead of providing them directly.
    """
    def __init__(self, api_key: str, school_id: int):
        """
        Initializes the SocraticRAG chain.
        
        Args:
            api_key (str): The Google Gemini API key.
            school_id (int): The ID of the school to isolate the vector store.
        """
        self.api_key = api_key
        self.school_id = school_id
        self.vector_store_path = f"faiss_index_socratic_{self.school_id}"
        
        # Embeddings model to convert text to vectors
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        
        # The core LLM for generating responses (Gemini Flash for speed)
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.7)
        
        self.vector_store = self._load_vector_store()

    def _load_vector_store(self):
        """Loads the FAISS vector store from disk if it exists."""
        if os.path.exists(self.vector_store_path):
            # Allow dangerous deserialization is required for FAISS with LangChain
            return FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
        return None

    def ingest_pdf(self, pdf_path: str):
        """
        Ingests a PDF, splits it into chunks, and stores it in the FAISS vector store.
        
        Args:
            pdf_path (str): The local path to the PDF file.
        """
        loader = PyPDFLoader(pdf_path)
        documents = loader.load_and_split()
        
        if self.vector_store:
            self.vector_store.add_documents(documents)
        else:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            
        self.vector_store.save_local(self.vector_store_path)

    def get_socratic_chain(self):
        """
        Builds and returns the conversational chain with the Socratic system prompt.
        """
        if not self.vector_store:
            return None

        # The Socratic System Prompt - CRUCIAL for the desired behavior
        socratic_system_prompt = """
        You are a Socratic Tutor. Your role is to guide the user to the answer, not to give it directly.
        When the user asks a question, use the provided context to understand the topic.
        Then, instead of answering, ask a probing question that makes the user think critically about the information.
        Guide them step-by-step until they arrive at the solution themselves.
        Never reveal the final answer. Always respond in the user's language, which is Arabic.
        
        Example:
        User: ما هي عاصمة فرنسا؟ (What is the capital of France?)
        Your Response: سؤال جيد! بالنظر إلى النص، هل يمكنك العثور على قسم يتحدث عن مدن أوروبية كبرى؟ ما هي المدن المذكورة هناك؟ (Good question! Looking at the text, can you find the section that talks about major European cities? What cities are mentioned there?)
        """

        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(socratic_system_prompt),
            HumanMessagePromptTemplate.from_template("{question}")
        ])

        # Memory to keep track of the conversation
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # The chain that combines the retriever, prompt, and LLM
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            memory=memory,
            combine_docs_chain_kwargs={"prompt": prompt_template}
        )
        return chain
