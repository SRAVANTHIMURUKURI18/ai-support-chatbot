# 🎓 VIThelpdesk: AI-Powered College Helpdesk with Intelligent Tool Selection

An AI-powered College Helpdesk chatbot developed to automate common student support services such as password reset, support ticket management, and answering college-related queries. The chatbot identifies the user's intent, selects the appropriate backend tool, and returns accurate responses using a Rule-Based Intent Engine and Retrieval-Augmented Generation (RAG).

---

# 📌 Project Overview

VIThelpdesk is designed to simplify communication between students and the college helpdesk by providing instant responses to frequently asked questions and automating repetitive support tasks.

The chatbot can:

- 🔹 Understand user requests
- 🔹 Detect user intent
- 🔹 Select the correct backend tool
- 🔹 Execute the requested operation
- 🔹 Retrieve institutional information using RAG
- 🔹 Return meaningful responses

Unlike cloud-based AI assistants, this project uses a local Rule-Based Intent Detection Engine along with a structured JSON-based RAG system, making it fast, lightweight, and independent of external API costs for knowledge retrieval.

---

# ✨ Features

## 🔐 Authentication

- Student Login
- Student Registration
- Secure Password Reset
- User Profile Management

---

## 🎫 Support Ticket Management

- Create Support Tickets
- View Existing Tickets
- Track Ticket Status

---

## 📚 College Information (RAG)

Students can ask questions regarding:

- Bus Timings
- Hostel Facilities
- Hostel Outing Procedure
- Fee Details
- Library Timings
- Academic Regulations
- Attendance Requirements
- Placement Statistics
- AP EAPCET Cutoffs
- Admission Documents
- IT Support

---

## 🤖 Intelligent Tool Selection

The chatbot automatically selects the correct backend tool depending on the user's request.

Example:

| User Query | Selected Tool |
|------------|---------------|
| Reset my password | Password Reset Tool |
| Create a ticket | Ticket Management |
| Show my tickets | Ticket Listing |
| Hostel timings | RAG Retrieval |
| Bus timings | RAG Retrieval |
| Placement statistics | RAG Retrieval |

---

# 🏗️ System Architecture

```
                        Student
                           │
                           ▼
                  Frontend (HTML/CSS/JS)
                           │
                     HTTP REST API
                           │
                           ▼
                    FastAPI Backend
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
 Rule-Based Intent     Session Manager    Tool Selector
     Detection                             │
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
              JSON RAG Engine                             SQLite Database
              (FAISS Search)                         (Users & Support Tickets)
                     │
                     ▼
               Chatbot Response
```

---

# 🧠 Intent Detection

Before implementation, three approaches were studied.

| Approach | Advantages | Limitations |
|-----------|------------|-------------|
| Rule-Based | Fast, deterministic, zero API cost | Limited flexibility |
| LLM-Based | Excellent semantic understanding | API cost, latency |
| Hybrid | Combines both approaches | Higher complexity |

## Selected Approach

The **Hybrid Approach** was selected because the College Helpdesk consists of both **structured student service workflows** and **knowledge-based information retrieval**.

Examples include:

- Login and Registration
- Password Reset
- Ticket Creation and Ticket Listing
- Chat History and Announcements
- College Handbook Queries (Hostel Rules, Bus Timings, Fee Information, Attendance, etc.)

Structured workflows are handled using **rule-based intent detection and state management**, ensuring fast and predictable execution. Knowledge-based queries are handled through **semantic retrieval using FAISS and HuggingFace embeddings**, which retrieves the most relevant information from the college handbook. Dynamic student-related operations such as ticket management, profiles, and chat history are performed using **SQLite and SQLAlchemy**.

This hybrid design combines the speed and reliability of rule-based routing with the flexibility of semantic search, while avoiding the latency and cost of external LLM APIs.

---

# 📂 Repository Structure

```
ai-support-chatbot/
│
├── backend/
│   ├── venv/
│   ├── chatbot.py
│   ├── database.py
│   ├── faq_data.txt
│   ├── faq_dataset.json
│   ├── faq_knowledge.py
│   ├── helpdesk.db
│   ├── main.py
│   ├── models.py
│   ├── rag_engine.py
│   ├── requirements.txt
│   ├── seed_announcement.py
│   └── tools.py
│
├── dataset/
│   └── test_cases.json
│
├── frontend/
│   ├── app.js
│   ├── chat.html
│   ├── index.html
│   ├── profile.html
│   ├── signup.html
│   └── styles.css
├── helpdesk.db
├── README.md
├── REPORT (1).pdf
├── REPORT.md
└── test_eval.py
```

---

# ⚙️ Technologies Used

## Frontend

- HTML5
- CSS3
- JavaScript

## Backend

- Python
- FastAPI

## AI

- Rule-Based Intent Detection
- LangChain
- FAISS
- Sentence Transformers

## Database

- SQLite

---
# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/your-username/VIThelpdesk.git
cd VIThelpdesk
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## Initialize Database / Seed Announcements (Optional)

If you want to populate the application with the sample announcement used in the project, run:

```bash
python backend/seed_announcement.py
```

> *This step is optional and only required if you want the default announcement to appear in the chatbot.*

---

## Start the Backend Server

```bash
uvicorn backend.main:app --reload
```

Backend URL:

```
http://127.0.0.1:8000
```

---

## Run the Frontend

Open any of the frontend pages in your browser, for example:

```
frontend/index.html
```

or

```
frontend/chat.html
```

or

```
frontend/signup.html
```

Alternatively, launch the frontend using the **VS Code Live Server** extension.

---

# 📊 Evaluation

The chatbot was evaluated using **53 test cases** covering:

- Clear Requests
- Ambiguous Queries
- Multi-Step Conversations
- Sensitive Inputs

## Results

| Metric | Result |
|---------|---------|
| Total Test Cases | 53 |
| Intent Detection Accuracy | **73.6%** |
| Tool Selection Accuracy | **96.0%** |
| Response Quality | **100%** |

---

## Sample Evaluation Output

```text
============================================================
📊 EVALUATION RESULTS SUMMARY
============================================================
• Total Test Cases Evaluated     : 53
• Intent Detection Accuracy      : 73.6%
• Tool Selection Accuracy        : 96.0%
• Response Quality               : 100.0%
============================================================
✅ Evaluation completed successfully!
```

# ⚠️ Challenges Faced

- Designing accurate rule-based intent detection for different user phrasings.
- Organizing institutional knowledge into structured JSON for precise RAG retrieval.
- Avoiding retrieval of unrelated information during semantic search.
- Managing multi-step conversational state efficiently.
- Maintaining consistent UI behavior across different themes.

---

# 🔮 Future Improvements

- Admin Dashboard for managing FAQs and support tickets.
- Voice-based interaction.
- Multilingual support.
- Live notifications and announcements.
- Integration with college ERP/Student Portal.
- Smarter hybrid intent detection for complex conversations.

---

# 🎥 Demonstration

The project includes a **5-minute demonstration video** showcasing:

- Login & Registration
- Password Reset
- Ticket Creation
- Ticket Listing
- RAG-based FAQ Retrieval
- Theme Switching
- End-to-End Chatbot Workflow

---

# 👩‍💻 Author

**M. Sravanthi**

Department of Computer Science and Engineering

Vishnu Institute of Technology

---

# 📄 License

This project was developed for academic purposes as part of the **AI Chatbot with Intelligent Tool Selection** project.
