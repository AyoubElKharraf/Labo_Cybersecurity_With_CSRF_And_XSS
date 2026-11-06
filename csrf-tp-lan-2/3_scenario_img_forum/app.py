# ==============================================================================
# SCÉNARIO 3 : CSRF PAR BALISE <img> (ZERO JAVASCRIPT / ZERO CLIC)
# ==============================================================================
import socket
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "secret_scenario_3_img"
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False

DB = {
    "username": "Ayoub",
    "password": "password123",
    "solde": 2000.0,
    "dons_effectues": []
}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Espace Don & Micro-Paiement - Scénario 3 (Image)</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #fdf4ff; margin: 30px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        h1 { color: #86198f; font-size: 22px; }
        .badge-ip { background: #fae8ff; color: #86198f; padding: 6px 10px; border-radius: 4px; font-size: 13px; font-weight: bold; }
        .box { background: #fdf2f8; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #db2777; }
    </style>
</head>
<body>
    <div class="card">
        <span class="badge-ip">🌐 Serveur LAN : http://{{ local_ip }}:5000</span>
        {% block body %}{% endblock %}
    </div>
</body>
</html>
"""

TEMPLATE_DASHBOARD = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Portefeuille Solidaire (Ayoub)</h1>
    <div class="box">
        Solde actuel : <strong style="font-size:22px; color:#86198f;">{{ solde }} €</strong>
    </div>

    <h3>Historique des Débits :</h3>
    <ul>
        {% for d in dons %}
        <li style="color:#b91c1c; margin-bottom:5px;">Débit instantané de <strong>{{ d.montant }} €</strong> vers <em>{{ d.beneficiaire }}</em></li>
        {% else %}
        <li>Aucun prélèvement enregistré.</li>
        {% endfor %}
    </ul>
    <br><a href="/logout" style="color:#666; font-size:13px;">Se déconnecter</a>
""")

@app.route('/')
def index():
    if "user" in session:
        return render_template_string(TEMPLATE_DASHBOARD, solde=DB["solde"], dons=DB["dons_effectues"], local_ip=LOCAL_IP)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == DB["username"] and request.form.get('password') == DB["password"]:
            session["user"] = DB["username"]
            return redirect('/')
    return """
    <h2>Connexion Portefeuille</h2>
    <form method="POST">
        Utilisateur: <input type="text" name="username" value="Ayoub"><br><br>
        Mot de passe: <input type="password" name="password" value="password123"><br><br>
        <input type="submit" value="Se connecter">
    </form>
    """

# ==============================================================================
# ROUTE VULNÉRABLE DÉCLENCHABLE PAR UNE SIMPLE BALISE <img src="...">
# ==============================================================================
@app.route('/don-rapide', methods=['GET'])
def don_rapide():
    if "user" not in session:
        return "Non authentifié", 401

    beneficiaire = request.args.get('dest', 'Association Pirate')
    try:
        montant = float(request.args.get('montant', 100))
    except ValueError:
        return "Montant invalide", 400

    if montant > 0 and DB["solde"] >= montant:
        DB["solde"] -= montant
        DB["dons_effectues"].append({"beneficiaire": beneficiaire, "montant": montant})
        return redirect('/')
    return "Fonds insuffisants", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print(f"[✓] Scénario 3 (Image) actif sur http://{LOCAL_IP}:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
