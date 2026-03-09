<?php
// defi-audit.php - Version Cloud (Connectée à Render)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $target_url = filter_input(INPUT_POST, 'target_url', FILTER_SANITIZE_URL);
    $client_email = filter_input(INPUT_POST, 'client_email', FILTER_SANITIZE_EMAIL);

    if (filter_var($target_url, FILTER_VALIDATE_URL) && filter_var($client_email, FILTER_VALIDATE_EMAIL)) {
        
        // 1. Préparer les données pour l'API Render
        $data = array("url" => $target_url, "email" => $client_email);
        $payload = json_encode($data);

        // 2. L'URL de votre cerveau sur Render (La route /api/audit qu'on a créée)
        $render_api_url = 'https://novasuite-1.onrender.com/api/audit';

        // 3. Appel cURL silencieux vers Render
        $ch = curl_init($render_api_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
        curl_setopt($ch, CURLOPT_TIMEOUT, 30); // On laisse 30 secondes pour que Shodan réponde
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        // 4. Traitement et affichage
        echo "<!DOCTYPE html><html lang='fr'><head><meta charset='UTF-8'><title>Résultat - NovaSuite</title>";
        echo "<script src='https://cdn.tailwindcss.com'></script>";
        echo "<style>body{background-color:#050505;color:white;font-family:sans-serif;} .glass{background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.1);}</style></head>";
        echo "<body class='p-8'>";

        if ($http_code == 200 && $response) {
            $result = json_decode($response, true);
            if ($result && $result['status'] === 'success') {
                // Succès de l'audit
                echo "<div class='glass p-8 max-w-3xl mx-auto rounded-xl border-l-4 border-green-500 shadow-2xl'>";
                echo "<h2 class='text-2xl font-bold text-white mb-6 flex items-center gap-3'>🔒 Rapport d'Audit Loi 25</h2>";
                echo "<pre class='text-green-400 font-mono text-sm overflow-x-auto p-4 bg-black rounded whitespace-pre-wrap leading-relaxed'>" . htmlspecialchars($result['report']) . "</pre>";
                echo "<div class='mt-8 text-center'>";
                // REMPLACEZ CE LIEN PAR VOTRE VRAI LIEN STRIPE
                echo "<a href='https://buy.stripe.com/votre_lien_premium' class='inline-block w-full bg-green-500 text-black font-black py-4 rounded text-lg hover:bg-green-400 transition transform hover:scale-105'>DÉBLOQUER L'AUDIT COMPLET (499 $)</a>";
                echo "<p class='text-gray-500 text-xs mt-4'>Paiement sécurisé par Stripe. Rapport technique complet et certificat de diligence livrés sous 24h.</p>";
                echo "</div></div>";
            } else {
                // Erreur retournée par le script Python
                echo "<div class='glass p-6 text-red-500 max-w-2xl mx-auto text-center'>";
                echo "Erreur du système d'audit : " . htmlspecialchars($result['message'] ?? 'Erreur inconnue');
                echo "</div>";
            }
        } else {
            // Erreur de connexion avec Render
            echo "<div class='glass p-6 text-red-500 max-w-2xl mx-auto text-center'>";
            echo "Erreur de communication avec le serveur d'analyse sécurisé (Code $http_code). Veuillez réessayer.";
            echo "</div>";
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
    <title>Défi Audit 60s - NovaSuite</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #050505; color: white; font-family: sans-serif; }
        .glass { background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4 relative">
    <div class="absolute inset-0 z-0" style="background-image: radial-gradient(circle at center, rgba(0,255,65,0.05) 0%, transparent 70%);"></div>
    <div class="glass p-10 rounded-2xl text-center w-full max-w-md z-10 relative border-t-2 border-green-500 shadow-[0_0_30px_rgba(0,255,65,0.1)]">
        <h2 class="text-3xl font-black text-white mb-2">Défi d'Audit <span class="text-green-400">60s</span></h2>
        <p class="text-gray-400 text-sm mb-8">Testez instantanément votre exposition à la Loi 25.</p>
        <form method="POST" action="">
            <div class="text-left mb-4">
                <label class="text-xs text-gray-500 font-bold uppercase tracking-wider">URL Cible</label>
                <input type="url" name="target_url" placeholder="https://votre-entreprise.com" required class="w-full p-4 mt-1 bg-[#0a0f18] border border-gray-700 rounded-lg text-white outline-none focus:border-green-500 transition">
            </div>
            <div class="text-left mb-8">
                <label class="text-xs text-gray-500 font-bold uppercase tracking-wider">Courriel de réception</label>
                <input type="email" name="client_email" placeholder="pdg@entreprise.com" required class="w-full p-4 mt-1 bg-[#0a0f18] border border-gray-700 rounded-lg text-white outline-none focus:border-green-500 transition">
            </div>
            <button type="submit" class="w-full bg-green-500 text-black font-black py-4 rounded-lg hover:bg-green-400 transition hover:shadow-[0_0_20px_rgba(0,255,65,0.4)] relative overflow-hidden group">
                <span class="relative z-10">LANCER LE DIAGNOSTIC GRATUIT</span>
                <div class="absolute inset-0 h-full w-full bg-white/20 scale-x-0 group-hover:scale-x-100 transition-transform origin-left"></div>
            </button>
        </form>
    </div>
</body>
</html>
