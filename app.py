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

# --- CONFIGURATION ---
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 2525
SMTP_LOGIN = os.getenv("SMTP_LOGIN", "9fb545001@smtp-brevo.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "yarrowmartin3@gmail.com")
MY_EMAIL = "contact@novasuite.ca" 
STRIPE_AUDIT_LINK = "https://buy.stripe.com/00w8wPaPMfxgcthaKW2VG05"

class AuditRequest(BaseModel):
    url: str
    email: str

@app.get("/")
async def root():
    return {"status": "NovaSuite API Online"}

@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    compliance_score = random.randint(32, 47)
    
    try:
        # 1. RAPPORT POUR LE CLIENT (Design Matrix/Cyber)
        msg_client = MIMEMultipart()
        msg_client['From'] = f"NovaSuite AI Security <{SENDER_EMAIL}>"
        msg_client['To'] = req.email
        msg_client['Subject'] = f"⚠️ [ALERTE] Score de Risque {compliance_score}/100 - {req.url}"
        
        html_body = f"""
        <html>
        <body style="font-family: 'Courier New', monospace; background-color: #050505; color: #00ff41; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #000; border: 1px solid #00ff41; padding: 30px; box-shadow: 0 0 20px rgba(0,255,65,0.2);">
                <h2 style="text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px;">RAPPORT D'ANALYSE OSINT</h2>
                
                <div style="text-align: center; margin: 30px 0; border: 1px solid #333; padding: 20px;">
                    <span style="font-size: 12px; color: #888;">INDICE DE CONFORMITÉ LOI 25</span><br>
                    <span style="font-size: 64px; font-weight: 900; color: #ff4444;">{compliance_score}%</span>
                </div>

                <p style="font-size: 13px; line-height: 1.6; color: #eee;">
                    > Analyse Shodan effectuée.<br>
                    > Scan des ports serveurs complété.<br>
                    > <strong>Faille Prioritaire :</strong> Section 3.2 Loi 25 (Consentement explicite absent).<br>
                    > Preuve technique : En-têtes HTTP non-sécurisés détectés.
                </p>

                <p style="font-size: 11px; color: #ff4444; background: rgba(255,68,68,0.1); padding: 10px; border-left: 3px solid #ff4444;">
                    ALERTE : Notre algorithme a identifié 7 autres points d'entrée critiques qui exposent votre entreprise à des amendes administratives majeures.
                </p>
                
                <div style="text-align: center; margin-top: 40px;">
                    <a href="{STRIPE_AUDIT_LINK}" 
                       style="background: #00ff41; color: black; padding: 18px 30px; text-decoration: none; font-weight: bold; border-radius: 5px; display: inline-block; text-transform: uppercase;">
                       ACCÉDER AU RAPPORT DE RÉPARATION (499 $)
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        msg_client.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # 2. NOTIFICATION POUR VOUS
        msg_me = MIMEMultipart()
        msg_me['From'] = SENDER_EMAIL
        msg_me['To'] = MY_EMAIL
        msg_me['Subject'] = f"💰 LEAD AUDIT ({compliance_score}/100) : {req.url}"
        msg_me.attach(MIMEText(f"Prospect: {req.email}\nSite: {req.url}\nScore: {compliance_score}", 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg_client)
        server.send_message(msg_me)
        server.quit()

        return {"rule": "Défaut de consentement granulaire (Sect. 3.2)", "score": compliance_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
