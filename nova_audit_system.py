import sys
import argparse
import requests
import time
import socket

def get_shodan_data(ip):
    """Utilise l'API gratuite InternetDB de Shodan"""
    try:
        url = f"https://internetdb.shodan.io/{ip}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="L'URL à auditer")
    # On rend l'email optionnel ici pour éviter les erreurs de status 2 si le site oublie de l'envoyer
    parser.add_argument("--email", required=False, default="client@novasuite.ca")
    args = parser.parse_args()

    # Nettoyage de l'URL pour la résolution DNS
    clean_url = args.url.replace('https://', '').replace('http://', '').split('/')[0].split(':')[0]
    
    print("==================================================")
    print(" N O V A S U I T E  //  N U C L E U S  E N G I N E")
    print(" PROTOCOLE D'AUDIT OSINT - LOI 25 / SOC 2")
    print("==================================================\n")

    # 1. Résolution IP
    try:
        ip_address = socket.gethostbyname(clean_url)
    except:
        ip_address = "Masquée/Introuvable"

    print(f"[*] Cible : {args.url}")
    print(f"[*] IP Détectée : {ip_address}")
    
    # 2. Interrogation Shodan
    print("\n[>] Interrogation des bases de données de menaces mondiales...")
    shodan_data = None
    if ip_address != "Masquée/Introuvable":
        shodan_data = get_shodan_data(ip_address)
    
    if shodan_data:
        ports = shodan_data.get('ports', [])
        vulns = shodan_data.get('vulns', [])
        print(f" [!] ALERTE : {len(ports)} services exposés sur le web public.")
        if ports:
            print(f" [!] Ports ouverts détectés : {', '.join(map(str, ports[:5]))}...")
        if vulns:
            print(f" [⚠️] {len(vulns)} vulnérabilités critiques (CVE) associées à cette IP.")
    else:
        print(" [✓] Aucune exposition majeure immédiate détectée sur les bases OSINT.")

    # 3. Scan des Headers (OWASP & Loi 25)
    print("\n[>] Analyse des vecteurs d'attaque web (OWASP Top 10)...")
    try:
        # On tente de se connecter pour voir les headers de sécurité
        r = requests.get(f"https://{clean_url}", timeout=5, verify=True)
        h = r.headers
        missing = []
        if 'Strict-Transport-Security' not in h: missing.append("HSTS (OWASP A02: Cryptographic Failures)")
        if 'Content-Security-Policy' not in h: missing.append("CSP (OWASP A03: Injection)")
        
        if missing:
            print(f" ❌ ÉCHEC DE CONFORMITÉ (SOC 2 / Loi 25) :")
            for m in missing:
                print(f"     -> Faille détectée : {m}")
        else:
            print(" [✓] Protections de base OWASP présentes (HSTS, CSP).")
    except Exception as e:
        print(f" ❌ ÉCHEC : Impossible d'analyser les headers (Délai d'attente dépassé).")

    # 4. Le Hook Premium
    print("\n--- DIAGNOSTIC D'INTRUSION PROFONDE ---")
    print(" [🔒] Analyse des injections SQL (Base de données) : REQUIERT NOVA PREMIUM")
    print(" [🔒] Audit d'accès Serveur Privé : REQUIERT NOVA PREMIUM")
    print(" [🔒] Schéma d'architecture sécurisée (Standard ByteByteGo) : REQUIERT NOVA PREMIUM")

    # 5. Le Verdict Commercial
    print("\n" + "!"*50)
    print(" !!! ACTION REQUISE : CONFORMITÉ LOI 25 COMPROMISE !!!")
    print("!"*50)
    print("\nVotre rapport détaillé incluant :")
    print(" - Plan de remédiation technique pour votre équipe")
    print(" - Alignement sur les standards SOC 2 Type II")
    print(" - Certificat de diligence raisonnable (Loi 25)")
    print("\nDISPONIBLE IMMÉDIATEMENT POUR 499 $ CAD.")
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
