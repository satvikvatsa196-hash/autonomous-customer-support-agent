import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.ai_agent.rag import setup_rag

if __name__ == "__main__":
    print("Initializing RAG Knowledge Base...")
    setup_rag()
    print("Done!")
