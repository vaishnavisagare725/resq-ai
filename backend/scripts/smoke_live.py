"""Acceptance test for the LIVE site. Run it after every deployment.

    $env:API_BASE = 'https://resq-ai-api.onrender.com/api'
    $env:DEMO_PASSWORD = '...'
    $env:FRONTEND_URL = 'https://resq-ai-web.onrender.com'    (optional: also checks CORS)
    python scripts\\smoke_live.py
"""
import io
import os
import re
import sys
import time

import requests
from PIL import Image

API = os.environ.get('API_BASE', '').rstrip('/')
PASSWORD = os.environ.get('DEMO_PASSWORD', '')
FRONTEND = os.environ.get('FRONTEND_URL', '').rstrip('/')
if not API or not PASSWORD:
    sys.exit('Set API_BASE (ending in /api) and DEMO_PASSWORD first.')

ROOT = API[:-4] if API.endswith('/api') else API
TIMEOUT = 90
failures = 0


def check(label, ok, detail=''):
    global failures
    if not ok:
        failures += 1
    print(('OK   ' if ok else 'FAIL ') + label + (f'   [{detail}]' if detail else ''))


# 0. wake the server: a free instance can need about a minute
print('Waking the server...')
deadline = time.time() + 180
while True:
    try:
        if requests.get(f'{ROOT}/health/', timeout=30).status_code == 200:
            break
    except requests.RequestException:
        pass
    if time.time() > deadline:
        sys.exit('The server did not wake up within 3 minutes. Check the Render logs.')
    time.sleep(5)
check('server is awake', True)


def login(username):
    r = requests.post(f'{API}/auth/login/', json={'username': username, 'password': PASSWORD},
                      timeout=TIMEOUT)
    r.raise_for_status()
    return {'Authorization': f"Bearer {r.json()['access']}"}


citizen = login('demo_citizen')
fire_boss = login('demo_fire_responder')
fire_worker = login('demo_fire_worker')

# 1. a citizen reports a fire
r = requests.post(f'{API}/incidents/', headers=citizen, timeout=TIMEOUT, json={
    'title': 'Smoke test: building fire', 'description': 'Fire on the second floor, people trapped',
    'latitude': 18.52, 'longitude': 73.85})
check('citizen creates an incident', r.status_code == 201, r.status_code)
incident = r.json()
iid = incident['id']
check('the AI rates it critical and routes it to fire',
      (incident['urgency'], incident['department']) == ('critical', 'fire'))

# 2. a photo, stored on Cloudinary and not on the server's disk
buffer = io.BytesIO()
Image.new('RGB', (40, 40), 'red').save(buffer, 'JPEG')
buffer.seek(0)
r = requests.post(f'{API}/incidents/{iid}/images/', headers=citizen, timeout=TIMEOUT,
                  files={'image': ('smoke.jpg', buffer, 'image/jpeg')})
check('photo uploads', r.status_code == 201, r.status_code)
if r.status_code == 201:
    url = r.json()['images'][0]['image']
    check('photo is stored on Cloudinary', url.startswith('https://res.cloudinary.com/'), url)
    check('photo address opens', requests.get(url, timeout=TIMEOUT).status_code == 200)

# 3. the workflow, with the roles enforced
r = requests.post(f'{API}/incidents/{iid}/take/', headers=citizen, timeout=TIMEOUT)
check('a citizen cannot take a case', r.status_code == 403, r.status_code)
r = requests.post(f'{API}/incidents/{iid}/take/', headers=fire_boss, timeout=TIMEOUT)
check('the fire responder takes it', r.status_code == 200, r.status_code)

workers = requests.get(f'{API}/workers/', headers=fire_boss, timeout=TIMEOUT).json()
worker_id = next((w['id'] for w in workers if w['username'] == 'demo_fire_worker'), None)
check('the responder sees the fire worker', worker_id is not None)
r = requests.post(f'{API}/incidents/{iid}/add-workers/', headers=fire_boss, timeout=TIMEOUT,
                  json={'worker_ids': [worker_id]})
check('the worker is added', r.status_code == 200, r.status_code)
r = requests.post(f'{API}/incidents/{iid}/resolve/', headers=fire_worker, timeout=TIMEOUT,
                  json={'note': 'Smoke test done'})
check('the worker resolves it', r.status_code == 200, r.status_code)
history = requests.get(f'{API}/incidents/{iid}/updates/', headers=fire_boss, timeout=TIMEOUT).json()
check('the history has three entries', len(history) == 3, len(history))

# 4. dashboard data
for path in ('/incidents/summary/', '/incidents/map/'):
    r = requests.get(f'{API}{path}', headers=fire_boss, timeout=TIMEOUT)
    check(f'GET {path}', r.status_code == 200, r.status_code)

# 5. HTTPS and security headers
plain = ROOT.replace('https://', 'http://', 1)
if plain != ROOT:
    r = requests.get(f'{plain}/api/incidents/', allow_redirects=False, timeout=TIMEOUT)
    check('plain http is redirected to https',
          r.status_code in (301, 302, 307, 308) and r.headers.get('Location', '').startswith('https://'),
          r.status_code)
r = requests.get(f'{API}/incidents/', timeout=TIMEOUT)
check('anonymous request gets 401', r.status_code == 401, r.status_code)
check('HSTS header is sent', 'Strict-Transport-Security' in r.headers)

# 6. the admin page and its styling
r = requests.get(f'{ROOT}/admin/login/', timeout=TIMEOUT)
check('admin login page loads', r.status_code == 200, r.status_code)
css = re.search(r'href="(/static/[^"]+\.css)"', r.text)
check('admin stylesheet is served', bool(css) and requests.get(ROOT + css.group(1), timeout=TIMEOUT).status_code == 200)

# 7. CORS for the real website
if FRONTEND:
    r = requests.options(f'{API}/incidents/', timeout=TIMEOUT, headers={
        'Origin': FRONTEND, 'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'authorization'})
    check('CORS allows the website', r.headers.get('access-control-allow-origin') == FRONTEND,
          r.headers.get('access-control-allow-origin'))

print(f'\n{failures} failure(s)')
sys.exit(1 if failures else 0)