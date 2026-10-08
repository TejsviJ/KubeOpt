from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        data = b"kubeopt"

        # Deliberately CPU-intensive work
        for _ in range(200_000):
            data = hashlib.sha256(data).digest()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"KubeOpt API OK\n")

    def log_message(self, format, *args):
        pass


server = HTTPServer(("0.0.0.0", 8080), Handler)

print("KubeOpt API listening on port 8080")

server.serve_forever()