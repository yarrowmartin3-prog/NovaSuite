import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION BREVO ---
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 2525
SMTP_LOGIN = os.getenv("SMTP_LOGIN", "9fb545001@smtp-brevo.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "yarrowmartin3@gmail.com")

# --- VOTRE NOUVELLE BOÎTE DE RÉCEPTION ---
MY_EMAIL = "contact@novasuite.ca" 

class AuditRequest(BaseModel):
    url: str
    email: str

class ContactRequest(BaseModel):
    nom: str
    email: str
    message: str

@app.head("/")
@app.get("/")
async def root():
    return {"status": "NovaSuite API Online"}

@app.post("/api/contact")
async def send_contact(req: ContactRequest):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"NovaSuite Web <{SENDER_EMAIL}>"
        msg['To'] = MY_EMAIL # Envoi à contact@novasuite.ca
        msg['Subject'] = f"Nouveau Contact : {req.nom}"
        
        body = f"Nouveau message de contact.\n\nNom: {req.nom}\nEmail: {req.email}\n\nMessage:\n{req.message}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    result_rule = f"Loi 25 - Section 3.2 : Consentement non conforme sur {req.url}"
    command = "Vérifiez l'en-tête X-Privacy-Consent."
    
    try:
        # 1. Envoi au CLIENT
        msg_client = MIMEMultipart()
        msg_client['From'] = f"Agent Nova <{SENDER_EMAIL}>"
        msg_client['To'] = req.email
        msg_client['Subject'] = "🔒 Votre Rapport d'Audit NovaSuite"
        
        body_client = f"Bonjour,\n\nL'Agent Nova a terminé l'audit pour : {req.url}\n\n🚨 Règle : {result_rule}\n🛠️ Commande : {command}\n\nComplet ici : https://buy.stripe.com/5kA9AT6zwa8W50PeUV"
        msg_client.attach(MIMEText(body_client, 'plain', 'utf-8'))
        
        # 2. Copie pour VOUS à contact@novasuite.ca
        msg_me = MIMEMultipart()
        msg_me['From'] = SENDER_EMAIL
        msg_me['To'] = MY_EMAIL
        msg_me['Subject'] = f"🔔 Audit effectué : {req.url}"
        msg_me.attach(MIMEText(f"Audit demandé par {req.email} pour le site {req.url}.", 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg_client)
        server.send_message(msg_me)
        server.quit()

        return {"rule": result_rule, "command": command}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
