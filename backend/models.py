from sqlalchemy import Column, Integer, String, Text
from database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    roll_number = Column(String)
    branch_year = Column(String)
    password = Column(String)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    category = Column(String)
    description = Column(Text)
    status = Column(String, default="Pending")