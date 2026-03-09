from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import subprocess
import os

# --- CONFIGURATION HYBRIDE ---
NOVA_API_URL = os.getenv("NOVA_API_URL", "http://localhost:1234/v1/chat/completions")
NOVA_MODEL_NAME = os.getenv("NOVA_MODEL_NAME", "llama3-8b-8192")
NOVA_API_KEY = os.getenv("NOVA_API_KEY", "lm-studio")

app = FastAPI()

# --- SÉCURITÉ (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class AuditRequest(BaseModel):
    url: str
    email: str = "client@novasuite.ca"

@app.get("/")
async def root():
    return {"status": "online", "agent": "Nova Nucleus V3"}

# --- 1. CHATBOT NOVA (Diagnostic Intégré) ---
@app.post("/api/chat/nova")
async def chat_with_nova(request: ChatRequest):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {NOVA_API_KEY}"
        }
        payload = {
            "model": NOVA_MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Vous êtes Nova, l'IA de cybersécurité de NovaSuite. Soyez bref, pro et expert en Loi 25."},
                {"role": "user", "content": request.message}
            ],
            "temperature": 0.7
        }
        
        # Envoi de la requête
        response = requests.post(NOVA_API_URL, json=payload, headers=headers, timeout=30)
        
        # --- BLOC DE DIAGNOSTIC RENDER ---
        if response.status_code != 200:
            print(f"🚨 ERREUR GROQ DÉTECTÉE (Code {response.status_code})")
            print(f"💬 RÉPONSE BRUTE DU SERVEUR : {response.text}")
        # ----------------------------------

        response.raise_for_status()
        
        data = response.json()
        return {"response": data['choices'][0]['message']['content']}
    
    except Exception as e:
        print(f"DEBUG CRITIQUE : {str(e)}")
        raise HTTPException(status_code=503, detail="Le cerveau de Nova est en maintenance. Réessayez dans 30 secondes.")

# --- 2. AUDIT 60 SECONDES ---
@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    try:
        result = subprocess.check_output(
            ['python3', 'nova_audit_system.py', '--url', req.url, '--email', req.email],
            text=True,
            stderr=subprocess.STDOUT
        )
        return {"status": "success", "report": result}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Analyse interrompue : {e.output}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
