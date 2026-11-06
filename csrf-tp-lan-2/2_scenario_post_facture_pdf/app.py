# ==============================================================================
# SCÉNARIO 2 : MÉTHODE POST - APPLICATION CLIENT VULNÉRABLE (ADRESSE/LIVRAISON)
# ==============================================================================
import socket
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "secret_scenario_2_post"
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False

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
    <title>Portail Télécom & Abonnements - Scénario 2</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 30px; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        h1 { color: #d97706; font-size: 22px; }
        .badge-ip { background: #fef3c7; color: #b45309; padding: 6px 10px; border-radius: 4px; font-size: 13px; font-weight: bold; }
        .box { background: #f1f5f9; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #d97706; }
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
    <h1>Espace Client Télécom (Ayoub)</h1>
    <div class="box">
        <p><strong>Formule active :</strong> {{ abo }}</p>
        <p><strong>Adresse de facturation / livraison :</strong><br><span style="color:#d97706; font-size:16px; font-weight:bold;">{{ adresse }}</span></p>
    </div>
    
    <h3>Modifier mon adresse :</h3>
    <form method="POST" action="/update-adresse">
        <input type="text" name="nouvelle_adresse" placeholder="Nouvelle adresse..." required style="width:100%; padding:8px;"><br><br>
        <input type="submit" value="Enregistrer l'adresse" style="background:#d97706; color:white; border:none; padding:10px 15px; border-radius:4px; cursor:pointer;">
    </form>
    <br><a href="/logout" style="color:#666; font-size:13px;">Se déconnecter</a>
""")

@app.route('/')
def index():
    if "user" in session:
        return render_template_string(TEMPLATE_DASHBOARD, abo=DB["abonnements"], adresse=DB["adresse_livraison"], local_ip=LOCAL_IP)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == DB["username"] and request.form.get('password') == DB["password"]:
            session["user"] = DB["username"]
            return redirect('/')
    return """
    <h2>Connexion Espace Client</h2>
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
    
    nouvelle = request.form.get('nouvelle_adresse')
    if nouvelle:
        DB["adresse_livraison"] = nouvelle
        return render_template_string(TEMPLATE_DASHBOARD, abo=DB["abonnements"], adresse=DB["adresse_livraison"], local_ip=LOCAL_IP)
    return "Adresse vide", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print(f"[✓] Scénario 2 (POST) actif sur http://{LOCAL_IP}:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
