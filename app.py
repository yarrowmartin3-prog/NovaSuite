import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

app = FastAPI()

# Configuration CORS pour permettre à votre site de parler à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Brevo (Assurez-vous que la clé est dans les variables d'environnement de Render)
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

class AuditRequest(BaseModel):
    url: str
    email: str

class ContactRequest(BaseModel):
    nom: str
    email: str
    message: str

@app.post("/api/audit")
async def run_audit(request: AuditRequest):
    # Logique simplifiée pour le POC (Simulation de résultat)
    result_rule = "Loi 25 - Section 3.2 : Consentement explicite non détecté sur " + request.url
    command = "Vérifiez l'en-tête X-Privacy-Consent dans vos requêtes HTTP."
    
    # Envoi du courriel via Brevo
    subject = "⚠️ Résultat Partiel de votre Audit - NovaSuite"
    html_content = f"""
    <html><body>
    <h1>NovaSuite - Rapport d'Audit 60s</h1>
    <p>Bonjour,</p>
    <p>Voici les résultats préliminaires pour le site : <strong>{request.url}</strong></p>
    <p style='color:red;'><strong>Règle citée :</strong> {result_rule}</p>
    <p><strong>Action recommandée :</strong> <code>{command}</code></p>
    <hr>
    <p>Pour obtenir le rapport complet de remédiation et corriger ces failles, procédez au paiement ici : <a href='https://buy.stripe.com/5kA9AT6zwa8W50PeUV'>Finaliser l'Audit Complet</a></p>
    </body></html>
    """
    
    sender = {"name": "NovaSuite Technologies", "email": "info@novasuite.ca"}
    to = [{"email": request.email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_instance.send_transac_email(send_smtp_email)
        return {"rule": result_rule, "command": command}
    except ApiException as e:
        raise HTTPException(status_code=500, detail="Erreur Brevo: " + str(e))

@app.post("/api/contact")
async def contact_form(request: ContactRequest):
    subject = f"Nouveau Contact : {request.nom}"
    html_content = f"<html><body><h2>Message de {request.nom}</h2><p>Email: {request.email}</p><p>Message: {request.message}</p></body></html>"
    
    # On s'envoie le message à soi-même (Yarrow)
    sender = {"name": "NovaSuite System", "email": "info@novasuite.ca"}
    to = [{"email": "martin.yarrow@gmail.com"}] # Remplacez par votre email de réception
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_instance.send_transac_email(send_smtp_email)
        return {"status": "success"}
    except ApiException as e:
        raise HTTPException(status_code=500, detail="Erreur d'envoi")

@app.get("/")
async def root():
    return {"status": "NovaSuite API Online"}
