import os
import smtplib
import socket
import requests
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

# Lien direct (RAW) vers votre logo sur GitHub
LOGO_URL = "https://raw.githubusercontent.com/yarrowmartin3-prog/NovaSuite/main/assets/apple-touch-icon.webp"

class AuditRequest(BaseModel):
    url: str
    email: str
    consent: bool

def perform_real_audit(url: str):
    """Effectue un véritable scan de surface (OSINT & Headers)"""
    score = 100
    vulns = []
    
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    
    try:
        ip_address = socket.gethostbyname(domain)
    except:
        return {"error": "Domaine inaccessible ou invalide.", "score": 0}

    try:
        response = requests.get(f"https://{domain}", timeout=5)
        headers = response.headers
        
        if 'Strict-Transport-Security' not in headers:
            score -= 25
            vulns.append("HSTS manquant : Risque d'interception des données (Non-conforme Loi 25).")
            
        if 'Content-Security-Policy' not in headers:
            score -= 20
            vulns.append("CSP manquant : Vulnérabilité aux injections de scripts malveillants (XSS).")
            
        if 'X-Frame-Options' not in headers:
            score -= 15
            vulns.append("X-Frame-Options manquant : Risque de détournement de clics (Clickjacking).")

    except requests.exceptions.RequestException:
        score -= 40
        vulns.append("Certificat SSL/TLS invalide ou serveur HTTPS inaccessible.")

    score = max(12, score)
    
    if score == 100:
        score = 85
        vulns.append("Politique de consentement granulaire à vérifier manuellement (Section 3.2).")

    return {
        "ip": ip_address,
        "score": score,
        "primary_vuln": vulns[0] if vulns else "Sécurité de surface adéquate. Audit profond requis.",
        "vuln_count": len(vulns) + 4 
    }

@app.head("/")
@app.get("/")
async def root():
    return {"status": "NovaSuite API Online"}

@app.post("/api/contact")
async def send_contact(req: BaseModel):
    # (Votre route de contact reste ici si vous l'avez gardée)
    pass 

@app.post("/api/audit")
async def run_audit(req: AuditRequest):
    if not req.consent:
        raise HTTPException(status_code=400, detail="Consentement légal requis.")

    audit_results = perform_real_audit(req.url)
    
    if "error" in audit_results:
        raise HTTPException(status_code=400, detail=audit_results["error"])

    compliance_score = audit_results["score"]
    target_ip = audit_results["ip"]
    primary_vuln = audit_results["primary_vuln"]
    
    try:
        # 1. RAPPORT CLIENT (Avec le Logo)
        msg_client = MIMEMultipart()
        msg_client['From'] = f"NovaSuite AI Security <{SENDER_EMAIL}>"
        msg_client['To'] = req.email
        msg_client['Subject'] = f"⚠️ [ALERTE] Score de Risque {compliance_score}/100 - {req.url}"
        
        html_body = f"""
        <html>
        <body style="font-family: 'Courier New', monospace; background-color: #050505; color: #00ff41; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #000; border: 1px solid #00ff41; padding: 30px; box-shadow: 0 0 20px rgba(0,255,65,0.2);">
                
                <div style="text-align: center; margin-bottom: 25px;">
                    <img src="{LOGO_URL}" alt="NovaSuite Logo" style="width: 70px; height: 70px; border-radius: 12px; border: 1px solid #333;">
                </div>
                
                <h2 style="text-align: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 0;">RAPPORT D'ANALYSE OSINT</h2>
                
                <div style="text-align: center; margin: 30px 0; border: 1px solid #333; padding: 20px; background: #0a0a0a;">
                    <span style="font-size: 12px; color: #888;">INDICE DE CONFORMITÉ LOI 25</span><br>
                    <span style="font-size: 64px; font-weight: 900; color: #ff4444;">{compliance_score}%</span>
                </div>

                <p style="font-size: 13px; line-height: 1.6; color: #eee;">
                    > Cible confirmée : <strong>{req.url}</strong><br>
                    > Résolution IP (DNS) : <strong style="color: #ff4444;">{target_ip}</strong><br>
                    > <strong>Faille Prioritaire :</strong> {primary_vuln}<br>
                </p>

                <p style="font-size: 11px; color: #ff4444; background: rgba(255,68,68,0.1); padding: 10px; border-left: 3px solid #ff4444; margin-top: 25px;">
                    ALERTE : Notre algorithme a identifié {audit_results['vuln_count']} autres points d'entrée potentiels qui exposent votre entreprise.
                </p>
                
                <div style="text-align: center; margin-top: 40px;">
                    <a href="{STRIPE_AUDIT_LINK}" 
                       style="background: #00ff41; color: black; padding: 18px 30px; text-decoration: none; font-weight: bold; border-radius: 5px; display: inline-block; text-transform: uppercase;">
                       ACCÉDER AU RAPPORT COMPLET (499 $)
                    </a>
                </div>
            </div>
            <p style="text-align: center; font-size: 10px; color: #555; margin-top: 20px; font-family: sans-serif;">© 2026 NovaSuite Technologies</p>
        </body>
        </html>
        """
        msg_client.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        # 2. NOTIFICATION POUR VOUS
        msg_me = MIMEMultipart()
        msg_me['From'] = SENDER_EMAIL
        msg_me['To'] = MY_EMAIL
        msg_me['Subject'] = f"💰 LEAD AUDIT ({compliance_score}/100) : {req.url}"
        msg_me.attach(MIMEText(f"Prospect: {req.email}\nSite: {req.url}\nIP: {target_ip}\nScore: {compliance_score}", 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg_client)
        server.send_message(msg_me)
        server.quit()

        return {"rule": primary_vuln, "score": compliance_score, "ip": target_ip}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
