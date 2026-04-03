import httpx
import json

prompt = """
You are an expert...
Return exactly in this JSON format:
{
    "questions": [
        {
            "question_en": "test",
            "question_hi": "test",
            "answer_en": "test",
            "answer_hi": "test"
        }
    ]
}

Context for generation:
Generate 2 MCQ questions about Python.
"""

print("Sending request to Ollama...")
try:
    response = httpx.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2:latest",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json"
        },
        timeout=180.0
    )
    response.raise_for_status()
    content = response.json()["message"]["content"]
    with open("output.json", "w", encoding="utf-8") as f:
        f.write(content)
    print("Raw content saved to output.json")
    
    data = json.loads(content)
    print("Parsed data keys: ", data.keys())
    if "questions" in data and isinstance(data["questions"], list):
        print(f"Found {len(data['questions'])} questions")
    else:
        print("No questions found or not a list")
except Exception as e:
    print(f"Error: {e}")
