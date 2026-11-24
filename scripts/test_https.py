#!/usr/bin/env python3
"""Test the compiled binary's HTTPS client against synthetic local fixtures."""
import base64
import collections
import http.server
import os
import ssl
import subprocess
import tempfile
import threading
import urllib.parse
import urllib.request
from pathlib import Path

BASE = os.environ.get('CONVERTER_URL', 'http://127.0.0.1:25500')
NODE = 'vless://11111111-1111-4111-8111-111111111111@example.com:443?security=tls&type=tcp#https-test'
hits = collections.Counter()
responses = {}

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def do_GET(self):
        hits[self.path] += 1
        content = responses.get(self.path)
        self.send_response(200 if content is not None else 404)
        payload = content if content is not None else b'Not found'
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        self.wfile.flush()

    def log_message(self, *_args):
        pass

with tempfile.TemporaryDirectory() as temp:
    cert, key = Path(temp) / 'cert.pem', Path(temp) / 'key.pem'
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                    '-days', '1', '-subj', '/CN=localhost', '-keyout', str(key),
                    '-out', str(cert)], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    server = http.server.ThreadingHTTPServer(('0.0.0.0', 0), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    address = 'https://' + os.environ.get('TLS_FIXTURE_HOST', 'host.docker.internal') + ':' + str(server.server_port)
    responses['/nodes.txt'] = base64.b64encode(NODE.encode())
    responses['/rules.list'] = b'DOMAIN-SUFFIX,https-regression.example\n'
    responses['/external.ini'] = (
        '[custom]\nenable_rule_generator=true\noverwrite_original_rules=true\n'
        'custom_proxy_group=HTTPS-REGRESSION`select`.*\n'
        'ruleset=HTTPS-REGRESSION,' + address + '/rules.list\n'
        'ruleset=HTTPS-REGRESSION,[]FINAL\n'
    ).encode()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        query = urllib.parse.urlencode({'target': 'surge6', 'url': address + '/nodes.txt',
                                        'config': address + '/external.ini', 'expand': 'true'})
        with urllib.request.urlopen(BASE + '/sub?' + query, timeout=30) as response:
            result = response.read().decode()
        assert 'HTTPS-REGRESSION = select,https-test' in result, result
        assert ('DOMAIN-SUFFIX,https-regression.example,HTTPS-REGRESSION' in result
                or 'RULE-SET,' + address + '/rules.list,HTTPS-REGRESSION' in result), result
        assert 'FINAL,HTTPS-REGRESSION' in result, result
        assert all(hits[path] for path in responses), dict(hits)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
print('PASS: HTTPS subscription, external config, and rule-set download by compiled converter')
