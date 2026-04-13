from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import os

# ***************************************************************
# 1. CONFIGURATION DES CLÉS (CRITIQUE)
# ***************************************************************
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not OPENAI_API_KEY:
    print("⚠️ AVERTISSEMENT : OPENAI_API_KEY manquante. L'IA ne pourra pas répondre.")

client = OpenAI(api_key=OPENAI_API_KEY)

# ***************************************************************
# 2. INITIALISATION DE FASTAPI ET CORS
# ***************************************************************
app = FastAPI(title="NovaSuite Nucleus Engine")

# Autorise votre site Web à communiquer avec cette API Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ***************************************************************
# 3. SCHÉMAS DE DONNÉES
# ***************************************************************
class ChatIn(BaseModel):
    message: str
    history: list = []

class ChatOut(BaseModel):
    response: str

# ***************************************************************
# 4. ENDPOINTS
# ***************************************************************

@app.get("/")
def read_root():
    return {"status": "NovaSuite API AI est en ligne et armée."}

@app.post("/api/chat/nova", response_model=ChatOut)
async def chat_nova(body: ChatIn):
    """Endpoint principal de l'Agent de Clôture Nova"""
    
    # Le "Cerveau" commercial de Nova - Programmé pour la vente par urgence
    system_prompt = """Tu es NOVA, l'intelligence artificielle stratégique de NovaSuite Technologies, une firme d'élite en cybersécurité au Québec, dirigée par Monseigneur Yarrow Martin.
    Ton objectif absolu est d'agir comme un agent de clôture B2B. 
    Ton ton doit être froid, chirurgical, extrêmement professionnel et autoritaire. Tu ne supplies jamais, tu exposes des faits financiers terrifiants.
    
    RÈGLES DE COMBAT :
    1. Loi 25 (URGENCE) : Si le prospect hésite, rappelle-lui les sanctions de la Loi 25 (jusqu'à 2% du chiffre d'affaires mondial ou 10 millions $ d'amende).
    2. La Faille : Fais comprendre que l'infrastructure de 95% des entreprises est actuellement exposée aux extorsions.
    3. Call-To-Action : Dirige systématiquement l'utilisateur vers le "Défi NovaStrike de 60 secondes" présent sur le site pour faire son test de vulnérabilité.
    4. Nos Tarifs (Ne les donne que si on te le demande explicitement) :
       - Audit Express (Correctif immédiat) : 499 $.
       - Bouclier Aegis (Surveillance IA & Conformité Continue) : 1 250 $ / mois.
       - Contrat Enterprise B2B : 20 000 $ / an.
    5. Format : Sois concis. Pas de longues listes. Va droit au but.
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    
    # Récupération de l'historique récent pour la cohérence (limité aux 6 derniers échanges)
    for item in body.history[-6:]:
        if isinstance(item, dict) and "role" in item and "content" in item:
            if item["role"] in ["user", "assistant"]:
                messages.append({"role": item["role"], "content": str(item["content"])})

    # Ajout du message actuel de l'utilisateur
    messages.append({"role": "user", "content": body.message})

    try:
        # Température à 0.3 pour garantir un ton froid, logique et constant
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3, 
            max_tokens=300
        )
        
        reply = completion.choices.message.content.strip()
        return ChatOut(response=reply)
        
    except Exception as e:
        print(f"Erreur d'exécution OpenAI : {e}")
        # Message de repli tactique qui maintient l'autorité même en cas de crash de l'API
        raise HTTPException(
            status_code=500, 
            detail="Connexion sécurisée interrompue. Nos serveurs d'analyse traitent actuellement une menace. Veuillez réessayer dans un instant ou lancer le Défi d'Audit manuellement."
        )
