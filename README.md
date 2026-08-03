# VIT AI Helpdesk

An intelligent campus support chatbot powered by Gemini 2.5 Flash, LangGraph, and a local FAISS RAG implementation.

## How to Run

1. Navigate to the `backend/` folder.
2. Ensure your virtual environment is active: `source venv/bin/activate`
3. Install the updated dependencies (including sentence-transformers):
   `pip install -r requirements.txt`
4. Set your API Key: `export GEMINI_API_KEY="your-key-here"`
5. Start the server: `python main.py`
6. Open `frontend/index.html` in your browser.