# ==============================================================================
# SCÉNARIO 1 : MÉTHODE GET - APPLICATION BANCAIRE VULNÉRABLE
# ==============================================================================
import socket
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "secret_scenario_1_get"
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False

DB = {
    "username": "Ayoub",
    "password": "password123",
    "solde": 1500.0,
    "transactions": []
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
    <title>Espace Bancaire - Démo CSRF en GET</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 30px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        h1 { color: #c0392b; font-size: 22px; }
        .badge-ip { background: #e3f2fd; color: #1565c0; padding: 6px 10px; border-radius: 4px; font-size: 13px; font-weight: bold; }
        .solde-box { background: #e8f5e9; border-left: 4px solid #2e7d32; padding: 15px; margin: 15px 0; border-radius: 4px; }
        .solde-val { font-size: 24px; font-weight: bold; color: #1b5e20; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f5f5f5; }
        .btn-logout { color: #666; text-decoration: none; font-size: 13px; }
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

TEMPLATE_LOGIN = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Connexion Banque en Ligne (Scénario 1 : GET)</h1>
    {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
    <p>Identifiants de test : <strong>Ayoub</strong> / <strong>password123</strong></p>
    <form method="POST" action="/login">
        <label>Nom d'utilisateur :</label><br>
        <input type="text" name="username" value="Ayoub" required style="width:100%; padding:8px; margin:5px 0;"><br>
        <label>Mot de passe :</label><br>
        <input type="password" name="password" value="password123" required style="width:100%; padding:8px; margin:5px 0;"><br><br>
        <input type="submit" value="Accéder à mes comptes" style="background:#c0392b; color:white; border:none; padding:10px 15px; border-radius:4px; cursor:pointer;">
    </form>
""")

TEMPLATE_DASHBOARD = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Mon Compte Bancaire (Ayoub)</h1>
    <div class="solde-box">
        Solde disponible : <span class="solde-val">{{ solde }} €</span>
    </div>
    
    <h3>Dernières Transactions :</h3>
    <table>
        <tr><th>Bénéficiaire</th><th>Montant</th><th>Type</th></tr>
        {% for t in transactions %}
        <tr style="color:red;"><td>{{ t.dest }}</td><td>- {{ t.montant }} €</td><td>Virement</td></tr>
        {% else %}
        <tr><td colspan="3">Aucun virement récent.</td></tr>
        {% endfor %}
    </table>
    <br>
    <a href="/logout" class="btn-logout">Se déconnecter</a>
""")

@app.route('/')
def index():
    if "user" in session:
        return render_template_string(TEMPLATE_DASHBOARD, solde=DB["solde"], transactions=DB["transactions"], local_ip=LOCAL_IP)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == DB["username"] and request.form.get('password') == DB["password"]:
            session["user"] = DB["username"]
            return redirect(url_for('index'))
        error = "Identifiants invalides."
    return render_template_string(TEMPLATE_LOGIN, error=error, local_ip=LOCAL_IP)

@app.route('/virement', methods=['GET'])
def virement():
    if "user" not in session:
        return "Erreur : Non authentifié !", 401
    
    dest = request.args.get('dest', 'Inconnu')
    try:
        montant = float(request.args.get('montant', 0))
    except ValueError:
        return "Montant invalide", 400

    if montant > 0 and DB["solde"] >= montant:
        DB["solde"] -= montant
        DB["transactions"].append({"dest": dest, "montant": montant})
        return f"<h2>Virement de {montant} € vers {dest} effectué avec succès !</h2><p>Nouveau solde : {DB['solde']} €</p><a href='/'>Retour</a>"
    return "Fonds insuffisants", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print(f"[✓] Scénario 1 (GET) actif sur http://{LOCAL_IP}:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
