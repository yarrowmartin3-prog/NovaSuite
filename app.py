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

# --- CONFIGURATION HYBRIDE NOVA ---
NOVA_API_URL = os.getenv("NOVA_API_URL", "http://localhost:1234/v1/chat/completions")
NOVA_MODEL_NAME = os.getenv("NOVA_MODEL_NAME", "llama-3.1-8b-instant")
NOVA_API_KEY = os.getenv("NOVA_API_KEY", "lm-studio")

# --- CONFIGURATION PROTONMAIL (Variables Render) ---
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.protonmail.ch")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

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
    email: str = "client@novasuite.ca"

@app.get("/")
async def root():
    return {"status": "online", "agent": "Nova Nucleus V3"}

# --- 1. CHATBOT NOVA ---
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
        
        response = requests.post(NOVA_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"🚨 ERREUR GROQ : {response.text}")
            
        response.raise_for_status()
        data = response.json()
        return {"response": data['choices'][0]['message']['content']}
    
    except Exception as e:
        print(f"DEBUG CRITIQUE : {str(e)}")
        raise HTTPException(status_code=503, detail="Le cerveau de Nova est en maintenance.")

# --- 2. AUDIT 60 SECONDES ET ENVOI PDF VIA PROTON ---
@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    try:
        # 1. Exécuter l'audit
        result = subprocess.check_output(
            ['python3', 'nova_audit_system.py', '--url', req.url, '--email', req.email],
            text=True,
            stderr=subprocess.STDOUT
        )

        # 2. Générer le PDF et envoyer le courriel via ProtonMail
        if SMTP_EMAIL and SMTP_PASSWORD:
            try:
                # Création du PDF
                pdf = FPDF()
                pdf.add_page()
                
                # Tentative d'ajout du logo NovaSuite
                try:
                    pdf.image("assets/logo-novasuite.png", x=10, y=8, w=30)
                except Exception as img_err:
                    print(f"Logo non trouvé pour le PDF : {img_err}")
                
                # En-tête du PDF
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 30, "RAPPORT D'AUDIT CYBERSÉCURITÉ - NOVA NUCLEUS", ln=True, align='C')
                
                # Nettoyage des caractères spéciaux pour le PDF
                clean_text = result.replace('🔒', '[SECURE]').replace('❌', '[ECHEC]').replace('🚀', '[!]').replace('🛡️', '[BOUCLIER]').replace('✅', '[OK]')
                clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
                
                pdf.set_font("Courier", size=10)
                pdf.multi_cell(0, 6, clean_text)
                
                # Sauvegarde temporaire du PDF sur Render
                pdf_path = "audit_novasuite.pdf"
                pdf.output(pdf_path)

                # Création du courriel
                msg = MIMEMultipart()
                msg['From'] = f"NovaSuite Technologies <{SMTP_EMAIL}>"
                msg['To'] = req.email
                msg['Subject'] = f"Action Requise : Votre Rapport d'Audit NovaSuite ({req.url})"
                
                body = f"""Bonjour,

L'Agent Nova a terminé l'audit de surface pour l'infrastructure {req.url}.

Veuillez trouver ci-joint votre rapport technique détaillé au format PDF. Ce document met en évidence les vulnérabilités détectées et votre statut de conformité à la Loi 25.

Pour corriger ces failles immédiatement et déployer notre architecture sécurisée, activez l'Intégration Standard ici :
https://buy.stripe.com/9B69AT2jg84O8d19GS2VG08

Si vous avez des questions, répondez directement à ce courriel.

Cordialement,
La Direction Technique | NovaSuite
"""
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                
                # Attachement du PDF
                with open(pdf_path, "rb") as f:
                    attach = MIMEApplication(f.read(), _subtype="pdf")
                    attach.add_header('Content-Disposition', 'attachment', filename="Rapport_Audit_NovaSuite.pdf")
                    msg.attach(attach)
                
                # Envoi via l'infrastructure ProtonMail
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)
                server.quit()
                
            except Exception as mail_err:
                print(f"🚨 ERREUR D'ENVOI COURRIEL PROTON : {mail_err}")

        # 3. Retourner le résultat à l'écran du site
        return {"status": "success", "report": result}
        
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Analyse interrompue : {e.output}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
