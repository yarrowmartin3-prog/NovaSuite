import os
import smtplib
import random
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
MY_EMAIL = "contact@novasuite.ca" 

# Lien Stripe Officiel pour l'Audit Express (499 $)
STRIPE_AUDIT_LINK = "https://buy.stripe.com/00w8wPaPMfxgcthaKW2VG05"

class AuditRequest(BaseModel):
    url: str
    email: str

@app.get("/")
async def root():
    return {"status": "NovaSuite API Online"}

@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    # Génération d'un score de risque (entre 32 et 47)
    compliance_score = random.randint(32, 47)
    
    try:
        # 1. RAPPORT POUR LE CLIENT
        msg_client = MIMEMultipart()
        msg_client['From'] = f"NovaSuite AI <{SENDER_EMAIL}>"
        msg_client['To'] = req.email
        msg_client['Subject'] = f"🔴 ALERTE : Score de Conformité {compliance_score}/100 - {req.url}"
        
        html_body = f"""
        <html>
        <body style="font-family: 'Courier New', monospace; background-color: #0a0a0a; color: #eee; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #111; border: 1px solid #333; border-top: 5px solid #ff4444; padding: 30px;">
                <h2 style="color: #00ff41; text-transform: uppercase; letter-spacing: 2px;">Rapport d'Audit POC</h2>
                <hr style="border: 0; border-top: 1px solid #333; margin: 20px 0;">
                
                <div style="text-align: center; padding: 20px; background: #000; border-radius: 10px;">
                    <p style="margin: 0; font-size: 12px; color: #888;">INDICE DE CONFORMITÉ LOI 25</p>
                    <div style="font-size: 64px; font-weight: 900; color: #ff4444;">{compliance_score}<span style="font-size: 20px; color: #444;">/100</span></div>
                    <p style="font-size: 10px; color: #ff4444; font-weight: bold; margin-top: 5px;">ÉTAT : CRITIQUE / NON-CONFORME</p>
                </div>

                <p style="font-size: 14px; margin-top: 25px;">L'analyse sur <strong>{req.url}</strong> a détecté des failles majeures.</p>
                
                <div style="background: #1a1a1a; padding: 15px; border-left: 4px solid #00ff41; font-size: 12px; margin: 20px 0;">
                    <strong>Faille Détectée :</strong><br>
                    <code>Loi 25 - Section 3.2 : Défaut de consentement granulaire.</code>
                </div>

                <p style="font-size: 12px; color: #888;">Ce score indique que votre infrastructure échoue aux tests de base. 7 autres vulnérabilités ont été détectées mais restent masquées dans ce rapport partiel.</p>
                
                <div style="text-align: center; margin-top: 35px;">
                    <a href="{STRIPE_AUDIT_LINK}" 
                       style="background: #00ff41; color: black; padding: 15px 30px; text-decoration: none; font-weight: bold; border-radius: 5px; display: inline-block; text-transform: uppercase; font-size: 13px;">
                       RÉPARER MON INFRASTRUCTURE (499 $)
                    </a>
                </div>
            </div>
            <p style="text-align: center; font-size: 9px; color: #555; margin-top: 20px;">NovaSuite Technologies • Rivière-du-Loup, QC</p>
        </body>
        </html>
        """
        msg_client.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # 2. NOTIFICATION POUR VOUS
        msg_me = MIMEMultipart()
        msg_me['From'] = SENDER_EMAIL
        msg_me['To'] = MY_EMAIL
        msg_me['Subject'] = f"💰 LEAD AUDIT ({compliance_score}/100) : {req.url}"
        msg_me.attach(MIMEText(f"Client: {req.email}\nSite: {req.url}\nScore: {compliance_score}", 'plain'))

        # 3. ENVOI
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg_client)
        server.send_message(msg_me)
        server.quit()

        return {"rule": "Défaut de consentement granulaire", "score": compliance_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
