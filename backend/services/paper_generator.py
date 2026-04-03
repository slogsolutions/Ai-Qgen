from sqlalchemy.orm import Session
from .. import models
import random

def build_paper(db: Session, subject_id: int, total_questions: int, q_type: str = "MCQ"):
    """
    Selects valid questions for a paper based on anti-repetition logic.
    """
    # 1. Fetch questions with usage < 6
    query = db.query(models.Question).filter(
        models.Question.subject_id == subject_id,
        models.Question.usage_count < 6
    )
    
    if q_type != "Mixed":
        query = query.filter(models.Question.q_type == q_type)
        
    available_qs = query.all()

    # 2. If not enough < 6, pull from any (random)
    if len(available_qs) < total_questions:
        shortfall = total_questions - len(available_qs)
        query_extra = db.query(models.Question).filter(
            models.Question.subject_id == subject_id,
            models.Question.usage_count >= 6
        )
        if q_type != "Mixed":
            query_extra = query_extra.filter(models.Question.q_type == q_type)
            
        extra_qs = query_extra.limit(shortfall).all()
        selected = available_qs + list(extra_qs)
    else:
        selected = random.sample(available_qs, total_questions)

    # 3. Update usage counters
    for q in selected:
        q.usage_count += 1
    db.commit()

    return selected
