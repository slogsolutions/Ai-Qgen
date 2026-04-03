from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True)
    name = Column(String)
    branch_name = Column(String)
    branch_code = Column(String)
    sem_year = Column(String)
    exam_title = Column(String)
    exam_year = Column(String)
    
    questions = relationship("Question", back_populates="subject", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="subject", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    q_type = Column(String) # MCQ, FIB, SA, LA, CASE
    question_en = Column(Text)
    question_hi = Column(Text)
    answer_en = Column(Text)
    answer_hi = Column(Text)
    options = Column(Text, nullable=True) # JSON stored options
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", back_populates="questions")

class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    status = Column(String) # generating, completed, failed
    file_url_docx = Column(String, nullable=True)
    file_url_pdf = Column(String, nullable=True)
    ans_url_docx = Column(String, nullable=True)
    ans_url_pdf = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", back_populates="papers")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String) # extraction, generation
    status = Column(String) # processing, completed, failed
    details = Column(Text, nullable=True) # JSON dump of metadata or errors
    created_at = Column(DateTime(timezone=True), server_default=func.now())
