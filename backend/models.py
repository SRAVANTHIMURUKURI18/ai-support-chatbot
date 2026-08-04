from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    tickets = relationship("Ticket", back_populates="student", cascade="all, delete-orphan")
    chats = relationship("ChatMessage", back_populates="student", cascade="all, delete-orphan")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    category = Column(String)
    description = Column(Text)
    status = Column(String, default="Open")  # Open, Resolved

    student = relationship("Student", back_populates="tickets")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    sender = Column(String)  # 'user' or 'bot'
    message_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="chats")