from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import subprocess
import os

# --- Configuration ---
NOVA_API_URL = os.getenv("NOVA_API_URL", "http://localhost:1234/v1/chat/completions")
NOVA_MODEL_NAME = os.getenv("NOVA_MODEL_NAME", "your-local-model")

app = FastAPI()

# --- Configuration de Sécurité (CORS) ---
# On autorise tout pour l'instant pour s'assurer que ça marche du premier coup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schémas de données ---
class ChatRequest(BaseModel):
    message: str

class AuditRequest(BaseModel):
    url: str
    email: str = "client@novasuite.ca"

# --- 1. Route de Chat (Nova) ---
@app.post("/api/chat/nova")
async def chat_with_nova(request: ChatRequest):
    try:
        payload = {
            "model": NOVA_MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Vous êtes Nova, un assistant de cybersécurité pour NovaSuite. Vous fournissez des conseils techniques concis et professionnels."},
                {"role": "user", "content": request.message}
            ],
            "temperature": 0.7 
        }
        response = requests.post(NOVA_API_URL, json=payload, timeout=60)
        response.raise_for_status() 
        response_data = response.json()
        nova_response = response_data['choices'][0]['message']['content']
        return {"response": nova_response}
    except Exception as e:
        print(f"Erreur: {e}")
        raise HTTPException(status_code=503, detail="Le service Nova est actuellement indisponible.")

# --- 2. Route d'Audit 60 Secondes (Loi 25) ---
@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    try:
        # Exécution de Nucleus V3 en arrière-plan
        result = subprocess.check_output(
            ['python3', 'nova_audit_system.py', '--url', req.url, '--email', req.email],
            text=True
        )
        return {"status": "success", "report": result}
    except subprocess.CalledProcessError as e:
        # Si le script Python plante, on capture l'erreur pour ne pas faire planter l'API
        return {"status": "error", "message": f"Erreur du script d'audit : {e.output}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
