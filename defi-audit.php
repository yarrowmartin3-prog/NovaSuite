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
        curl_setopt($ch, CURLOPT_TIMEOUT, 45); // Un peu plus de temps pour Shodan
        
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
                echo "<a href='https://buy.stripe.com/votre_lien_premium' class='inline-block w-full bg-green-500 text-black font-black py-4 rounded text-lg hover:bg-green-400 transition transform hover:scale-105'>DÉBLOQUER L'AUDIT COMPLET (499 $)</a>";
                echo "</div></div>";
            } else {
                echo "<div class='glass p-6 text-red-500 max-w-md mx-auto text-center'>Erreur : " . htmlspecialchars($result['message']) . "</div>";
            }
        } else {
            echo "<div class='glass p-6 text-red-500 max-w-md mx-auto text-center'>Le serveur Nova est surchargé. Code : $http_code</div>";
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
        .neon-text { text-shadow: 0 0 10px rgba(74, 222, 128, 0.5); }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4 relative">
    
    <div class="absolute inset-0 z-0" style="background-image: radial-gradient(circle at center, rgba(34,197,94,0.08) 0%, transparent 70%);"></div>

    <div class="glass p-10 rounded-2xl text-center w-full max-w-md z-10 relative border-t-2 border-green-500 shadow-2xl">
        <h2 class="text-3xl font-black text-white mb-2 tracking-tight">DÉFI AUDIT <span class="text-green-400 neon-text">60S</span></h2>
        <p class="text-gray-400 text-sm mb-8 italic">Vérifiez votre conformité Loi 25 en un clic.</p>
        
        <form method="POST" action="">
            <div class="text-left mb-4">
                <label class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em]">URL de l'entreprise</label>
                <input type="url" name="target_url" placeholder="https://clinique-exemple.ca" required 
                    class="w-full p-4 mt-1 bg-black border border-gray-800 rounded-lg text-white focus:border-green-500 outline-none transition duration-300">
            </div>
            <div class="text-left mb-8">
                <label class="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em]">Votre Courriel Professionnel</label>
                <input type="email" name="client_email" placeholder="directeur@domaine.com" required 
                    class="w-full p-4 mt-1 bg-black border border-gray-800 rounded-lg text-white focus:border-green-500 outline-none transition duration-300">
            </div>
            <button type="submit" class="w-full bg-green-500 text-black font-black py-4 rounded-lg hover:bg-green-400 transition-all duration-300 shadow-[0_0_20px_rgba(34,197,94,0.3)]">
                LANCER LE DIAGNOSTIC GRATUIT
            </button>
        </form>
    </div>

    <div id="chat-container" class="fixed bottom-5 right-5 w-80 z-50 font-mono">
        <div id="chat-window" class="hidden glass rounded-t-xl h-96 flex flex-col border-b-0 shadow-2xl border-green-900/50">
            <div class="bg-green-600 text-black p-3 font-bold rounded-t-xl flex justify-between items-center text-xs">
                <span>🤖 AGENT NOVA v1.0</span>
                <button onclick="toggleChat()" class="hover:text-white">✖</button>
            </div>
            <div id="chat-messages" class="flex-1 p-4 overflow-y-auto text-[11px] leading-relaxed bg-black/80">
                <p class="text-green-500">[SYS] Connexion sécurisée établie...</p>
                <p class="text-gray-400 mt-2 italic">Bonjour Monseigneur. Comment puis-je assister NovaSuite aujourd'hui ?</p>
            </div>
            <div class="p-2 bg-gray-900/50 flex border-t border-gray-800">
                <input id="chat-input" type="text" class="flex-1 bg-black border border-gray-700 p-2 text-white text-[11px] outline-none focus:border-green-500" placeholder="Entrer commande...">
                <button onclick="sendMessage()" class="bg-green-500 text-black px-3 font-bold hover:bg-green-400">></button>
            </div>
        </div>
        <button onclick="toggleChat()" class="w-full bg-black border border-green-500/50 text-green-500 font-bold py-3 rounded-full shadow-lg hover:bg-green-500 hover:text-black transition-all duration-300 text-xs tracking-widest">
            + INTERROGER NOVA
        </button>
    </div>

    <script>
    function toggleChat() {
        const win = document.getElementById('chat-window');
        win.classList.toggle('hidden');
    }

    async function sendMessage() {
        const input = document.getElementById('chat-input');
        const msgDiv = document.getElementById('chat-messages');
        if(!input.value) return;

        msgDiv.innerHTML += `<p class="text-white mt-3 border-l-2 border-gray-700 pl-2">> ${input.value}</p>`;
        const userMsg = input.value;
        input.value = '';

        try {
            const response = await fetch('https://novasuite-1.onrender.com/api/chat/nova', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: userMsg})
            });
            const data = await response.json();
            msgDiv.innerHTML += `<p class="text-green-400 mt-2"><span class="text-green-600">NOVA:</span> ${data.response || data.detail}</p>`;
        } catch (e) {
            msgDiv.innerHTML += `<p class="text-red-500 mt-2">[ERREUR] Serveur non rejoint.</p>`;
        }
        msgDiv.scrollTop = msgDiv.scrollHeight;
    }
    </script>
</body>
</html>
