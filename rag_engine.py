
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

class RAGChatBot:
    def __init__(self, api_key, school_id):
        self.api_key = api_key
        self.school_id = school_id
        self.vector_store_path = f"faiss_index_{self.school_id}"
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.7)
        self.vector_store = self._load_vector_store()

    def _load_vector_store(self):
        if os.path.exists(self.vector_store_path):
            return FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
        return None

    def ingest_documents(self, file_paths):
        documents = []
        for file_path in file_paths:
            if file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
            else:
                continue
            documents.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        if self.vector_store:
            self.vector_store.add_documents(splits)
        else:
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
        
        self.vector_store.save_local(self.vector_store_path)

    def get_conversational_chain(self):
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        if self.vector_store:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
            chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=True
            )
            return chain
        return None
