from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import Student, Ticket
from chatbot import process_chat_message

Base.metadata.create_all(bind=engine)

app = FastAPI(title="VIT AI Helpdesk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SignupRequest(BaseModel):
    name: str
    email: str
    roll_number: str
    branch_year: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class PasswordResetRequest(BaseModel):
    email: str
    old_password: str
    new_password: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = "vit_student_session"

@app.post("/api/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    clean_email = data.email.lower().strip()
    if not clean_email.endswith("@vishnu.edu.in"):
        raise HTTPException(status_code=400, detail="Email must end with @vishnu.edu.in")
    
    existing = db.query(Student).filter(Student.email == clean_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists with this email.")
    
    student = Student(
        name=data.name.strip(),
        email=clean_email,
        roll_number=data.roll_number.strip(),
        branch_year=data.branch_year.strip(),
        password=data.password
    )
    db.add(student)
    db.commit()
    return {"status": "success", "message": "Account created successfully."}

@app.post("/api/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    clean_email = data.email.lower().strip()
    student = db.query(Student).filter(Student.email == clean_email, Student.password == data.password).first()
    if not student:
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    return {"status": "success", "email": student.email, "name": student.name}

@app.get("/api/profile/{email}")
def get_profile(email: str, db: Session = Depends(get_db)):
    clean_email = email.lower().strip()
    student = db.query(Student).filter(Student.email == clean_email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    # Flexible lookup to match tickets registered under the user's email
    tickets = db.query(Ticket).filter(
        (Ticket.student_id == clean_email) | 
        (Ticket.student_id.contains(clean_email))
    ).all()
    
    active_count = sum(1 for t in tickets if t.status.lower() == "pending")
    resolved_count = sum(1 for t in tickets if t.status.lower() == "resolved")
    
    return {
        "name": student.name,
        "email": student.email,
        "roll_number": student.roll_number,
        "branch_year": student.branch_year,
        "active_tickets": active_count,
        "resolved_tickets": resolved_count
    }

@app.post("/api/reset-password")
def reset_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    clean_email = data.email.lower().strip()
    student = db.query(Student).filter(Student.email == clean_email).first()
    if not student or student.password != data.old_password:
        raise HTTPException(status_code=400, detail="Incorrect current password.")
    
    student.password = data.new_password
    db.commit()
    return {"status": "success", "message": "Password updated successfully."}

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        reply = process_chat_message(request.message, request.session_id)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)