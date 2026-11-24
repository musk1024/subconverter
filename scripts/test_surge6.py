#!/usr/bin/env python3
"""Exercise the converter using synthetic nodes; no real subscription is needed."""
import base64
import time
import urllib.parse
import urllib.request

BASE = 'http://127.0.0.1:25500'
NODE = 'vless://11111111-1111-4111-8111-111111111111@example.com:443?security=tls&sni=example.com&type=tcp#surge6-test'

def convert(target, version=None, node_list=True, node=NODE):
    params = {'target': target, 'url': node, 'list': str(node_list).lower()}
    if version is not None:
        params['ver'] = str(version)
    with urllib.request.urlopen(BASE + '/sub?' + urllib.parse.urlencode(params), timeout=20) as r:
        return r.read().decode()

for attempt in range(60):
    try:
        urllib.request.urlopen(BASE + '/version', timeout=2).close()
        break
    except OSError:
        time.sleep(1)
else:
    raise RuntimeError('Converter did not become ready')

for target, version in [('surge6', None), ('surge', 6)]:
    for node_list in [True, False]:
        result = convert(target, version, node_list)
        assert 'vless,' in result and '11111111-1111-4111-8111-111111111111' in result, result
        if not node_list:
            assert '[Proxy]' in result and '[Rule]' in result, result
    ws = convert(target, version, node=NODE.replace('type=tcp', 'type=ws&path=%2Fws&host=example.com'))
    assert 'vless,' in ws and 'ws=true' in ws, ws

# Include a supported node so old targets return a valid list after skipping VLESS.
ss_auth = base64.urlsafe_b64encode(b'aes-128-cfb:synthetic-password').decode().rstrip('=')
combined = NODE + '|ss://' + ss_auth + '@example.org:8388#ss-test'
for version in [2, 3, 4, 5]:
    result = convert('surge', version, node=combined)
    assert 'vless,' not in result and 'ss-test' in result, result
print('PASS: Surge 6 aliases, full profiles, node lists, WebSocket, and Surge 2–5 VLESS exclusion')
