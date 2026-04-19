import requests, os, json, time
from pathlib import Path

for line in Path('.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())

G = os.environ['NOIR_GATEWAY_URL']
H = {'Authorization': 'Bearer ' + os.environ['NOIR_API_KEY']}

print("=== HASIL DARI ANDROID AGENT ===")
results = requests.get(G+'/agent/results', headers=H, timeout=10).json()
for r in results.get('results', []):
    d = json.loads(r.get('result') or '{}')
    ok = 'SUCCESS' if d.get('success') else 'FAIL'
    desc = r.get('description', '?')
    out = str(d.get('output', d.get('error', '-')))[:120]
    device = d.get('device_id', '?')
    print(f"[{ok}] {desc}")
    print(f"      device={device} | output={out}")
    print()
print("================================")
