# ==============================================================================
# SCÉNARIO 2 : VERSION SÉCURISÉE (TOKEN CSRF + SAMESITE STRICT)
# ==============================================================================
import socket
import secrets
from flask import Flask, request, session, redirect, url_for, render_template_string, abort

app = Flask(__name__)
app.secret_key = "secret_scenario_2_post_secure"
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_HTTPONLY'] = True

DB = {
    "username": "Ayoub",
    "password": "password123",
    "adresse_livraison": "12 Rue de la Paix, 75000 Paris",
    "abonnements": "Abonnement Fibre Pro 1 Gb/s (79,90 € / mois)"
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
    <title>Espace Client - Sécurisé CSRF</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 30px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        h1 { color: #16a34a; font-size: 22px; }
        .badge-ip { background: #dcfce7; color: #15803d; padding: 6px 10px; border-radius: 4px; font-size: 13px; font-weight: bold; }
        .box { background: #f1f5f9; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #16a34a; }
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
    <h1>Espace Client Télécom (Sécurisé)</h1>
    <div class="box">
        <p><strong>Formule active :</strong> {{ abo }}</p>
        <p><strong>Adresse de facturation / livraison :</strong><br><span style="color:#15803d; font-size:16px; font-weight:bold;">{{ adresse }}</span></p>
    </div>
    
    <h3>Modifier mon adresse (Protégé par Jeton) :</h3>
    <form method="POST" action="/update-adresse">
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
        <input type="text" name="nouvelle_adresse" placeholder="Nouvelle adresse..." required style="width:100%; padding:8px;"><br><br>
        <input type="submit" value="Enregistrer l'adresse" style="background:#16a34a; color:white; border:none; padding:10px 15px; border-radius:4px; cursor:pointer;">
    </form>
    <br><a href="/logout" style="color:#666; font-size:13px;">Se déconnecter</a>
""")

@app.route('/')
def index():
    if "user" not in session:
        return redirect('/login')
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return render_template_string(TEMPLATE_DASHBOARD, abo=DB["abonnements"], adresse=DB["adresse_livraison"], csrf_token=session["csrf_token"], local_ip=LOCAL_IP)

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
        <input type="submit" value="Se connecter">
    </form>
    """

@app.route('/update-adresse', methods=['POST'])
def update_adresse():
    if "user" not in session:
        return "Non autorisé", 401

    token = request.form.get('csrf_token')
    if not token or not secrets.compare_digest(token, session.get('csrf_token', '')):
        abort(403, description="Échec de validation CSRF : Jeton invalide ou absent !")

    nouvelle = request.form.get('nouvelle_adresse')
    if nouvelle:
        DB["adresse_livraison"] = nouvelle
        return redirect('/')
    return "Adresse vide", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print(f"[✓] Scénario 2 Sécurisé actif sur http://{LOCAL_IP}:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
