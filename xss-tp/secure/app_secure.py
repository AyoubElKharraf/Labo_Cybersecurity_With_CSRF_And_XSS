# ==============================================================================
# TP SÉCURITÉ WEB - APPLICATION SÉCURISÉE CONTRE LE XSS (OWASP)
# Protections appliquées :
# 1. Échappement automatique (Contextual Output Encoding / Auto-escaping Jinja2)
# 2. Activation stricte du flag HttpOnly (Interdit document.cookie en JavaScript)
# 3. Content Security Policy (CSP) stricte (Interdit l'exécution de scripts inline)
# ==============================================================================

from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "cle_secrete_demo_xss_secure"

# ==============================================================================
# PROTECTION N°1 : FLAG HttpOnly ACTIF SUR LE COOKIE DE SESSION
# Même si un script malveillant réussissait à s'exécuter, document.cookie renvoie vide !
# ==============================================================================
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

COMMENTS = [
    {"author": "Alice", "content": "Bienvenue sur notre nouveau blog sécurisé !"},
    {"author": "Bob", "content": "Toutes les entrées sont désormais échappées."}
]

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Portail Collaboratif - Sécurisé XSS</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 30px; }
        .container { max-width: 750px; margin: auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #15803d; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { color: #333; margin-top: 25px; }
        .badge { background: #dcfce7; color: #15803d; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
        .nav { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        .nav a { margin-right: 15px; text-decoration: none; color: #0284c7; font-weight: 500; }
        .search-box { display: flex; gap: 10px; margin: 15px 0; }
        input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"], button { background-color: #15803d; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        input[type="submit"]:hover { background-color: #166534; }
        .comment-card { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 12px; margin-bottom: 12px; border-radius: 0 4px 4px 0; }
        .author { font-weight: bold; color: #1f2937; margin-bottom: 4px; }
        .cookie-box { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; padding: 10px; border-radius: 4px; font-size: 13px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Accueil</a>
            <a href="/search?q=sécurité">Recherche (XSS Réfléchi Protégé)</a>
            <a href="/guestbook">Livre d'or (XSS Stocké Protégé)</a>
            {% if session.get('user') %}
                <span style="float: right;">Connecté en tant que <strong>{{ session['user'] }}</strong> | <a href="/logout">Déconnexion</a></span>
            {% else %}
                <a href="/login" style="float: right;">Se connecter</a>
            {% endif %}
        </div>

        <div class="cookie-box">
            🛡️ <strong>Défenses Actives :</strong> 
            <code>HttpOnly = True</code> + Échappement HTML automatique + <code>Content-Security-Policy</code>.
        </div>

        {% block body %}{% endblock %}
    </div>
</body>
</html>
"""

TEMPLATE_HOME = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Portail Entreprise (Version Sécurisée) <span class="badge">PROTÉGÉ</span></h1>
    <p>Cette version neutralise les attaques XSS par plusieurs couches de défense en profondeur :</p>
    <ul>
        <li><strong>Échappement automatique (HTML Entity Encoding)</strong> : Les balises &lt;script&gt; sont converties en texte inoffensif.</li>
        <li><strong>Cookie HttpOnly</strong> : Le cookie est masqué vis-à-vis de l'API JavaScript <code>document.cookie</code>.</li>
        <li><strong>Content-Security-Policy (CSP)</strong> : Empêche l'exécution de scripts injectés.</li>
    </ul>
    <p><a href="/login"><button>Se connecter avec le compte Ayoub</button></a></p>
""")

TEMPLATE_LOGIN = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Connexion Utilisateur</h1>
    <p>Identifiants de test : <strong>Ayoub</strong> / <strong>password123</strong></p>
    <form method="POST" action="/login">
        <label>Nom d'utilisateur :</label>
        <input type="text" name="username" value="Ayoub" required><br><br>
        <label>Mot de passe :</label>
        <input type="password" name="password" value="password123" required><br><br>
        <input type="submit" value="Ouvrir la session">
    </form>
""")

TEMPLATE_SEARCH = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Moteur de Recherche Interne (Sécurisé)</h1>
    <form method="GET" action="/search" class="search-box">
        <input type="text" name="q" placeholder="Tapez votre recherche..." value="{{ query }}">
        <input type="submit" value="Rechercher">
    </form>

    {% if query %}
        <div style="margin-top: 20px; padding: 15px; background: #f3f4f6; border-radius: 4px;">
            <!-- 
                PROTECTION N°2 : ÉCHAPPEMENT PAR DÉFAUT JINJA2
                Sans le filtre '| safe', <script> devient &lt;script&gt;
                Le navigateur affiche le code sous forme de texte pur sans JAMAIS l'exécuter !
            -->
            Résultats pour votre recherche : <strong>{{ query }}</strong>
            <p><em>Aucun article trouvé.</em></p>
        </div>
    {% endif %}
""")

TEMPLATE_GUESTBOOK = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Livre d'Or des Employés (Sécurisé)</h1>
    <p>Laissez un message visible par tous les employés connectés :</p>

    <form method="POST" action="/guestbook">
        <label>Votre nom :</label>
        <input type="text" name="author" value="{{ session.get('user', 'Anonyme') }}" required><br><br>
        <label>Votre message :</label>
        <textarea name="content" rows="3" placeholder="Écrivez votre commentaire..." required></textarea><br><br>
        <input type="submit" value="Publier le message">
    </form>

    <h2>Messages publiés :</h2>
    {% for c in comments %}
        <div class="comment-card">
            <!-- 
                PROTECTION N°3 : RENDU SÉCURISÉ DU CONTENU UTILISATEUR
                L'échappement HTML garantit que le texte est inoffensif même si un pirate
                injecte <script src="..."></script> ou <img onerror="...">.
            -->
            <div class="author">{{ c.author }} :</div>
            <div>{{ c.content }}</div>
        </div>
    {% endfor %}
""")


# ==============================================================================
# PROTECTION N°4 : CONTENT SECURITY POLICY (CSP)
# En-tête HTTP indiquant au navigateur quelles sources de scripts sont autorisées
# ==============================================================================
@app.after_request
def set_security_headers(response):
    # Interdit l'exécution de scripts inline non autorisés
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline';"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.route('/')
def index():
    return render_template_string(TEMPLATE_HOME)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        if user:
            session['user'] = user
            session['secret_token'] = "SECRET_SESSION_TOKEN_AYOUB_998877"
            return redirect(url_for('guestbook'))
    return render_template_string(TEMPLATE_LOGIN)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    # La variable query est rendue avec échappement HTML natif Jinja2
    return render_template_string(TEMPLATE_SEARCH, query=query)


@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        author = request.form.get('author', 'Anonyme')
        content = request.form.get('content', '')
        if content:
            COMMENTS.append({"author": author, "content": content})
            return redirect(url_for('guestbook'))
    return render_template_string(TEMPLATE_GUESTBOOK, comments=COMMENTS)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)

