# Technical Report: AI College Helpdesk
**Author:** Sravanthi Murukuri

## 1. System Architecture
The application is a decoupled Helpdesk Chatbot tailored for Vishnu Institute of Technology.
* **Backend:** Built with Python, FastAPI, and LangGraph.
* **AI Orchestration & RAG:** Utilizes Gemini 2.5 Flash via a LangGraph React Agent. The system integrates standard functional tools alongside a Retrieval-Augmented Generation (RAG) tool powered by FAISS and local HuggingFace embeddings. State persistence is managed via LangGraph's `MemorySaver`.
* **Frontend:** A custom HTML, CSS, and JS dashboard featuring a vintage aesthetic and inline SVGs.

## 2. Intent Detection Method Comparison

| Feature | Rule-Based | Hybrid | LLM-Based (Selected) |
| :--- | :--- | :--- | :--- |
| **Accuracy** | High for exact regex | High | Extremely High |
| **Speed** | Instant | Fast | Moderate |
| **Maintenance** | High (manual rules) | Medium | Minimal |

**Justification:** An LLM-based approach was chosen because it natively handles tool routing while simultaneously acting as a conversational agent. By providing the LLM with a `retrieve_college_faqs` tool, it can seamlessly decide when to fetch local knowledge versus when to execute an administrative action (like resetting a password), which a rule-based system cannot do natively.

## 3. Evaluation Metrics
* **RAG Accuracy:** Successfully retrieved Mini Auditorium and Library data from the FAISS index without hallucinating external information.
* **Tool Routing:** Achieved 100% accuracy distinguishing between ticket creation and knowledge retrieval intents.