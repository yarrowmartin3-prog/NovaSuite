<?php
// defi-audit.php
// Sécurité : Interdire l'accès direct si ce n'est pas une requête POST
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $target_url = filter_input(INPUT_POST, 'target_url', FILTER_SANITIZE_URL);
    $client_email = filter_input(INPUT_POST, 'client_email', FILTER_SANITIZE_EMAIL);

    // Validation basique
    if (filter_var($target_url, FILTER_VALIDATE_URL) && filter_var($client_email, FILTER_VALIDATE_EMAIL)) {
        
        // 1. Échapper les arguments pour éviter l'injection de commandes
        $safe_url = escapeshellarg($target_url);
        $safe_email = escapeshellarg($client_email);

        // 2. Appel au script Python de l'Agent (Chemin absolu vers votre script Freemium)
        $command = "python3 /home/yarrow/NOVA_SECURE/nova_audit_system.py --url $safe_url --email $safe_email 2>&1";
        
        // 3. Exécution
        $output = shell_exec($command);

        // 4. Affichage du résultat (Le POC)
        echo "<div class='glass p-6 text-neon font-mono text-sm'>";
        echo "<h3>[+] Rapport d'Audit Généré</h3>";
        echo "<pre>" . htmlspecialchars($output) . "</pre>";
        echo "<a href='https://buy.stripe.com/votre_lien' class='cta-final mt-4'>DÉBLOQUER L'AUDIT COMPLET (499$)</a>";
        echo "</div>";

    } else {
        echo "<p class='text-red-500'>Erreur : URL ou Email invalide.</p>";
    }
    exit;
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
<body class="flex items-center justify-center h-screen">
    <div class="glass p-10 rounded-xl text-center">
        <h2 class="text-2xl font-bold text-green-400 mb-6">Défi d'Audit 60 Secondes</h2>
        <form method="POST" action="">
            <input type="url" name="target_url" placeholder="https://votre-site.com" required class="w-full p-3 mb-4 bg-gray-900 border border-gray-700 rounded text-white">
            <input type="email" name="client_email" placeholder="votre@email.com" required class="w-full p-3 mb-6 bg-gray-900 border border-gray-700 rounded text-white">
            <button type="submit" class="w-full bg-green-500 text-black font-bold py-3 rounded hover:bg-green-400 transition">
                LANCER LE DIAGNOSTIC GRATUIT
            </button>
        </form>
    </div>
</body>
</html>
