# api/langchain_logic.py
import os
import logging
import tempfile
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain, create_history_aware_retriever

def get_vectorstore_from_file(uploaded_file, google_api_key):
    # This logic is almost identical to before, but it takes a file object
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load_and_split(RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200))
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)
        vector_store = FAISS.from_documents(documents, embeddings)
        
        os.remove(tmp_file_path)
        return vector_store
    except Exception as e:
         logging.error(f"Failed to process PDF and create vector store: {e}", exc_info=True)
         return None
def get_conversational_rag_chain(vector_store, google_api_key):
    # This is identical to our Streamlit app's logic
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=google_api_key)
    
    rephrase_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given a chat history... formulate a standalone question..."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(llm, vector_store.as_retriever(), rephrase_prompt)
    
    # answer_prompt = ChatPromptTemplate.from_messages([
    #     ("system", "Answer the user's question based only on the provided context..."),
    #     MessagesPlaceholder(variable_name="context"),
    #     ("human", "{input}"),
    # ])
    answer_prompt = ChatPromptTemplate.from_template("""
        Answer the following question based only on the provided context:

        <context>
        {context}
        </context> 

        Question: {input}
        """)
    document_chain = create_stuff_documents_chain(llm, answer_prompt)
    
    return create_retrieval_chain(history_aware_retriever, document_chain)