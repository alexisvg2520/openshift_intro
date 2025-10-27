# app.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import time
import socket
import os

# 👉 Para LOCAL cambia esta URL a "http://localhost:8081/"
# 👉 En Kubernetes/OpenShift usa el DNS del Service de B:
URL_APP_B = os.getenv("URL_APP_B", "http://mi-servicio2.ecuaalejo2013-dev.svc.cluster.local:8080/")

START_TIME = time.time()
STARTUP_GRACE_SECONDS = int(os.getenv("STARTUP_GRACE_SECONDS", "1"))  # por si quieres demorar start-up

def http_ok(url: str, timeout: float = 3.0) -> bool:
    try:
        # HEAD suele ser suficiente y más liviano
        req = Request(url, method="HEAD")
        with urlopen(req, timeout=timeout) as resp:
            code = resp.getcode() or 200
            return 200 <= code < 400
    except HTTPError as e:
        # Si es 404 en B pero el servicio responde, igual consideramos listo (depende de tu caso)
        return 200 <= e.code < 500
    except URLError:
        return False
    except Exception:
        return False

class HolaAHandler(BaseHTTPRequestHandler):
    def _send(self, code: int, text: str, ctype="text/plain; charset=utf-8"):
        body = text.encode("utf-8", "replace")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        # -------- Startup probe --------
        if path == "/startup":
            # Opción: dar un pequeño margen de arranque
            if time.time() - START_TIME >= STARTUP_GRACE_SECONDS:
                return self._send(200, "OK - startup")
            else:
                return self._send(503, "Starting up...")

        # -------- Readiness probe --------
        if path == "/readiness":
            ready = http_ok(URL_APP_B, timeout=2.0)
            if ready:
                return self._send(200, "OK - ready (B reachable)")
            else:
                return self._send(503, "Not ready - B unreachable")

        # -------- Liveness probe --------
        if path == "/health":
            # Check mínimo: socket hostname resolve + proceso vivo
            try:
                socket.gethostname()
                return self._send(200, "OK - healthy")
            except Exception as e:
                return self._send(500, f"Unhealthy: {e}")

        # -------- Ruta por defecto: llama a B y devuelve su respuesta --------
        try:
            with urlopen(URL_APP_B, timeout=5) as resp:
                data = resp.read()
                status = resp.getcode() or 200
                msg = f"🛰️ Respuesta desde app B: {data.decode('utf-8', 'replace')}"
                return self._send(status, msg)
        except HTTPError as e:
            return self._send(502, f"❌ HTTPError {e.code} al llamar a app B")
        except URLError as e:
            return self._send(502, f"❌ URLError al llamar a app B: {e.reason}")
        except Exception as e:
            return self._send(500, f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    server = HTTPServer(("", 8080), HolaAHandler)
    print("App A escuchando (llamará a B): ")
    server.serve_forever()