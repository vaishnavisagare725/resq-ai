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


USERS = [('citizen1', None), ('responder1', None), ('responder2', None),
         ('admin', None), ('Ramesh', None), ('Arati', None)]

for name, _ in USERS:
    h = login(name)
    s = get('/incidents/summary/', h).json()
    active = s['open'] + s['assigned']

    m = check(f'map as {name}', get('/incidents/map/', h), 200).json()
    same(f'{name}: map has every active incident', len(m['results']), active)
    same(f'{name}: nothing resolved on the map', all(p['status'] != 'resolved' for p in m['results']), True)
    same(f'{name}: not truncated', m['truncated'], False)
    if m['results']:
        same(f'{name}: the slim fields only',
             set(m['results'][0]) == {'id', 'title', 'latitude', 'longitude', 'urgency', 'status',
                                      'category', 'needs_review'}, True)
        same(f'{name}: coordinates are numbers',
             all(isinstance(p['latitude'], float) and isinstance(p['longitude'], float)
                 for p in m['results']), True)

    count = get('/incidents/?active=true', h).json()['count']
    same(f'{name}: active filter matches', count, active)

check('map needs a token', get('/incidents/map/'), 401)

# most urgent first
h = login('admin')
rows = get('/incidents/map/', h).json()['results']
rank = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
order = [rank[p['urgency']] for p in rows]
same('map is sorted by urgency', order == sorted(order), True)