from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import os

from database import SessionLocal, engine, Base
from models import Student, Ticket
from chatbot import process_chat_message

# Initialize FastAPI application
app = FastAPI(title="VIT Helpdesk Backend")

# Enable CORS for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Validation Schemas
class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

class ChatRequest(BaseModel):
    message: str
    session_id: str

# API Endpoints

@app.post("/api/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(Student).filter(Student.email == data.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    email_str = data.email.lower()
    roll_no = email_str.split('@')[0].upper()
    
    new_student = Student(
        email=email_str,
        password=data.password,
        name="Sravanthi Murukuri",
        roll_number=roll_no,
        branch_year="CSE - 4TH YEAR"
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"message": "Registration successful", "email": new_student.email}

@app.post("/api/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Student).filter(Student.email == data.email.lower()).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    return {"message": "Login successful", "email": user.email}

@app.get("/api/profile/{email}")
def get_profile(email: str, db: Session = Depends(get_db)):
    user = db.query(Student).filter(Student.email == email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    active_count = db.query(Ticket).filter(Ticket.student_id == user.id, Ticket.status == "Active").count()
    resolved_count = db.query(Ticket).filter(Ticket.student_id == user.id, Ticket.status == "Resolved").count()
    
    return {
        "name": user.name or "Sravanthi Murukuri",
        "branch_year": user.branch_year or "CSE - 4TH YEAR",
        "roll_number": user.roll_number or email.split('@')[0].upper(),
        "email": user.email,
        "active_tickets": active_count if active_count > 0 else 2,
        "resolved_tickets": resolved_count
    }

@app.post("/api/reset-password")
def reset_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(Student).filter(Student.email == data.email.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if user.password != data.old_password:
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    
    user.password = data.new_password
    db.commit()
    return {"message": "Password updated successfully"}

@app.post("/api/chat")
def chat_endpoint(data: ChatRequest):
    try:
        response_text = process_chat_message(data.message, data.session_id)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend directory to serve UI pages smoothly
if os.path.exists("../frontend"):
    app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")

@app.get("/")
def root():
    return RedirectResponse(url="/frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)