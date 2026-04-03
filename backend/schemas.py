from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SubjectBase(BaseModel):
    code: str
    name: str
    branch_name: str
    branch_code: str
    sem_year: str
    exam_title: str
    exam_year: str

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    q_type: str
    question_en: str
    question_hi: str
    answer_en: str
    answer_hi: str
    options: Optional[str] = None # JSON string of options

class QuestionCreate(QuestionBase):
    subject_id: int

class QuestionResponse(QuestionBase):
    id: int
    subject_id: int
    usage_count: int
    options: Optional[str] = None
    class Config:
        from_attributes = True

class PaperGenerationRequest(BaseModel):
    subject_id: int
    total_marks: int = 100
    sections_config: list = [] # e.g. [{"name": "A", "marks_per_q": 2, "num_q": 10}]
