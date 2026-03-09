from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import subprocess
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fpdf import FPDF

# --- CONFIGURATION NOVA NUCLEUS ---
NOVA_API_URL = os.getenv("NOVA_API_URL", "https://api.groq.com/openai/v1/chat/completions")
NOVA_MODEL_NAME = os.getenv("NOVA_MODEL_NAME", "llama-3.1-8b-instant")
NOVA_API_KEY = os.getenv("NOVA_API_KEY", "")

# --- CONFIGURATION PROTONMAIL (Port 465 pour SSL Direct) ---
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.protonmail.ch")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))

app = FastAPI()

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
    email: str

@app.get("/")
async def root():
    return {"status": "online", "agent": "Nova Nucleus V3", "security": "Proton-Shielded"}

# --- 1. AGENT DE CONVERSATION NOVA ---
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
                {"role": "system", "content": "Vous êtes Nova, l'IA de NovaSuite. Soyez bref, expert et rassurant sur la Loi 25."},
                {"role": "user", "content": request.message}
            ]
        }
        response = requests.post(NOVA_API_URL, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        return {"response": response.json()['choices'][0]['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. DÉFI D'AUDIT : SCAN + GÉNÉRATION PDF + ENVOI PROTON ---
@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    try:
        # Exécution du script de diagnostic local
        result = subprocess.check_output(
            ['python3', 'nova_audit_system.py', '--url', req.url],
            text=True, stderr=subprocess.STDOUT
        )

        if SMTP_EMAIL and SMTP_PASSWORD:
            try:
                # Création du PDF Professionnel
                pdf = FPDF()
                pdf.add_page()
                
                # Gestion sécurisée du Logo
                logo_path = "assets/logo-novasuite.png"
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=10, y=8, w=33)
                else:
                    print(f"⚠️ LOGO MANQUANT: {logo_path}")

                pdf.set_font("Arial", 'B', 16)
                pdf.ln(20)
                pdf.cell(0, 10, "RAPPORT D'AUDIT DE CONFORMITÉ - NOVASUITE", ln=True, align='C')
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 10, f"Cible : {req.url} | Inspecté par Nova Nucleus", ln=True, align='C')
                pdf.ln(10)

                # Nettoyage du texte pour compatibilité PDF (latin-1)
                clean_text = result.replace('🔒', '[SECURE]').replace('❌', '[FAIL]').replace('🚀', '[!]').replace('✅', '[OK]')
                clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')

                pdf.set_font("Courier", size=9)
                pdf.multi_cell(0, 5, clean_text)
                
                pdf_filename = "Rapport_NovaSuite_Audit.pdf"
                pdf.output(pdf_filename)

                # Construction du Courriel
                msg = MIMEMultipart()
                msg['From'] = f"NovaSuite Technologies <{SMTP_EMAIL}>"
                msg['To'] = req.email
                msg['Subject'] = f"🔒 Action Requise : Votre Rapport d'Audit NovaSuite ({req.url})"

                body = f"""Bonjour,

L'Agent Nova a terminé l'audit de surface pour l'infrastructure {req.url}.

Vous trouverez ci-joint votre rapport technique détaillé (PDF). Ce document identifie les failles potentielles et votre statut de conformité préliminaire à la Loi 25.

Pour corriger ces vulnérabilités et déployer notre architecture de protection :
https://buy.stripe.com/9B69AT2jg84O8d19GS2VG08

Cordialement,
Monseigneur Yarrow | NovaSuite Technologies
"""
                msg.attach(MIMEText(body, 'plain'))

                with open(pdf_filename, "rb") as f:
                    attach = MIMEApplication(f.read(), _subtype="pdf")
                    attach.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
                    msg.attach(attach)

                # Connexion SSL Directe (Port 465) pour éviter les Timeouts
                print(f"Connexion à {SMTP_SERVER}:{SMTP_PORT}...")
                server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)
                server.quit()
                print("✅ Rapport envoyé avec succès via Proton.")

            except Exception as mail_err:
                print(f"🚨 ERREUR CRITIQUE ENVOI : {mail_err}")

        return {"status": "success", "report": result}

    except Exception as e:
        return {"status": "error", "message": str(e)}
