const API_BASE = "http://localhost:8000/api/v1";

document.addEventListener("DOMContentLoaded", () => {
    loadSubjects();

    const subjectForm = document.getElementById("subjectForm");
    subjectForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const status = document.getElementById("subjectStatus");
        status.textContent = "Saving...";
        status.style.color = "inherit";
        try {
            const res = await fetch(`${API_BASE}/subjects/`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    code: document.getElementById("subCode").value,
                    name: document.getElementById("subName").value,
                    branch_name: document.getElementById("branchName").value,
                    branch_code: document.getElementById("branchCode").value,
                    sem_year: document.getElementById("semYear").value,
                    exam_title: document.getElementById("examTitle").value,
                    exam_year: document.getElementById("examYear").value
                })
            });
            if(res.ok) {
                status.style.color = "#4ade80";
                status.textContent = "Subject Saved Successfully!";
                subjectForm.reset();
                loadSubjects();
            } else {
                throw new Error("Failed to save branch");
            }
        } catch(err) {
            status.style.color = "#f87171";
            status.textContent = "Error: " + err.message;
        }
    });

    const genForm = document.getElementById("genForm");
    const aiProvider = document.getElementById("aiProvider");
    const aiModel = document.getElementById("aiModel");

    // Fetch models on load
    fetchModels(aiProvider.value);

    aiProvider.addEventListener("change", () => {
        fetchModels(aiProvider.value);
    });

    genForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const subjectId = document.getElementById("subjectId").value;
        const pdfFile = document.getElementById("syllabusPdf").files[0];
        const numQs = document.getElementById("numQs").value;
        const qType = document.getElementById("qType").value;
        const provider = aiProvider.value;
        const modelName = aiModel.value;

        const status = document.getElementById("genStatus");
        const btn = genForm.querySelector(".btn");
        const loader = btn.querySelector(".loader");
        const btnText = btn.querySelector(".btn-text");

        if(!subjectId) {
            alert("Subject required!");
            return;
        }

        const formData = new FormData();
        formData.append("file", pdfFile);
        formData.append("provider", provider);
        formData.append("model_name", modelName);
        formData.append("q_type", qType);
        
        btnText.textContent = `Processing with ${modelName}...`;
        loader.classList.remove("hidden");
        status.textContent = "";
        
        try {
            const res = await fetch(`${API_BASE}/generate/from-pdf/?subject_id=${subjectId}&num_questions=${numQs}`, {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if(res.ok) {
                status.style.color = "#4ade80";
                status.textContent = "Success: " + data.message;
            } else {
                throw new Error(data.detail || "Server Error");
            }
        } catch(err) {
            status.style.color = "#f87171";
            status.textContent = "Error: " + err.message;
        } finally {
            btnText.textContent = "Generate Questions (AI)";
            loader.classList.add("hidden");
        }
    });

    const paperForm = document.getElementById("paperForm");
    paperForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const subjectId = document.getElementById("paperSubjectId").value;
        const status = document.getElementById("paperStatus");
        
        status.textContent = "Compiling Paper...";
        try {
            const numQs = document.getElementById("paperNumQs").value;
            const res = await fetch(`${API_BASE}/papers/generate/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    subject_id: parseInt(subjectId),
                    total_marks: 100,
                    sections_config: [{"num_q": parseInt(numQs)}]
                })
            });
            const data = await res.json();
            if(res.ok) {
                status.textContent = "Paper successfully created!";
                status.style.color = "#4ade80";
                
                // Show links
                const downloadLinks = document.getElementById("downloadLinks");
                downloadLinks.classList.remove("hidden");
                
                const baseURL = API_BASE.replace("/api/v1", "");
                document.getElementById("docxLink").href = `${baseURL}/${data.paper_file}`;
                document.getElementById("ansLink").href = `${baseURL}/${data.ans_key_file}`;

            } else {
                throw new Error(data.detail);
            }
        } catch(err) {
            status.style.color = "#f87171";
            status.textContent = "Error: " + err.message;
        }
    });
});

async function loadSubjects() {
    try {
        const res = await fetch(`${API_BASE}/subjects/`);
        if (!res.ok) {
            // Seed a mock subject for testing if db is empty or failed
            seedMockSubject();
            return;
        }
        const subjects = await res.json();
        
        const sel1 = document.getElementById("subjectId");
        const sel2 = document.getElementById("paperSubjectId");
        
        sel1.innerHTML = '<option value="">Select a subject</option>';
        sel2.innerHTML = '<option value="">Select a subject</option>';
        
        if(subjects.length === 0) {
            seedMockSubject();
        } else {
            subjects.forEach(sub => {
                const opt = `<option value="${sub.id}">${sub.code} - ${sub.name}</option>`;
                sel1.innerHTML += opt;
                sel2.innerHTML += opt;
            });
        }
    } catch(err) {
        console.error("Could not load subjects, ensure backend is running.");
    }
}

async function seedMockSubject() {
    try {
        await fetch(`${API_BASE}/subjects/`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                code: "CS101",
                name: "Computer Science",
                branch_name: "B.Tech",
                branch_code: "CSE",
                sem_year: "1st Year",
                exam_title: "Mid Term",
                exam_year: "2026"
            })
        });
        // reload safely
        const res = await fetch(`${API_BASE}/subjects/`);
        const subjects = await res.json();
        const sel1 = document.getElementById("subjectId");
        const sel2 = document.getElementById("paperSubjectId");
        sel1.innerHTML = '<option value="">Select a subject</option>';
        sel2.innerHTML = '<option value="">Select a subject</option>';
        subjects.forEach(sub => {
            const opt = `<option value="${sub.id}">${sub.code} - ${sub.name}</option>`;
            sel1.innerHTML += opt;
            sel2.innerHTML += opt;
        });
    } catch(e) {}
}

async function fetchModels(provider) {
    const aiModel = document.getElementById("aiModel");
    aiModel.innerHTML = '<option value="">Loading models...</option>';
    try {
        const res = await fetch(`${API_BASE}/llm/models/?provider=${provider}`);
        const models = await res.json();
        aiModel.innerHTML = "";
        models.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m.id;
            opt.textContent = m.name;
            aiModel.appendChild(opt);
        });
        
        // Auto-select first model if available
        if (models.length > 0 && !aiModel.value) {
            aiModel.value = models[0].id;
        }
    } catch (err) {
        aiModel.innerHTML = '<option value="">Error loading models</option>';
        console.error("Failed to fetch models:", err);
    }
}
