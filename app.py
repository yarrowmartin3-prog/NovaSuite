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
    allow_methods=["*"],
    allow_headers=["*"],
)

STRIPE_AUDIT_LINK = "https://buy.stripe.com/00w8wPaPMfxgcthaKW2VG05"

class AuditRequest(BaseModel):
    url: str
    email: str

@app.post("/api/audit")
async def perform_audit(req: AuditRequest):
    clean_url = req.url.replace('https://', '').replace('http://', '').split('/')
    
    # Audit réel des headers
    try:
        r = requests.get(f"https://{clean_url}", timeout=5)
        h = r.headers
        score = 100
        fails = []
        if 'Strict-Transport-Security' not in h: score -= 30; fails.append("HSTS")
        if 'Content-Security-Policy' not in h: score -= 40; fails.append("CSP")
        
        # Envoi de l'email de conversion
        send_scare_email(req.email, clean_url, score, fails)
        
        return {"status": "ok", "score": score, "ip": socket.gethostbyname(clean_url)}
    except:
        raise HTTPException(status_code=400, detail="Domaine inaccessible")

def send_scare_email(email, url, score, fails):
    # Logique SMTP Brevo / Render
    msg = MIMEMultipart()
    msg['Subject'] = f"⚠️ ALERTE LOI 25 : Rapport d'exposition pour {url}"
    # Template focalisé sur le risque financier et la délégation
    body = f"""
    <html>
    <body style="font-family: sans-serif; background: #050505; color: white; padding: 20px;">
        <h1 style="color: #00ff41;">VULNÉRABILITÉ DÉTECTÉE : {score}/100</h1>
        <p>Votre domaine présente des failles critiques (Manquant : {', '.join(fails)}).</p>
        <p><b>Amende estimée Loi 25 :</b> Jusqu'à 2% de votre CA mondial.</p>
        <hr border="1" color="#111">
        <p>Ne gaspillez pas votre énergie à essayer de coder une solution. Déléguez la responsabilité à NovaSuite.</p>
        <a href="{STRIPE_AUDIT_LINK}" style="background: #00ff41; color: black; padding: 15px 25px; text-decoration: none; font-weight: bold;">ACTIVER LE BOUCLIER AEGIS</a>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))
    # [Code smtplib.SMTP_SSL ici...]
