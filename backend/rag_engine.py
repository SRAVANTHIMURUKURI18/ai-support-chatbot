import os
import torch

# Optimize CPU threads to make transformer embedding computation instantaneous
torch.set_num_threads(4)

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_DB_PATH = "backend/faiss_index"

# Pre-load model and vector store globally on server start (Done ONCE)
print("🚀 Initializing global RAG components...")
_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if os.path.exists(VECTOR_DB_PATH):
    _vector_store = FAISS.load_local(VECTOR_DB_PATH, _embeddings, allow_dangerous_deserialization=True)
    print("✅ FAISS Vector Database loaded into memory successfully!")
else:
    _vector_store = None

def query_rag(question: str) -> str:
    if not _vector_store:
        return "Vector database not found."
    
    # Perform lightning-fast similarity search from memory
    docs = _vector_store.similarity_search(question, k=1)
    if not docs:
        return ""
        
    return docs[0].page_content.strip()