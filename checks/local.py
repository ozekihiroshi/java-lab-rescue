"""Read-only checks for the running standalone local deployment."""
from pathlib import Path
import sys
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from lab import model, inventory, selected

config = model()
hubs, _ = selected(config, inventory())
for service in ('jwks', 'jupyterhub'):
    items = [i for i in hubs if i['Config']['Labels'].get('com.docker.compose.service') == service]
    assert len(items) == 1 and items[0]['State']['Running']
    assert items[0]['State']['Health']['Status'] == 'healthy'
port = config['services']['jupyterhub']['ports'][0]['published']
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
assert opener.open(f'http://127.0.0.1:{port}/hub/health', timeout=10).status == 200
print('PASS: standalone Compose, Hub, local JWKS and health endpoint')
