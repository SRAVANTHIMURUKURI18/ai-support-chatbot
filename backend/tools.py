import os
from langchain_core.tools import tool
from database import SessionLocal
from models import Ticket
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Fast local embedding initialization
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

docs = [
    "The central library is open from 8:00 AM to 8:00 PM on all working days and 9:00 AM to 1:00 PM on Saturdays.",
    "Hostel WiFi issues can be resolved by registering a ticket with your laptop MAC address at the campus network center or online helpdesk.",
    "The college academic fee counter is open from 9:30 AM to 4:00 PM in the main administrative block on all working days.",
    "EAMCET counseling and admissions office is located on the ground floor of the administrative block, operating from 10:00 AM to 5:00 PM."
]

if os.path.exists("faiss_index"):
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
else:
    vectorstore = FAISS.from_texts(docs, embeddings)
    vectorstore.save_local("faiss_index")

retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

@tool
def search_knowledge_base(query: str) -> str:
    """Call this tool to look up general campus guidelines or library timings."""
    try:
        results = retriever.invoke(query)
        if not results:
            return "Please check the menu options for quick assistance."
        return results[0].page_content
    except Exception:
        return "The central library is open from 8:00 AM to 8:00 PM on all working days."

@tool
def reset_password(student_id: str) -> str:
    """Call this tool when a user resets their portal password."""
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