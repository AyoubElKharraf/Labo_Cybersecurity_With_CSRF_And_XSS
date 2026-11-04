# ==============================================================================
# TP SÉCURITÉ WEB - APPLICATION DÉLIBÉRÉMENT VULNÉRABLE AU XSS
# Présente :
# 1. XSS Réfléchi (Reflected) via la barre de recherche (/search)
# 2. XSS Stocké (Stored / Persistant) via le livre d'or (/guestbook)
# 3. Absence de HttpOnly sur les cookies (permet le vol de session)
# ==============================================================================

from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "cle_secrete_demo_xss"

# VULNÉRABILITÉ MAJEURE : HttpOnly désactivé -> document.cookie est accessible en JavaScript !
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = None

# "Base de données" simulée en mémoire pour les commentaires du livre d'or
COMMENTS = [
    {"author": "Alice", "content": "Bienvenue sur notre nouveau blog de formation !"},
    {"author": "Bob", "content": "Superbe initiative pour le TP de cybersécurité."}
]

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Portail Collaboratif - Vulnérable XSS</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; margin: 30px; }
        .container { max-width: 750px; margin: auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #d9534f; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { color: #333; margin-top: 25px; }
        .badge { background: #fee2e2; color: #b91c1c; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
        .nav { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        .nav a { margin-right: 15px; text-decoration: none; color: #0284c7; font-weight: 500; }
        .search-box { display: flex; gap: 10px; margin: 15px 0; }
        input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"], button { background-color: #d9534f; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        input[type="submit"]:hover { background-color: #b91c1c; }
        .comment-card { background: #fdf2f2; border-left: 4px solid #ef4444; padding: 12px; margin-bottom: 12px; border-radius: 0 4px 4px 0; }
        .author { font-weight: bold; color: #1f2937; margin-bottom: 4px; }
        .cookie-box { background: #fffbeb; border: 1px solid #fef3c7; color: #92400e; padding: 10px; border-radius: 4px; font-size: 13px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Accueil</a>
            <a href="/search?q=sécurité">Recherche (XSS Réfléchi)</a>
            <a href="/guestbook">Livre d'or (XSS Stocké)</a>
            {% if session.get('user') %}
                <span style="float: right;">Connecté en tant que <strong>{{ session['user'] }}</strong> | <a href="/logout">Déconnexion</a></span>
            {% else %}
                <a href="/login" style="float: right;">Se connecter</a>
            {% endif %}
        </div>

        <div class="cookie-box">
            🍪 <strong>État du Cookie de Session :</strong> 
            <code>HttpOnly = False</code> (Accessible en lecture via <code>document.cookie</code>).
        </div>

        {% block body %}{% endblock %}
    </div>
</body>
</html>
"""

TEMPLATE_HOME = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Portail Entreprise (Démo Vulnérable XSS) <span class="badge">VULNÉRABLE</span></h1>
    <p>Cette application illustre les deux grands vecteurs de failles <strong>Cross-Site Scripting (XSS)</strong> :</p>
    <ul>
        <li><strong>XSS Réfléchi (Reflected)</strong> : Via la page de recherche.</li>
        <li><strong>XSS Stocké (Stored)</strong> : Via le livre d'or partagé entre utilisateurs.</li>
    </ul>
    <p>Connectez-vous d'abord pour posséder un cookie de session contenant un secret :</p>
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
    <h1>Moteur de Recherche Interne</h1>
    <form method="GET" action="/search" class="search-box">
        <input type="text" name="q" placeholder="Tapez votre recherche..." value="{{ query_raw }}">
        <input type="submit" value="Rechercher">
    </form>

    {% if query_raw %}
        <div style="margin-top: 20px; padding: 15px; background: #f3f4f6; border-radius: 4px;">
            <!-- 
                LIGNE VULNÉRABLE XSS RÉFLÉCHI :
                Le filtre '| safe' désactive l'échappement automatique de Jinja2 !
                Le texte tapé dans l'URL s'insère tel quel dans le DOM HTML !
            -->
            Résultats pour votre recherche : <strong>{{ query_raw | safe }}</strong>
            <p><em>Aucun article trouvé.</em></p>
        </div>
    {% endif %}
""")

TEMPLATE_GUESTBOOK = HTML_LAYOUT.replace("{% block body %}{% endblock %}", """
    <h1>Livre d'Or des Employés (XSS Stocké)</h1>
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
                LIGNE VULNÉRABLE XSS STOCKÉ :
                Le contenu du message est rendu avec '| safe' sans aucune désinfection !
                Tout script injecté reste en mémoire et s'exécute pour TOUS les visiteurs !
            -->
            <div class="author">{{ c.author }} :</div>
            <div>{{ c.content | safe }}</div>
        </div>
    {% endfor %}
""")


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


# ==============================================================================
# ROUTE 1 : VULNÉRABLE AU XSS RÉFLÉCHI (REFLECTED XSS)
# ==============================================================================
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # La variable query est passée brute et affichée avec '| safe' dans le template
    return render_template_string(TEMPLATE_SEARCH, query_raw=query)


# ==============================================================================
# ROUTE 2 : VULNÉRABLE AU XSS STOCKÉ / PERSISTANT (STORED XSS)
# ==============================================================================
@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        author = request.form.get('author', 'Anonyme')
        content = request.form.get('content', '')
        if content:
            # Enregistrement direct sans nettoyage / assainissement (sanitization)
            COMMENTS.append({"author": author, "content": content})
            return redirect(url_for('guestbook'))
    return render_template_string(TEMPLATE_GUESTBOOK, comments=COMMENTS)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)

