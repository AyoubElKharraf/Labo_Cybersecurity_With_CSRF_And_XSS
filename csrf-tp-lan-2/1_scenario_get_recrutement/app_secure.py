# ==============================================================================
# SCÉNARIO 1 : VERSION SÉCURISÉE (INTERDICTION DU GET + TOKEN CSRF EN POST)
# ==============================================================================
import socket
import secrets
from flask import Flask, request, session, redirect, url_for, render_template_string, abort

app = Flask(__name__)
app.secret_key = "secret_scenario_1_get_secure"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True

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
    <title>Espace Bancaire - Sécurisé contre CSRF GET</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 30px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        h1 { color: #27ae60; font-size: 22px; }
        .badge-ip { background: #e8f5e9; color: #2e7d32; padding: 6px 10px; border-radius: 4px; font-size: 13px; font-weight: bold; }
        .solde-box { background: #e8f5e9; border-left: 4px solid #2e7d32; padding: 15px; margin: 15px 0; border-radius: 4px; }
        .solde-val { font-size: 24px; font-weight: bold; color: #1b5e20; }
        .token-box { background: #e3f2fd; padding: 10px; border-radius: 4px; font-size: 12px; margin: 10px 0; border-left: 3px solid #1976d2; }
    </style>
</head>
<body>
    <div class="card">
        <span class="badge-ip">🛡️ Serveur LAN Sécurisé : http://{{ local_ip }}:5000</span>
        {% block body %}{% endblock %}
    </div>
</body>
</html>
"""

TEMPLATE_DASHBOARD = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Mon Compte Bancaire (Sécurisé)</h1>
    <div class="solde-box">
        Solde disponible : <span class="solde-val">{{ solde }} €</span>
    </div>
    
    <div class="token-box">
        <strong>Jeton anti-CSRF :</strong> <code>{{ csrf_token }}</code>
    </div>

    <h3>Effectuer un Virement Légitime (Méthode POST obligatoire) :</h3>
    <form method="POST" action="/virement">
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
        <label>Bénéficiaire :</label><br>
        <input type="text" name="dest" placeholder="Nom ou IBAN" required style="width:100%; padding:8px; margin:5px 0;"><br>
        <label>Montant (€) :</label><br>
        <input type="number" name="montant" placeholder="Montant" required style="width:100%; padding:8px; margin:5px 0;"><br><br>
        <input type="submit" value="Confirmer le virement" style="background:#27ae60; color:white; border:none; padding:10px 15px; border-radius:4px; cursor:pointer;">
    </form>
    <br>
    <a href="/logout" style="color:#666; font-size:13px;">Se déconnecter</a>
""")

@app.route('/')
def index():
    if "user" not in session:
        return redirect('/login')
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return render_template_string(TEMPLATE_DASHBOARD, solde=DB["solde"], csrf_token=session["csrf_token"], local_ip=LOCAL_IP)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == DB["username"] and request.form.get('password') == DB["password"]:
            session["user"] = DB["username"]
            session["csrf_token"] = secrets.token_hex(32)
            return redirect('/')
    return """
    <h2>Connexion Sécurisée</h2>
    <form method="POST">
        Utilisateur: <input type="text" name="username" value="Ayoub"><br><br>
        Mot de passe: <input type="password" name="password" value="password123"><br><br>
        <input type="submit" value="Connexion">
    </form>
    """

@app.route('/virement', methods=['POST'])
def virement():
    if "user" not in session:
        return "Non authentifié", 401

    token = request.form.get('csrf_token')
    if not token or not secrets.compare_digest(token, session.get('csrf_token', '')):
        abort(403, description="Échec de validation CSRF : Jeton invalide ou action en GET interdite !")

    dest = request.form.get('dest', 'Inconnu')
    montant = float(request.form.get('montant', 0))
    if montant > 0 and DB["solde"] >= montant:
        DB["solde"] -= montant
        DB["transactions"].append({"dest": dest, "montant": montant})
        return redirect('/')
    return "Fonds insuffisants", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print(f"[✓] Scénario 1 Sécurisé actif sur http://{LOCAL_IP}:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
