import os
from langchain_core.tools import tool
from database import SessionLocal
from models import Ticket
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"local_files_only": True}
)

docs = [
    "Campus Facilities: Digital library, normal library, park, tea leaf, cyber zone, playground, gym, squash court, tennis court, cricket ground, snacks zone, and gods of temple for divine vibes.",
    "Food Outlets: Canoe and cuisine for biryanis, tea leaf for tea, juice corner for juices, temple square and central square for snacks, fresh choice bakery for birthday cakes, and milk parlour for milk related products.",
    "Faculty Contacts for Permissions & Placements: For placement related queries contact TPO. For permission related queries contact HOD or assigned mentor.",
    "Placement Statistics (Batch-wise): 2021: 750+ placements, 2022: 850+ placements, 2023: 920+ placements, 2024: 980+ placements, 2025: 1050+ placements, 2026: 1000+ placements so far.",
    "College Websites & Portals: vishnu.ac.in is for attendance, student profile, and fee-related details. vishnu.ac.results is for checking semester results. vishnulearning.com is for all semester subjects related stuff like PDFs, quizzes, and assignments. vedic.dev is for complete detailed student profile required for placements, mock interviews, tech guidance, and administrator communications.",
    "Smart Campus App (Hostel Students): Used for hostel attendance, food orders, and applying for local or general outings.",
    "Available Student Clubs: E-Cell, GDG (Google Developer Groups), Student Success Center, Dance Club, Music Club, Drone Club, and Robotics Club.",
    "Hostel Outing Procedure: 1. Open Smart Campus App, select outing (general or local), and fill in date, reason, in-time, out-time, and companion details. 2. Automated WhatsApp message/call goes to parent for approval/decline. 3. Department HOD approves/declines based on rules. 4. Head Warden gives final approval. 5. Scan QR code at security gate to check out (triggers parent notification with date/time). Same scan procedure applies when re-entering campus."
]

if os.path.exists("faiss_index"):
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
else:
    vectorstore = FAISS.from_texts(docs, embeddings)
    vectorstore.save_local("faiss_index")

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

@tool
def search_knowledge_base(query: str) -> str:
    """Call this tool to look up campus guidelines, facilities, food, websites, or club info."""
    try:
        results = retriever.invoke(query)
        if not results:
            return "Please check the menu options for quick assistance."
        return "\n\n".join([doc.page_content for doc in results])
    except Exception:
        return "Please type **'menu'** to view available options."

@tool
def reset_password(student_id: str) -> str:
    """Call this tool when a user explicitly requests to reset their portal password."""
    return f"Password reset created for {student_id}."

@tool
def create_ticket(student_id: str, category: str, description: str) -> str:
    """Call this tool to report an issue or create a support ticket."""
    db = SessionLocal()
    clean_id = student_id.lower().strip()
    new_ticket = Ticket(student_id=clean_id, category=category, description=description, status="Pending")
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    db.close()
    return f"ACTION COMPLETED: Ticket created successfully. Ticket ID: #{new_ticket.id} | Category: {category} | Status: Pending."

@tool
def show_tickets(student_id: str) -> str:
    """Call this tool when a user wants to view their support tickets."""
    db = SessionLocal()
    clean_id = student_id.lower().strip()
    tickets = db.query(Ticket).filter(Ticket.student_id == clean_id).all()
    db.close()
    if not tickets:
        return f"You currently have no open support tickets registered under {clean_id}."
    response = f"Here are your registered support tickets:\n"
    for t in tickets:
        response += f"• Ticket #{t.id} [{t.category}]: {t.description} (Status: {t.status})\n"
    return response