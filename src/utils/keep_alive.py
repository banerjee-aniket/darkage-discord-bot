import os
import threading
import socket
from flask import Flask
import socketserver

# /c:/Users/anike/darkage-discord-bot/src/utils/keep_alive.py
# Lightweight keep-alive helper. Call keep_alive() to start a small HTTP server
# in a background thread so uptime monitors can ping your bot.

PORT = int(os.getenv("PORT", "8080"))


def _find_free_port(preferred):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", preferred))
            return preferred
    except OSError:
        return 0


def keep_alive():
    """
    Start a tiny HTTP server in a daemon thread.
    Tries to use Flask if available, falls back to built-in http.server.
    """
    try:

        app = Flask("keep_alive")

        @app.route("/")
        def index():
            return "OK", 200

        port = PORT if _find_free_port(PORT) == PORT else 0
        thread = threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False),
            daemon=True,
            name="keep-alive-flask",
        )
        thread.start()
        return

    except Exception:
        # Fallback to built-in server (no external dependencies)
        import http.server

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"OK")

            def log_message(self, format, *args):
                # silence default logging
                return

        port = PORT if _find_free_port(PORT) == PORT else 0
        def _serve():
            with socketserver.ThreadingTCPServer(("0.0.0.0", port), Handler) as httpd:
                # allow reuse quickly after restarts
                httpd.allow_reuse_address = True
                httpd.serve_forever()

        thread = threading.Thread(target=_serve, daemon=True, name="keep-alive-http")
        thread.start()
        return