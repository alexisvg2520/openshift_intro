# app_a.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# 👉 Para LOCAL cambia esta URL a "http://localhost:8081/"
# 👉 En Kubernetes/OpenShift usa el DNS del Service de B:
URL_APP_B = "http://mi-servicio2.ecuaalejo2013-dev.svc.cluster.local:8080/"

class HolaAHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with urlopen(URL_APP_B, timeout=5) as resp:
                data = resp.read()
                status = resp.getcode() or 200
                body = f"🛰️ Respuesta desde app B: {data.decode('utf-8', 'replace')}".encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except HTTPError as e:
            body = f"❌ HTTPError {e.code} al llamar a app B".encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except URLError as e:
            body = f"❌ URLError al llamar a app B: {e.reason}".encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            msg = f"❌ Error inesperado: {e}"
            body = msg.encode("utf-8", "replace")
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

if __name__ == "__main__":
    server = HTTPServer(("", 8080), HolaAHandler)
    print("App A escuchando (llamará a B): ")
    server.serve_forever()