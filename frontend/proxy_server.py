from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.request

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api'):
            # Proxy API requests to another server
            url = 'http://localhost:7123' + self.path
            with urllib.request.urlopen(url) as response:
                data = response.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
        else:
            # Serve static files as usual
            super().do_GET()

def run(server_class=HTTPServer, handler_class=ProxyHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
