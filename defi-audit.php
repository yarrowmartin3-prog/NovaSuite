<?php
// defi-audit.php - Système de Diagnostic Automatisé NovaSuite
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $target_url = filter_input(INPUT_POST, 'target_url', FILTER_SANITIZE_URL);
    $client_email = filter_input(INPUT_POST, 'client_email', FILTER_SANITIZE_EMAIL);

    if (filter_var($target_url, FILTER_VALIDATE_URL) && filter_var($client_email, FILTER_VALIDATE_EMAIL)) {
        $data = array("url" => $target_url, "email" => $client_email);
        $payload = json_encode($data);
        $render_api_url = 'https://novasuite-1.onrender.com/api/audit';

        $ch = curl_init($render_api_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
        curl_setopt($ch, CURLOPT_TIMEOUT, 45); 
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        echo "<!DOCTYPE html><html lang='fr'><head><meta charset='UTF-8'><title>Rapport - NovaSuite</title>";
        echo "<script src='https://cdn.tailwindcss.com'></script>";
        echo "<style>body{background-color:#050505;color:white;font-family:sans-serif;} .glass{background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.1);}</style></head>";
        echo "<body class='p-8 flex items-center justify-center min-h-screen'>";

        if ($http_code == 200 && $response) {
            $result = json_decode($response, true);
            if ($result && $result['status'] === 'success') {
                echo "<div class='glass p-8 max-w-3xl w-full rounded-xl border-l-4 border-green-500 shadow-2xl'>";
                echo "<h2 class='text-2xl font-bold text-white mb-6 flex items-center gap-3'>🔒 Rapport d'Audit Loi 25 - POC</h2>";
                echo "<pre class='text-green-400 font-mono text-sm overflow-x-auto p-4 bg-black rounded whitespace-pre-wrap leading-relaxed border border-green-900/30'>" . htmlspecialchars($result['report']) . "</pre>";
                echo "<div class='mt-8 text-center'>";
                // LIEN STRIPE 499 $ ICI
                echo "<a href='https://buy.stripe.com/00w8wPaPMfxgcthaKW2VG05' class='inline-block w-full bg-green-500 text-black font-black py-4 rounded text-lg hover:bg-green-400 transition transform hover:scale-105'>DÉBLOQUER L'AUDIT COMPLET (499 $)</a>";
                echo "</div></div>";
            } else {
                echo "<div class='glass p-6 text-red-500 max-w-md mx-auto text-center'>Erreur : " . htmlspecialchars($result['message']) . "</div>";
            }
        } else {
            echo "<div class='glass p-6 text-red-500 max-w-md mx-auto text-center'>Le serveur Nova analyse les données. Code : $http_code</div>";
        }
        echo "</body></html>";
        exit;
    }
}
?>

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Défi Audit 60s - NovaSuite Technologies</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #050505; color: white; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        .glass { background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4 relative pt-10">
    <div class="absolute inset-0 z-0" style="background-image: radial-gradient(circle at center, rgba(34,197,94,0.08) 0%, transparent 70%);"></div>

    <div class="glass p-10 rounded-2xl text-center w-full max-w-md z-10 relative border-t-2 border-green-500 shadow-2xl">
        <h2 class="text-3xl font-black text-white mb-2 tracking-tight">DÉFI AUDIT <span class="text-green-400 drop-shadow-[0_0_10px_rgba(74,222,128,0.5)]">60S</span></h2>
        <p class="text-gray-400 text-sm mb-8 italic">Vérifiez votre conformité Loi 25 en un clic.</p>
        
        <form method="POST" action="">
            <div class="text-left mb-4">
                <label class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em]">URL de l'entreprise</label>
                <input type="url" name="target_url" placeholder="https://clinique-exemple.ca" required class="w-full p-4 mt-1 bg-black border border-gray-800 rounded-lg text-white focus:border-green-500 outline-none transition duration-300">
            </div>
            <div class="text-left mb-8">
                <label class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em]">Votre Courriel Professionnel</label>
                <input type="email" name="client_email" placeholder="directeur@domaine.com" required class="w-full p-4 mt-1 bg-black border border-gray-800 rounded-lg text-white focus:border-green-500 outline-none transition duration-300">
            </div>
            <button type="submit" class="w-full bg-green-500 text-black font-black py-4 rounded-lg hover:bg-green-400 transition-all duration-300 shadow-[0_0_20px_rgba(34,197,94,0.3)]">
                LANCER LE DIAGNOSTIC GRATUIT
            </button>
        </form>
        <div style="margin-top: 20px;"><a href="/" style="color:#888; text-decoration: none; font-size: 12px;">Retour à l'accueil</a></div>
    </div>

    <div style="position:fixed;top:0;left:0;width:100%;background:#dc2626;color:white;padding:8px;text-align:center;font-size:10px;font-weight:bold;z-index:99999;letter-spacing:0.1em;box-shadow:0 0 15px rgba(220,38,38,0.5);">ALERTE : CONFORMITÉ LOI 25 REQUISE. <a href="defi-audit.php" style="text-decoration:underline;color:white;">LANCEZ LE POC GRATUIT</a></div>
    <div id="chat-container" style="position:fixed;bottom:20px;right:20px;width:320px;z-index:99999;font-family:monospace;"><div id="chat-window" style="display:none;flex-direction:column;background:#0a0a0a;border:1px solid #00ff41;border-bottom:none;border-radius:12px 12px 0 0;height:384px;box-shadow:0 20px 25px -5px rgba(0,0,0,0.5);"><div style="background:#16a34a;color:black;padding:12px;font-weight:bold;border-radius:12px 12px 0 0;display:flex;justify-content:space-between;"><span>🤖 AGENT NOVA v1.0</span><button type="button" onclick="toggleChat()" style="color:black;font-weight:900;background:none;border:none;cursor:pointer;">X</button></div><div id="chat-messages" style="flex:1;padding:16px;overflow-y:auto;font-size:11px;background:rgba(0,0,0,0.9);color:#22c55e;"><p>[SYS] Nova en ligne. Prêt pour l'audit.</p></div><div style="padding:8px;background:#111;display:flex;border-top:1px solid #333;"><input id="chat-input" type="text" style="flex:1;background:#000;border:1px solid #333;padding:8px;color:white;font-size:11px;outline:none;" placeholder="Entrer commande..." onkeypress="if(event.key==='Enter') sendMessage()"><button type="button" onclick="sendMessage()" style="background:#22c55e;color:black;padding:0 12px;font-weight:bold;border:none;cursor:pointer;">></button></div></div><button type="button" onclick="toggleChat()" style="width:100%;background:#000;border:1px solid #22c55e;color:#22c55e;font-weight:bold;padding:12px;border-radius:9999px;cursor:pointer;font-size:10px;letter-spacing:0.1em;margin-top:8px;">+ ASSISTANCE IA NOVA</button></div>
    <script>function toggleChat(){const w=document.getElementById('chat-window');w.style.display=w.style.display==='none'||w.style.display===''?'flex':'none';} async function sendMessage(){const i=document.getElementById('chat-input');const m=document.getElementById('chat-messages');if(!i.value.trim())return;m.innerHTML+=`<p style="color:white;margin-top:8px;">> ${i.value.trim()}</p>`;const msg=i.value.trim();i.value='';m.scrollTop=m.scrollHeight;try{const r=await fetch('https://novasuite-1.onrender.com/api/chat/nova',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});const d=await r.json();m.innerHTML+=`<p style="color:#4ade80;margin-top:8px;">NOVA: ${d.response||d.detail}</p>`;}catch(e){m.innerHTML+=`<p style="color:#ef4444;margin-top:8px;">[ERREUR] Connexion API Render échouée.</p>`;}m.scrollTop=m.scrollHeight;}</script>
</body>
</html>
