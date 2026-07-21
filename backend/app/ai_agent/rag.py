import os
import chromadb
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
    if settings.CHROMA_HOST:
        print(f"Connecting to remote ChromaDB at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}")
        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings, 
            client=client
        )
    else:
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings, 
            persist_directory=CHROMA_DB_DIR
        )
    print("RAG setup complete! Vectors persisted.")
    return vectorstore

def get_retriever():
    """
    Returns a configured retriever service connected to ChromaDB.
    """
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    
    # Load the existing vector store
    if settings.CHROMA_HOST:
        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        vectorstore = Chroma(
            client=client, 
            embedding_function=embeddings
        )
    else:
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR, 
            embedding_function=embeddings
        )
    
    # Retrieve the top 2 most relevant chunks
    return vectorstore.as_retriever(search_kwargs={"k": 2})

def query_knowledge_base_with_score(query: str) -> tuple[str, bool]:
    """
    Retrieves the most relevant information for a given query,
    along with a low confidence flag if the match isn't strong enough.
    """
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    
    # Load the existing vector store
    if settings.CHROMA_HOST:
        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        vectorstore = Chroma(
            client=client, 
            embedding_function=embeddings
        )
    else:
        vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR, 
            embedding_function=embeddings
        )
        
    docs_and_scores = vectorstore.similarity_search_with_score(query, k=2)
    
    if not docs_and_scores:
        return "I couldn't find any relevant information in the knowledge base.", True
    
    # In Chroma, using default L2 distance, lower score is better.
    # We set a threshold for low confidence (e.g., > 0.5 can be considered low confidence)
    best_score = docs_and_scores[0][1]
    is_low_confidence = best_score > 0.5
    
    # Combine the retrieved chunks into a single text block
    result = "\n\n".join([f"Source snippet (score {score:.2f}):\n{doc.page_content}" for doc, score in docs_and_scores])
    return result, is_low_confidence

def query_knowledge_base(query: str) -> str:
    """Legacy wrapper for existing usage without confidence score."""
    result, _ = query_knowledge_base_with_score(query)
    return result
