# ==============================================================================
# TP CSRF MULTI-MACHINES (LAN / WI-FI) - DÉFENSE PAR SAMESITE=STRICT
# ==============================================================================

import socket
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "super_cle_secrete_pedagogique_lan"

# Configuration SameSite=Strict & HttpOnly
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False

DB = {
    "username": "Ayoub",
    "password": "password123",
    "email": "ayoub.legitime@gmail.com"
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

HTML_BASE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Banque LAN - Protégé par SameSite</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; margin: 40px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 550px; margin: auto; }
        h2 { color: #2e7d32; }
        .net-badge { background: #e8eaf6; color: #283593; padding: 6px 10px; border-radius: 4px; font-size: 13px; margin-bottom: 15px; display: inline-block; }
        input[type="text"], input[type="password"], input[type="email"] { width: 100%; padding: 10px; margin: 8px 0; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
        input[type="submit"] { background-color: #2e7d32; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold; }
        input[type="submit"]:hover { background-color: #1b5e20; }
        .alert { padding: 10px; background-color: #f2dede; color: #a94442; border-radius: 4px; margin-bottom: 15px; }
        .success { padding: 10px; background-color: #dff0d8; color: #3c763d; border-radius: 4px; margin-bottom: 15px; }
        .badge { background: #eee; padding: 3px 6px; border-radius: 3px; font-family: monospace; }
        .cookie-info { font-size: 11px; color: #1b5e20; background: #e8f5e9; padding: 8px; border-radius: 4px; border-left: 3px solid #2e7d32; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="net-badge">🌐 Serveur LAN Victime : <strong>http://{{ local_ip }}:5000</strong></div>
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

TEMPLATE_LOGIN = HTML_BASE.replace("{% block content %}{% endblock %}", """
    <h2>Connexion Client (SameSite=Strict - LAN)</h2>
    {% if error %}
        <div class="alert">{{ error }}</div>
    {% endif %}
    <p>Identifiants de test : <span class="badge">Ayoub</span> / <span class="badge">password123</span></p>
    <form method="POST" action="/login">
        <label>Nom d'utilisateur :</label>
        <input type="text" name="username" required>
        <label>Mot de passe :</label>
        <input type="password" name="password" required>
        <input type="submit" value="Se connecter">
    </form>
""")

TEMPLATE_PROFIL = HTML_BASE.replace("{% block content %}{% endblock %}", """
    <h2>Espace Client (SameSite=Strict)</h2>
    {% if msg %}
        <div class="success">{{ msg }}</div>
    {% endif %}
    <p>Bienvenue <strong>{{ session['user'] }}</strong> !</p>
    <p>Email actuel enregistré : <span class="badge">{{ email }}</span></p>
    
    <div class="cookie-info">
        <strong>Attribut de sécurité actif sur le Cookie :</strong><br>
        <code>Set-Cookie: session=...; SameSite=Strict; HttpOnly; Path=/</code>
    </div>

    <hr style="margin: 20px 0; border: 0; border-top: 1px solid #eee;">
    <h3>Modifier mon adresse email :</h3>
    <form method="POST" action="/update-email">
        <label>Nouvel Email :</label>
        <input type="email" name="email" placeholder="nouveau@domaine.com" required>
        <input type="submit" value="Mettre à jour l'email">
    </form>
    
    <p style="margin-top: 25px;"><a href="/logout" style="color: #666;">Se déconnecter</a></p>
""")

@app.route('/')
def index():
    if "user" in session:
        return redirect(url_for('profil'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == DB["username"] and password == DB["password"]:
            session["user"] = username
            return redirect(url_for('profil'))
        else:
            error = "Identifiants invalides."
    return render_template_string(TEMPLATE_LOGIN, error=error, local_ip=LOCAL_IP)

@app.route('/profil')
def profil():
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template_string(TEMPLATE_PROFIL, email=DB["email"], local_ip=LOCAL_IP)

@app.route('/update-email', methods=['POST'])
def update_email():
    if "user" not in session:
        return "Échec de sécurité : Cookie de session non transmis par le navigateur (Non autorisé).", 401

    new_email = request.form.get('email')
    if new_email:
        DB["email"] = new_email
        return render_template_string(TEMPLATE_PROFIL, email=DB["email"], local_ip=LOCAL_IP, msg=f"Email modifié avec succès : {new_email}")
    
    return "Requête invalide", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("=" * 65)
    print(f" [✓] Serveur Cible Protégé par SameSite démarré sur : http://{LOCAL_IP}:5000")
    print("=" * 65)
    app.run(host='0.0.0.0', port=5000, debug=False)

