# ==============================================================================
# TP AVANCÉ : COMBINAISON CSRF + XSS (CHAÎNE D'EXPLOITATION PÉDAGOGIQUE)
# L'application est protégée contre le CSRF par un jeton secret (Synchronizer Token),
# MAIS elle possède un espace de commentaires vulnérable au XSS Stocké.
# ==============================================================================

import secrets
from flask import Flask, request, session, redirect, url_for, render_template_string, abort

app = Flask(__name__)
app.secret_key = "super_secret_combo_demo"

# Pour la démo, HttpOnly est actif sur le cookie de session (prouvant qu'on n'a même pas
# besoin de voler le cookie de session pour exécuter l'action grâce au XSS !)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Base de données simulée en mémoire
DB = {
    "username": "user",
    "password": "password123",
    "email": "victime.legitime@banque.local",
    "solde": 2500.0,
    "transactions": []
}

# Commentaires du forum interne (Vulnérable au XSS Stocké !)
FORUM_POSTS = [
    {"author": "Admin", "message": "Bienvenue sur l'espace collaboratif et bancaire sécurisé par Token CSRF."}
]

def get_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

HTML_BASE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Banque Privée & Portail Interne - Lab Chaîne XSS+CSRF</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 25px; }
        .wrapper { max-width: 800px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: 1px solid #334155; }
        h1 { color: #38bdf8; font-size: 24px; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 20px; }
        h2 { font-size: 18px; color: #facc15; margin-top: 25px; }
        .grid-info { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
        .card-stat { background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; }
        .card-stat strong { display: block; font-size: 20px; color: #4ade80; margin-top: 5px; }
        .token-box { background: #0c4a6e; border-left: 4px solid #38bdf8; padding: 10px; border-radius: 4px; font-size: 12px; margin: 15px 0; word-break: break-all; }
        .post { background: #0f172a; border-left: 4px solid #f43f5e; padding: 12px; border-radius: 4px; margin-bottom: 10px; }
        input[type="text"], input[type="password"], input[type="number"], textarea { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #475569; color: white; border-radius: 6px; box-sizing: border-box; margin-top: 5px; }
        input[type="submit"], button { background: #38bdf8; color: #0f172a; font-weight: bold; padding: 10px 18px; border: none; border-radius: 6px; cursor: pointer; margin-top: 10px; }
        input[type="submit"]:hover { background: #0ea5e9; }
        .badge-secure { background: #14532d; color: #4ade80; padding: 4px 8px; border-radius: 4px; font-size: 11px; }
        .badge-vuln { background: #7f1d1d; color: #f87171; padding: 4px 8px; border-radius: 4px; font-size: 11px; }
    </style>
</head>
<body>
    <div class="wrapper">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

TEMPLATE_LOGIN = HTML_BASE.replace("{% block content %}{% endblock %}", """
    <h1>Connexion Espace Client Sécurisé</h1>
    <p>Identifiants de test : <strong>user</strong> / <strong>password123</strong></p>
    <form method="POST" action="/login">
        <label>Nom d'utilisateur :</label>
        <input type="text" name="username" value="user" required>
        <label style="margin-top:10px; display:block;">Mot de passe :</label>
        <input type="password" name="password" value="password123" required>
        <input type="submit" value="Se connecter">
    </form>
""")

TEMPLATE_DASHBOARD = HTML_BASE.replace("{% block content %}{% endblock %}", """
    <h1>Portail Bancaire & Collaboratif</h1>
    <div style="margin-bottom:15px; font-size:13px; color:#94a3b8;">
        Connecté en tant que <strong>{{ user }}</strong> | <a href="/logout" style="color:#38bdf8;">Déconnexion</a>
    </div>

    <div class="grid-info">
        <div class="card-stat">
            Solde disponible :
            <strong>{{ solde }} €</strong>
        </div>
        <div class="card-stat">
            Email enregistré :
            <span style="color:#cbd5e1; font-weight:bold; display:block; margin-top:5px;">{{ email }}</span>
        </div>
    </div>

    <!-- MODULE 1 : PROTÉGÉ PAR TOKEN CSRF STRICT -->
    <h2>1. Virement Bancaire <span class="badge-secure">PROTÉGÉ PAR TOKEN ANTI-CSRF</span></h2>
    <div class="token-box">
        🔑 <strong>Jeton Anti-CSRF actif (Synchronizer Token) :</strong><br>
        <code id="currentTokenSpan">{{ csrf_token }}</code>
    </div>

    <form method="POST" action="/virement" id="formVirement">
        <!-- Le jeton secret est obligatoirement requis pour que le virement aboutisse ! -->
        <input type="hidden" name="csrf_token" id="csrf_token_input" value="{{ csrf_token }}">
        <label>Bénéficiaire :</label>
        <input type="text" name="dest" placeholder="Nom du destinataire" required>
        <label style="margin-top:10px; display:block;">Montant (€) :</label>
        <input type="number" name="montant" placeholder="Montant" required>
        <input type="submit" value="Valider le virement sécurisé">
    </form>

    {% if transactions %}
    <h3 style="font-size:14px; margin-top:15px; color:#f87171;">Historique des Débits :</h3>
    <ul>
        {% for t in transactions %}
        <li style="color:#f87171; font-size:13px;">- {{ t.montant }} € vers {{ t.dest }}</li>
        {% endfor %}
    </ul>
    {% endif %}

    <hr style="border:0; border-top:1px solid #334155; margin:30px 0;">

    <!-- MODULE 2 : FORUM INTERNE VULNÉRABLE AU XSS STOCKÉ -->
    <h2>2. Espace d'Échange des Collaborateurs <span class="badge-vuln">VULNÉRABILITÉ XSS STOCKÉ DÉTECTÉE</span></h2>
    <p style="font-size:13px; color:#94a3b8;">Laissez une note ou un mémo visible par tous les utilisateurs de l'entreprise :</p>
    
    <form method="POST" action="/post-message">
        <textarea name="message" rows="3" placeholder="Écrire un message..." required></textarea>
        <input type="submit" value="Publier sur le forum" style="background:#f43f5e; color:white;">
    </form>

    <div style="margin-top:20px;">
        {% for p in posts %}
        <div class="post">
            <strong style="color:#38bdf8;">{{ p.author }} :</strong>
            <!-- FAILLE XSS : Rendu avec | safe sans aucun échappement HTML ! -->
            <div>{{ p.message | safe }}</div>
        </div>
        {% endfor %}
    </div>
""")

@app.route('/')
def index():
    if "user" not in session:
        return redirect('/login')
    token = get_csrf_token()
    return render_template_string(
        TEMPLATE_DASHBOARD,
        user=session["user"],
        solde=DB["solde"],
        email=DB["email"],
        csrf_token=token,
        transactions=DB["transactions"],
        posts=FORUM_POSTS
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == DB["username"] and pwd == DB["password"]:
            session["user"] = user
            get_csrf_token()
            return redirect('/')
    return render_template_string(TEMPLATE_LOGIN)

# ==============================================================================
# ROUTE DU VIREMENT : PROTÉGÉE CONTRE LE CSRF DIRECT VIA TOKEN SECRET !
# Si un pirate soumet cette route depuis un site tiers externe, elle répond 403 !
# ==============================================================================
@app.route('/virement', methods=['POST'])
def virement():
    if "user" not in session:
        return "Non authentifié", 401

    token_soumis = request.form.get('csrf_token')
    token_attendu = session.get('csrf_token')

    # VÉRIFICATION STRICTE ANTI-CSRF
    if not token_soumis or not token_attendu or not secrets.compare_digest(token_soumis, token_attendu):
        abort(403, description="BLOCAGE SÉCURITÉ CSRF : Jeton anti-CSRF manquant ou invalide !")

    dest = request.form.get('dest', 'Inconnu')
    try:
        montant = float(request.form.get('montant', 0))
    except ValueError:
        return "Montant invalide", 400

    if montant > 0 and DB["solde"] >= montant:
        DB["solde"] -= montant
        DB["transactions"].append({"dest": dest, "montant": montant})
        return redirect('/')
    return "Fonds insuffisants", 400

# ==============================================================================
# ROUTE FORUM : VULNÉRABLE AU XSS STOCKÉ (ABSENCE D'ASSAINISSEMENT)
# ==============================================================================
@app.route('/post-message', methods=['POST'])
def post_message():
    if "user" not in session:
        return "Non authentifié", 401
    
    msg = request.form.get('message')
    if msg:
        FORUM_POSTS.append({"author": session["user"], "message": msg})
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    print("=" * 65)
    print(" [✓] Serveur Cible Combiné (CSRF Token + Faille XSS)")
    print("     Actif sur http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host='127.0.0.1', port=5000, debug=False)
