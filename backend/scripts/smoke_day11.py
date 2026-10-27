from concurrent.futures import ThreadPoolExecutor

import requests

BASE = 'http://127.0.0.1:8000/api'


def login(username, password='Test@1234'):
    r = requests.post(f'{BASE}/auth/login/', json={'username': username, 'password': password})
    r.raise_for_status()
    return {'Authorization': f"Bearer {r.json()['access']}"}


def check(label, response, expected):
    mark = 'OK  ' if response.status_code == expected else 'FAIL'
    print(f'{mark} {label}: got {response.status_code}, expected {expected}')
    return response


def same(label, actual, expected):
    mark = 'OK  ' if actual == expected else 'FAIL'
    print(f'{mark}     {label}: got {actual!r}, expected {expected!r}')


def get(path, headers=None):
    return requests.get(f'{BASE}{path}', headers=headers)


citizen, r1, r2 = login('citizen1'), login('responder1'), login('responder2')
admin, ramesh = login('admin'), login('Ramesh')

# 1. the workers list: a responder sees only their own department
r = check('responder1 lists workers', get('/workers/', r1), 200)
names = [w['username'] for w in r.json()]
same('only fire workers', all(w['department'] == 'fire' for w in r.json()), True)
same('Ramesh is listed', 'Ramesh' in names, True)
same('Arati is not listed', 'Arati' in names, False)

r = check('responder2 lists workers', get('/workers/', r2), 200)
names = [w['username'] for w in r.json()]
same('Arati is listed', 'Arati' in names, True)
same('Ramesh is not listed', 'Ramesh' in names, False)

check('citizen cannot list workers', get('/workers/', citizen), 403)
check('worker cannot list workers', get('/workers/', ramesh), 403)
check('no token gives 401', get('/workers/'), 401)

r = check('admin filters by department', get('/workers/?department=medical', admin), 200)
same('all medical', all(w['department'] == 'medical' for w in r.json()), True)

# 2. the summary counts must match the list for every role
for label, headers in [('citizen1', citizen), ('responder1', r1), ('responder2', r2),
                       ('admin', admin), ('Ramesh', ramesh)]:
    s = check(f'summary as {label}', get('/incidents/summary/', headers), 200).json()
    for key in ('open', 'assigned', 'resolved'):
        count = get(f'/incidents/?status={key}', headers).json()['count']
        same(f'{label}: {key} matches the list', s[key], count)
    count = get('/incidents/?status=open&urgency=critical', headers).json()['count']
    same(f'{label}: critical_open matches', s['critical_open'], count)
    count = get('/incidents/?status=open&needs_review=true', headers).json()['count']
    same(f'{label}: needs_review_open matches', s['needs_review_open'], count)
check('summary needs a token', get('/incidents/summary/'), 401)

# 3. the race: two responders take the same unrouted incident at the same moment
inc = requests.post(f'{BASE}/incidents/', headers=citizen, json={
    'title': 'Need help', 'description': 'Please send someone to the old market area',
    'latitude': 18.5, 'longitude': 73.8}).json()
url = f"{BASE}/incidents/{inc['id']}/take/"


def take(headers):
    return requests.post(url, headers=headers).status_code


with ThreadPoolExecutor(max_workers=2) as pool:
    codes = list(pool.map(take, [r1, r2]))
same('exactly one responder wins the race', sorted(codes), [200, 400])