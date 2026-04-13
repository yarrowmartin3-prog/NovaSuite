import os
import smtplib
import socket
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# 1. INITIALISATION
app = FastAPI(title="NovaSuite Unified Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. CONFIGURATION DES CLÉS & VARIABLES
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 2525
SMTP_LOGIN = os.getenv("SMTP_LOGIN", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "yarrowmartin3@gmail.com")
STRIPE_AUDIT_LINK = "https://buy.stripe.com/00w8wPaPMfxgcthaKW2VG05"

# 3. SCHÉMAS DE DONNÉES
class AuditRequest(BaseModel):
    url: str
    email: str
    consent: bool

class ChatIn(BaseModel):
    message: str
    history: list = []

# Le correctif magique : on renvoie 'response' ET 'reply' pour satisfaire tous vos scripts JS
class ChatOut(BaseModel):
    response: str
    reply: str

@app.get("/")
def read_root():
    return {"status": "NovaSuite API (IA & Audit) est en ligne."}

# ==========================================
# MODULE 1 : L'AUDIT AUTOMATISÉ (OSINT FURTIF)
# ==========================================
@app.post("/api/audit")
async def perform_audit(req: AuditRequest):
    if not req.consent:
        raise HTTPException(status_code=400, detail="Le consentement légal est obligatoire.")
        
    clean_url = req.url.replace('https://', '').replace('http://', '').split('/')
    
    try:
        ip_address = socket.gethostbyname(clean_url)
    except:
        ip_address = "IP Masquée/Cloudflare"
    
    try:
        # Mode "Furtif" pour contourner les pare-feux anti-bots
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(f"https://{clean_url}", headers=headers, timeout=10, verify=False)
        h = r.headers
        score = 100
        fails = []
        
        if 'Strict-Transport-Security' not in h: 
            score -= 30
            fails.append("HSTS")
        if 'Content-Security-Policy' not in h: 
            score -= 40
            fails.append("CSP")
            
        rule_message = "Faille de sécurité détectée. Votre entreprise est exposée à des sanctions administratives selon la Loi 25 (jusqu'à 2% du CA)." if fails else "Infrastructure sécurisée."
        
        # Envoi de l'alerte
        if SMTP_LOGIN and SMTP_PASSWORD:
            try:
                msg = MIMEMultipart()
                msg['From'] = SENDER_EMAIL
                msg['To'] = req.email
                msg['Subject'] = f"⚠️ ALERTE LOI 25 : Rapport d'exposition pour {clean_url}"
                body = f"<html><body style='background:#050505;color:white;font-family:sans-serif;padding:20px;'><h2 style='color:#00ff41;'>VULNÉRABILITÉ DÉTECTÉE</h2><p>Absence de : {', '.join(fails)}</p><p>Déléguez la remédiation à NovaSuite : <a href='{STRIPE_AUDIT_LINK}' style='color:#00ff41;'>Activer le Bouclier</a></p></body></html>"
                msg.attach(MIMEText(body, 'html', 'utf-8'))
                
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
                server.starttls()
                server.login(SMTP_LOGIN, SMTP_PASSWORD)
                server.send_message(msg)
                server.quit()
            except Exception as e:
                print(f"Erreur SMTP: {e}")

        return {"status": "ok", "score": score, "ip": ip_address, "rule": rule_message}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pare-feu détecté ou domaine inaccessible.")

# ==========================================
# MODULE 2 : L'AGENT IA NOVA
# ==========================================
@app.post("/api/chat/nova", response_model=ChatOut)
async def chat_nova(body: ChatIn):
    if not client:
        return ChatOut(response="Système IA indisponible.", reply="Système IA indisponible.")
        
    system_prompt = """Tu es NOVA, l'IA de NovaSuite Technologies, dirigée par Monseigneur Yarrow.
    Agis comme un agent B2B froid et logique. Rappelle l'urgence de la Loi 25 et redirige vers le test de 60 secondes."""
    
    messages = [{"role": "system", "content": system_prompt}]
    for item in body.history[-6:]:
        if isinstance(item, dict) and "role" in item and "content" in item:
            messages.append({"role": item["role"], "content": str(item["content"])})
    messages.append({"role": "user", "content": body.message})

    try:
        completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.3)
        reply_text = completion.choices.message.content.strip()
        # On renvoie les DEUX clés pour que tous vos scripts fonctionnent parfaitement
        return ChatOut(response=reply_text, reply=reply_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Connexion interrompue.")
