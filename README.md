# AI_Qgen - AI-Based Bilingual Question Paper Generator

AI_Qgen is an AI-powered application designed to generate bilingual (English and Hindi) question papers automatically from a given book or syllabus. It features a robust Python/FastAPI backend, PostgreSQL database with SQLAlchemy models, and a modern, aesthetically pleasing frontend interface.

## System Requirements
- Python 3.10+
- PostgreSQL Server (Local)
- Groq API Key (for LLM Question Generation)

---

## 🚀 Setup Instructions

### 1. Database Setup
Ensure you have PostgreSQL installed and running locally.
1. Open pgAdmin or connect via `psql`.
2. Create a new empty database named `ai_qgen`.

### 2. Environment Variables (.env)
The project includes a `.env` template file at the root. Update the variables using your credentials:
```env
# Add your Groq API Key here
GROQ_API_KEY=your_actual_groq_api_key_here

# PostgreSQL connection string Format: postgresql://user:password@host:port/database_name
# Change "your_password" to your actual postgres password
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_qgen
```

### 3. Virtual Environment & Dependencies
We recommend using the localized virtual environment.
1. Open PowerShell and navigate to the project directory.
2. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
3. *(Optional)* If you moved to a new machine, install dependencies using:
   ```powershell
   pip install -r requirements.txt
   ```

### 4. Run Database Migrations
Before starting the backend server, apply the database migrations using Alembic to create the necessary tables.
```powershell
alembic revision --autogenerate -m "Initial Schema"
alembic upgrade head
```

---

## 🛠️ Running the Application

### Starting the Backend Server (FastAPI)
With the virtual environment active, run the Uvicorn server:
```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- The backend API will be available at: `http://localhost:8000`
- API Documentation (Swagger UI): `http://localhost:8000/docs`

### Starting the Frontend UI
The frontend relies on standard HTML/JS/CSS. To prevent CORS or local file issues, you can serve the frontend folder using Python's built-in HTTP server:
1. Open a **new terminal tab/window**.
2. Navigate to the project root and start an HTTP server targeting the `frontend` folder:
   ```powershell
   python -m http.server 3000 --directory frontend
   ```
3. Open your browser and navigate to: `http://localhost:3000`

---

## Features
- **Syllabus Parsing:** Upload syllabus PDFs to extract exact context.
- **Bilingual Generation:** Guaranteed formatted LLM generation of English and Hindi questions.
- **Anti-Repetition Engine:** Safely tracks questions to minimize usage duplication (max 6 usage limit).
- **DOCX / PDF Export:** Export dynamically formatted examination question papers securely.
