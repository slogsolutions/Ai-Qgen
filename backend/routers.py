from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from .database import get_db
from . import schemas, models
from .services import pdf_extractor, llm_service, paper_generator, exporter, model_fetcher
import json

router = APIRouter()

@router.post("/subjects/", response_model=schemas.SubjectResponse)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    db_subject = models.Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.get("/subjects/", response_model=list[schemas.SubjectResponse])
def get_subjects(db: Session = Depends(get_db)):
    return db.query(models.Subject).all()

@router.get("/llm/models/")
def get_llm_models(provider: str = "groq"):
    """Returns available models for the given provider."""
    if provider == "ollama":
        return model_fetcher.get_ollama_models()
    return model_fetcher.get_groq_models()

@router.post("/generate/from-pdf/")
async def generate_from_pdf(
    subject_id: int, 
    file: UploadFile = File(...), 
    num_questions: int = 10, 
    q_type: str = Form("Mixed"),
    provider: Optional[str] = Form(None),
    model_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    text = await pdf_extractor.extract_text_from_pdf(file)
    
    # Normally this would be a background task (using models.Job)
    try:
        # If ollama selected, ensure it's serving
        if provider == "ollama":
            model_fetcher.ensure_ollama_running()
            
        generated = llm_service.generate_questions(
            subject_context=text, 
            num_questions=num_questions, 
            q_type=q_type,
            provider=provider,
            model=model_name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    saved_qs = []
    for q_data in generated:
        # Extract q_type and options from model response if available
        # Default to the requested q_type if model didn't return one
        actual_q_type = q_data.get("q_type", q_type)
        options_json = json.dumps(q_data.get("options")) if q_data.get("options") else None

        new_q = models.Question(
            subject_id=subject_id,
            q_type=actual_q_type,
            question_en=q_data.get("question_en", ""),
            question_hi=q_data.get("question_hi", ""),
            answer_en=q_data.get("answer_en", ""),
            answer_hi=q_data.get("answer_hi", ""),
            options=options_json
        )
        db.add(new_q)
        saved_qs.append(new_q)
        
    db.commit()
    return {"message": f"Generated {len(saved_qs)} questions successfully."}

@router.post("/papers/generate/")
def generate_paper(request: schemas.PaperGenerationRequest, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
        
    # Extract number of questions and type from sections_config, fallback to 20/Mixed
    num_qs = request.sections_config[0].get("num_q", 20) if request.sections_config else 20
    q_type = request.sections_config[0].get("q_type", "Mixed") if request.sections_config else "Mixed"
    questions = paper_generator.build_paper(db, request.subject_id, num_qs, q_type)
    
    n = len(questions)
    a_len = max(1, int(n * 0.4))
    b_len = max(1, int(n * 0.3))
    c_len = n - a_len - b_len
    
    sections_json = {
        "section_a": [],
        "section_b": [],
        "section_c": []
    }
    
    for i, q in enumerate(questions):
        merged_q = f"{q.question_en} / {q.question_hi}"
        merged_a = f"{q.answer_en} / {q.answer_hi}"
        
        options = None
        if q.options:
            try:
                options = json.loads(q.options)
            except:
                pass
                
        item = {"q": merged_q, "options": options, "a": merged_a}
        
        if i < a_len:
            sections_json["section_a"].append(item)
        elif i < a_len + b_len:
            sections_json["section_b"].append(item)
        else:
            sections_json["section_c"].append(item)
            
    subject_info = {
        "exam_title": subject.exam_title,
        "subject_name": subject.name,
        "subject_code": subject.code,
        "branch_name": subject.branch_name,
        "branch_code": subject.branch_code,
        "sem_year": subject.sem_year,
        "total_marks": 100
    }
    
    paper_path = exporter.export_paper_docx(sections_json, subject_info, is_answer_key=False)
    ans_path = exporter.export_paper_docx(sections_json, subject_info, is_answer_key=True)
    
    # Save paper record
    paper = models.Paper(
        subject_id=subject.id,
        status="completed",
        file_url_docx=paper_path,
        ans_url_docx=ans_path
    )
    db.add(paper)
    db.commit()
    
    return {"message": "Paper generated successfully", "paper_file": paper_path, "ans_key_file": ans_path}
