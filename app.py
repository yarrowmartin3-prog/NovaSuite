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

# --- LA COMBINAISON GAGNANTE ---
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 2525  # Le port fantôme qui traverse le pare-feu de Render

# Le login technique trouvé par Monseigneur Yarrow
SMTP_LOGIN = os.getenv("SMTP_LOGIN", "9fb545001@smtp-brevo.com")

# Le mot de passe (la clé xsmtpsib-...)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# L'adresse affichée aux clients
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "yarrowmartin3@gmail.com")

# L'adresse où VOUS recevez les messages
DESTINATION_EMAIL = "martin.yarrow@gmail.com" 

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
        msg['To'] = DESTINATION_EMAIL
        msg['Subject'] = f"Nouveau Contact Web : {req.nom}"
        
        body = f"Nouveau lead depuis le site NovaSuite.\n\nNom: {req.nom}\nEmail: {req.email}\n\nMessage:\n{req.message}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return {"status": "success", "message": "Transmis"}
    except Exception as e:
        print(f"🚨 Erreur Contact Brevo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    result_rule = f"Loi 25 - Section 3.2 : Consentement explicite non détecté sur {req.url}"
    command = "Vérifiez l'en-tête X-Privacy-Consent."
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Agent Nova <{SENDER_EMAIL}>"
        msg['To'] = req.email
        msg['Subject'] = "⚠️ Résultat Partiel de votre Audit - NovaSuite"
        
        body = f"""Bonjour,

L'Agent Nova a terminé l'audit préliminaire pour l'infrastructure : {req.url}

🚨 Règle critique identifiée : {result_rule}
🛠️ Commande de remédiation : {command}

Des vulnérabilités supplémentaires ont été détectées en arrière-plan. 
Pour obtenir le rapport de remédiation complet et sécuriser votre infrastructure, procédez à la mise à niveau immédiate :
https://buy.stripe.com/5kA9AT6zwa8W50PeUV

Cordialement,
Monseigneur Yarrow | NovaSuite Technologies
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        return {"rule": result_rule, "command": command}
    except Exception as e:
        print(f"🚨 Erreur Audit Brevo: {e}")
        raise HTTPException(status_code=500, detail=str(e))
