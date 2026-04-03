import os
import httpx
import subprocess
import time
from groq import Groq

# Reuse the client from llm_service if possible, or create a simple one here
client = Groq(api_key=os.getenv("GROQ_API_KEY", "default-test-key"))

def ensure_ollama_running():
    """Checks if Ollama is running, and tries to start it if not."""
    try:
        # Simple heartbeat check
        httpx.get("http://localhost:11434/api/tags", timeout=1.0)
        return True
    except (httpx.ConnectError, httpx.TimeoutException):
        print("Ollama not responding. Attempting to start 'ollama serve'...")
        try:
            # Start ollama serve in a new process group on Windows
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Give it a few seconds to warm up
            max_retries = 5
            for i in range(max_retries):
                time.sleep(2)
                try:
                    httpx.get("http://localhost:11434/api/tags", timeout=1.0)
                    print("Ollama successfully started.")
                    return True
                except:
                    print(f"Waiting for Ollama to initialize (retry {i+1}/{max_retries})...")
            return False
        except Exception as e:
            print(f"Failed to start Ollama automatically: {e}")
            return False

def get_ollama_models():
    """Fetches list of models from local Ollama instance."""
    ensure_ollama_running()
    try:
        response = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        models = []
        for m in data.get("models", []):
            models.append({"id": m["name"], "name": m["name"]})
        return models
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return []

def get_groq_models():
    """Fetches list of models from Groq API."""
    try:
        # Manual list of common Groq models as a fallback if API is unreachable or restricted
        default_models = [
            {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant"},
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B Versatile"},
            {"id": "llama-guard-3-8b", "name": "Llama Guard 3 8B"},
            {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B"},
            {"id": "gemma2-9b-it", "name": "Gemma 2 9B"}
        ]
        
        # Try to fetch dynamically
        try:
            models_resp = client.models.list()
            dynamic_models = []
            for m in models_resp.data:
                # Filter for text models
                if "llama" in m.id or "gemma" in m.id or "mixtral" in m.id:
                    dynamic_models.append({"id": m.id, "name": m.id})
            return dynamic_models if dynamic_models else default_models
        except:
            return default_models
            
    except Exception as e:
        print(f"Error fetching Groq models: {e}")
        return []
