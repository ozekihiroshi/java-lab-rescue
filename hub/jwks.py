"""Fixed-purpose local Moodle signing-key bridge; no arbitrary proxy URLs."""
import json
import os
import urllib.request
from urllib.parse import urlsplit
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/jwks":
            self.send_error(404)
            return
        try:
            request = urllib.request.Request(
                os.environ.get("MOODLE_INTERNAL_URL", "http://moodle-rescue-local").rstrip('/') + "/mod/lti/certs.php",
                headers={"Host": urlsplit(os.environ.get("MOODLE_ORIGIN", "http://localhost:8083")).netloc},
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = response.read()
            assert isinstance(json.loads(payload).get("keys"), list)
        except Exception:
            self.send_error(502)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass

ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
