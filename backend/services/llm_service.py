import os
from groq import Groq
import json
import httpx

client = Groq(api_key=os.getenv("GROQ_API_KEY", "default-test-key"))
USE_OLLAMA = os.getenv("USE_OLLAMA", "False").lower() in ["true", "1", "yes"]
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def _call_llm(prompt: str, provider: str = None, model: str = None) -> str:
    """Wrapper to handle Groq vs Ollama seamlessly, with optional overrides."""
    active_provider = provider or ("ollama" if USE_OLLAMA else "groq")
    active_model = model or (OLLAMA_MODEL if active_provider == "ollama" else "llama-3.1-8b-instant")

    if active_provider == "ollama":
        response = httpx.post(
            "http://localhost:11434/api/chat",
            json={
                "model": active_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "format": "json",
                "options": {
                    "num_ctx": 4096,
                    "num_predict": 2048
                }
            },
            timeout=600.0
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    else:
        response = client.chat.completions.create(
            model=active_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=6000,
        )
        return response.choices[0].message.content

def generate_questions(subject_context: str, num_questions: int, q_type: str, provider: str = None, model: str = None) -> list:
    """
    Generates structured bilingual questions using an iterative chunking approach over the full context.
    Supports dynamic provider/model selection and multiple question types.
    """
    # 1. Chunking Logic
    chunk_size = 4000
    chunks = [subject_context[i:i+chunk_size] for i in range(0, len(subject_context), chunk_size)]
    if not chunks:
        chunks = [""] # Fallback for completely empty PDF
        
    num_chunks = len(chunks)
    base_q = num_questions // num_chunks
    rem_q = num_questions % num_chunks
    
    all_qs = []
    
    for i, chunk in enumerate(chunks):
        target_q = base_q + (1 if i < rem_q else 0)
        
        if target_q == 0:
            continue
            
        prompt = f"""
You are an expert educational content creator. Based on the provided context chunk, generate {target_q} questions.
Requested Question Type: {q_type} (If 'Mixed', provide a varied selection).

### SUPPORTED TYPES:
- MCQ: Multiple Choice Question (Include 4 options: A, B, C, D)
- FIB: Fill in the Blanks (Show as sentence with '___')
- T/F: True or False Questions
- SA: Short Answer (Detailed 1-2 sentence answers)
- LA: Long Answer (Comprehensive explanations)
- CASE: Case-based/Scenario Questions (Provide a small context first)

### STRICT RULES:
1. CONTEXT-BOUND: Use ONLY the provided content. If info is missing, SKIP it.
2. NO HALLUCINATION: Every question MUST be documented in the text.
3. CONTENT FILTERING: NO meta-questions about authors, dates of publishing, etc.
4. UNIQUE & BILINGUAL: No duplicates. All questions/answers must be in EN and HI.

### JSON FORMAT:
Return ONLY a valid JSON object with a "questions" key:
{{
    "questions": [
        {{
            "q_type": "MCQ",
            "question_en": "...",
            "question_hi": "...",
            "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
            "answer_en": "...",
            "answer_hi": "..."
        }},
        {{
            "q_type": "FIB",
            "question_en": "... ___ ...",
            "question_hi": "... ___ ...",
            "options": null,
            "answer_en": "...",
            "answer_hi": "..."
        }}
    ]
}}

Context Chunk:
{chunk}
"""
        try:
            content = _call_llm(prompt, provider=provider, model=model)
            
            # Clean markdown backticks
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                data = json.loads(content)
            except json.decoder.JSONDecodeError as decode_err:
                # Salvage incomplete JSON if model token limit reached
                last_brace = content.rfind("}")
                if last_brace != -1:
                    salvaged = content[:last_brace+1] + "]}"
                    try:
                        data = json.loads(salvaged)
                    except Exception:
                        print(f"Chunk {i+1} parsing failed. Error: {decode_err}")
                        continue
                else:
                    print(f"Chunk {i+1} Decode Error: {decode_err}")
                    continue

            # Extract lists
            if "questions" in data and isinstance(data["questions"], list):
                all_qs.extend(data["questions"])
            elif isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        all_qs.extend(v)
                        break
                
        except Exception as e:
            print(f"Error processing chunk {i+1} with LLM: {str(e)}")
            continue

    if not all_qs:
        raise ValueError("Complete failure across all PDF chunks. No LLM questions generated successfully.")
        
    return all_qs
