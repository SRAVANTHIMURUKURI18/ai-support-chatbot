from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Student, Ticket, ChatMessage, TicketComment
from chatbot import process_chat_message

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class PasswordResetRequest(BaseModel):
    email: str
    old_password: str
    new_password: str

class TicketUpdate(BaseModel):
    status: str

class CommentCreate(BaseModel):
    sender: str
    message: str

@app.post("/api/register")
def register(req: RegisterRequest):
    db: Session = SessionLocal()
    clean_email = req.email.lower().strip()
    
    existing = db.query(Student).filter(Student.email == clean_email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_student = Student(
        name=req.name.strip(),
        email=clean_email,
        password="VITB@123"
    )
    db.add(new_student)
    db.commit()
    db.close()
    return {"success": True, "message": "Registration successful. Default password is VITB@123"}

@app.post("/api/login")
def login(req: LoginRequest):
    db: Session = SessionLocal()
    student = db.query(Student).filter(Student.email == req.email.lower().strip()).first()
    db.close()
    if student and student.password == req.password:
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/chat")
def chat(req: ChatRequest):
    db: Session = SessionLocal()
    clean_email = req.session_id.lower().strip()
    student = db.query(Student).filter(Student.email == clean_email).first()

    if student:
        db.add(ChatMessage(student_id=student.id, sender="user", message_text=req.message))
        db.commit()

    bot_reply = process_chat_message(req.message, req.session_id)

    if student:
        db.add(ChatMessage(student_id=student.id, sender="bot", message_text=bot_reply))
        db.commit()

    db.close()
    return {"response": bot_reply}

@app.get("/api/chat/history/{email}")
def get_chat_history(email: str):
    db: Session = SessionLocal()
    student = db.query(Student).filter(Student.email == email.lower().strip()).first()
    if not student:
        db.close()
        return []
    history = db.query(ChatMessage).filter(ChatMessage.student_id == student.id).order_by(ChatMessage.timestamp.asc()).all()
    result = [{"sender": h.sender, "message": h.message_text} for h in history]
    db.close()
    return result

@app.get("/api/profile/{email}")
def get_profile(email: str):
    db: Session = SessionLocal()
    student = db.query(Student).filter(Student.email == email.lower().strip()).first()
    if not student:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")
    
    tickets = db.query(Ticket).filter(Ticket.student_id == student.id).all()
    active_count = sum(1 for t in tickets if t.status in ["Open", "Active"])
    resolved_count = sum(1 for t in tickets if t.status in ["Resolved", "Closed"])

    data = {
        "name": student.name,
        "email": student.email,
        "branch_year": "CSE - 4TH YEAR",
        "roll_number": student.email.split('@')[0].upper(),
        "active_tickets": active_count,
        "resolved_tickets": resolved_count
    }
    db.close()
    return data

@app.get("/api/tickets/{email}")
def get_student_tickets(email: str):
    db: Session = SessionLocal()
    student = db.query(Student).filter(Student.email == email.lower().strip()).first()
    if not student:
        db.close()
        return []
    
    tickets = db.query(Ticket).filter(Ticket.student_id == student.id).all()
    result = [{
        "id": t.id,
        "category": t.category,
        "description": t.description,
        "status": t.status
    } for t in tickets]
    db.close()
    return result

@app.patch("/api/tickets/{ticket_id}")
def update_ticket_status(ticket_id: int, update: TicketUpdate):
    db: Session = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        db.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = update.status
    db.commit()
    db.close()
    return {"success": True, "message": f"Ticket marked as {update.status}"}

@app.get("/api/tickets/{ticket_id}/comments")
def get_ticket_comments(ticket_id: int):
    db: Session = SessionLocal()
    try:
        comments = db.query(TicketComment).filter(TicketComment.ticket_id == ticket_id).all()
        return [{"id": c.id, "sender": c.sender, "message": c.message, "timestamp": str(c.timestamp)} for c in comments]
    finally:
        db.close()

@app.post("/api/tickets/{ticket_id}/comments")
def add_ticket_comment(ticket_id: int, payload: CommentCreate):
    db: Session = SessionLocal()
    try:
        new_comment = TicketComment(
            ticket_id=ticket_id,
            sender=payload.sender,
            message=payload.message
        )
        db.add(new_comment)
        db.commit()
        return {"success": True, "message": "Comment added successfully"}
    finally:
        db.close()

@app.post("/api/reset-password")
def reset_password(req: PasswordResetRequest):
    db: Session = SessionLocal()
    student = db.query(Student).filter(Student.email == req.email.lower().strip()).first()
    if not student or student.password != req.old_password:
        db.close()
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    student.password = req.new_password
    db.commit()
    db.close()
    return {"success": True, "message": "Password updated successfully"}