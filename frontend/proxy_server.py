from http.server import SimpleHTTPRequestHandler, HTTPServer
import requests

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api'):
            self.proxy_request('GET')
        else:
            # Serve index.html for any other path
            self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api'):
            self.proxy_request('POST')
        else:
            super().do_POST()

    def do_PUT(self):
        if self.path.startswith('/api'):
            self.proxy_request('PUT')
        else:
            super().do_PUT()

    def do_DELETE(self):
        if self.path.startswith('/api'):
            self.proxy_request('DELETE')
        else:
            super().do_DELETE()

    def proxy_request(self, method):
        # Proxy API requests to another server
        url = 'http://localhost:7123' + self.path
        headers = dict(self.headers)
        body = self.rfile.read(int(self.headers['Content-Length'])) if 'Content-Length' in self.headers else None
        response = requests.request(method, url, headers=headers, data=body)
        self.send_response(response.status_code)
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response.content)

def run(server_class=HTTPServer, handler_class=ProxyHandler, port=5000):
    # Start the HTTP server
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
