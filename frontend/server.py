import http.client
import os
import socket
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse


class ProxyHandler(SimpleHTTPRequestHandler):
    """静态文件 + API 代理"""

    def __init__(self, *args, **kwargs):
        self.static_dir = os.path.join(os.path.dirname(__file__), 'dist')
        super().__init__(*args, directory=self.static_dir, **kwargs)

    def do_GET(self):
        if self.path.startswith('/api/') or self.path.startswith('/uploads/'):
            self._proxy('GET')
        else:
            # 前端路由 history mode fallback
            target = os.path.join(self.static_dir, self.path.lstrip('/'))
            if not os.path.exists(target) or os.path.isdir(target):
                self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/') or self.path.startswith('/uploads/'):
            self._proxy('POST')
        else:
            self.send_error(404)

    def do_PUT(self):
        if self.path.startswith('/api/') or self.path.startswith('/uploads/'):
            self._proxy('PUT')
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith('/api/') or self.path.startswith('/uploads/'):
            self._proxy('DELETE')
        else:
            self.send_error(404)

    def _proxy(self, method):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length else None

            conn = http.client.HTTPConnection('localhost', 8000, timeout=30)
            headers = {k: v for k, v in self.headers.items() if k.lower() not in ('host', 'content-length')}
            headers['Host'] = 'localhost:8000'
            conn.request(method, self.path, body=body, headers=headers)
            resp = conn.getresponse()

            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() not in ('transfer-encoding', 'connection', 'content-length'):
                    self.send_header(k, v)
            self.send_header('Content-Length', resp.length or len(resp.read()))
            self.end_headers()

            if resp.length is None:
                data = resp.read()
                self.wfile.write(data)
            else:
                while chunk := resp.read(8192):
                    self.wfile.write(chunk)
            conn.close()
        except Exception as e:
            self.send_error(502, message=str(e))

    def log_message(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


def find_free_port(start=8080):
    for port in range(start, start + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    raise RuntimeError('No free port found')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', find_free_port()))
    server = ReusableHTTPServer(('0.0.0.0', port), ProxyHandler)
    print(f'Server running at http://0.0.0.0:{port}')
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print('Press Ctrl+C to stop')
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.shutdown()
