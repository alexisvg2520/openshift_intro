from http.server import BaseHTTPRequestHandler, HTTPServer

class HolaHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Hola Mundo")

if __name__ == "__main__":
    server = HTTPServer(("", 8080), HolaHandler)
    print("Servidor iniciado en el puerto 8080...")
    server.serve_forever()