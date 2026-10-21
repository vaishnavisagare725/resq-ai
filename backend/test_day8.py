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


citizen, r1, r2, admin = login('citizen1'), login('responder1'), login('responder2'), login('admin')

# 1. the AI sets urgency, category and department on creation
CASES = [
    ('Building fire', 'Fire on second floor, people trapped', 'critical', 'fire', 'fire'),
    ('Chest pain', 'Man has severe chest pain at the bus stop', 'high', 'medical', 'medical'),
    ('Highway crash', 'Two cars crashed, many people injured', 'critical', 'accident', 'police'),
    ('Water logging', 'Street flooded after rain', 'high', 'flood', 'disaster'),
    ('Pothole', 'There is a big pothole on the main road', 'low', 'other', ''),
]
ids = {}
for title, desc, urgency, category, dept in CASES:
    r = check(f'create "{title}"', requests.post(f'{BASE}/incidents/', headers=citizen, json={
        'title': title, 'description': desc, 'latitude': 18.5, 'longitude': 73.8}), 201)
    d = r.json()
    ids[title] = d['id']
    same('urgency', d['urgency'], urgency)
    same('category', d['category'], category)
    same('department', d['department'], dept)
    print('         reason:', d['ai_reason'])

# 2. the client cannot fake the AI fields
r = check('citizen tries to fake urgency', requests.post(f'{BASE}/incidents/', headers=citizen, json={
    'title': 'Help', 'description': 'Please help me quickly', 'latitude': 18.5, 'longitude': 73.8,
    'urgency': 'critical', 'category': 'fire', 'department': 'fire'}), 201)
same('urgency stays low', r.json()['urgency'], 'low')
same('category stays other', r.json()['category'], 'other')

# 3. routing decides who sees what
fire = f"{BASE}/incidents/{ids['Building fire']}/"
check('fire responder sees the fire incident', requests.get(fire, headers=r1), 200)
check('medical responder does not', requests.get(fire, headers=r2), 404)

pot = f"{BASE}/incidents/{ids['Pothole']}/"
check('unrouted: responder1 sees it', requests.get(pot, headers=r1), 200)
check('unrouted: responder2 sees it', requests.get(pot, headers=r2), 200)
same('needs_review is True', requests.get(pot, headers=r1).json()['needs_review'], True)

# 4. human triage
url = f'{pot}triage/'
check('citizen cannot triage', requests.post(url, headers=citizen, json={'urgency': 'high'}), 403)
check('no token gives 401', requests.post(url, json={'urgency': 'high'}), 401)
check('empty body rejected', requests.post(url, headers=r1, json={}), 400)
check('invalid urgency rejected', requests.post(url, headers=r1, json={'urgency': 'urgent'}), 400)
r = check('responder1 corrects it to high + medical', requests.post(
    url, headers=r1, json={'urgency': 'high', 'category': 'medical', 'note': 'caller says a man fell'}), 200)
same('department routed to medical', r.json()['department'], 'medical')
same('needs_review cleared', r.json()['needs_review'], False)
check('responder1 no longer sees it', requests.get(pot, headers=r1), 404)
check('responder2 now sees it', requests.get(pot, headers=r2), 200)

# 5. triage rules after the case is taken
check('responder2 takes it', requests.post(f'{pot}take/', headers=r2), 200)
check('nothing to change', requests.post(url, headers=r2, json={'urgency': 'high'}), 400)
check('urgency can still change', requests.post(url, headers=r2, json={'urgency': 'critical'}), 200)
check('department cannot change after taking', requests.post(url, headers=r2, json={'category': 'fire'}), 400)

# 6. history and review queue
r = check('history', requests.get(f'{pot}updates/', headers=r2), 200)
for row in reversed(r.json()):
    print('    ', row['updated_by_name'], '|', row['note'])

r = check('needs_review filter', requests.get(f'{BASE}/incidents/?needs_review=true', headers=admin), 200)
print('    still waiting for review:', [i['title'] for i in r.json()['results']])