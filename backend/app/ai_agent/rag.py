import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.utils.config import settings

# Paths for data and vector store
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")
DATA_FILE = os.path.join(BASE_DIR, "data", "knowledge_base.txt")

def setup_rag():
    """
    1. Loads the knowledge base documents.
    2. Splits them into chunks.
    3. Generates embeddings.
    4. Stores them in ChromaDB.
    """
    print(f"Loading documents from {DATA_FILE}...")
    loader = TextLoader(DATA_FILE)
    docs = loader.load()
    
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50
    )
    splits = text_splitter.split_documents(docs)
    
    print("Generating embeddings and storing in ChromaDB...")
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    
    # Create or update the vector store
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    print("RAG setup complete! Vectors persisted to disk.")
    return vectorstore

def get_retriever():
    """
    Returns a configured retriever service connected to ChromaDB.
    """
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    
    # Load the existing vector store
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR, 
        embedding_function=embeddings
    )
    
    # Retrieve the top 2 most relevant chunks
    return vectorstore.as_retriever(search_kwargs={"k": 2})

def query_knowledge_base(query: str) -> str:
    """
    Retrieves the most relevant information for a given query.
    This acts as the retriever service for the LangGraph agent.
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)
    
    if not docs:
        return "I couldn't find any relevant information in the knowledge base."
    
    # Combine the retrieved chunks into a single text block
    result = "\n\n".join([f"Source snippet:\n{doc.page_content}" for doc in docs])
    return result
