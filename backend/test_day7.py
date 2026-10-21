import os
import tempfile

import requests
from PIL import Image

BASE = 'http://127.0.0.1:8000/api'
RAMESH, ARATI = 4, 5          # fire worker, medical worker ids: check yours

tmp = tempfile.mkdtemp()      # test pictures live in a temp folder, not in your project
GOOD = os.path.join(tmp, 'photo.jpg')
FAKE = os.path.join(tmp, 'fake.jpg')
Image.new('RGB', (300, 200), 'red').save(GOOD)
with open(FAKE, 'w') as f:
    f.write('this is not an image')


def login(username, password='Test@1234'):
    r = requests.post(f'{BASE}/auth/login/', json={'username': username, 'password': password})
    r.raise_for_status()
    return {'Authorization': f"Bearer {r.json()['access']}"}


def check(label, response, expected):
    mark = 'OK  ' if response.status_code == expected else 'FAIL'
    print(f'{mark} {label}: got {response.status_code}, expected {expected}')
    return response


def upload(url, headers, path=GOOD):
    with open(path, 'rb') as f:
        return requests.post(f'{url}/images/', headers=headers,
                             files={'image': (os.path.basename(path), f, 'image/jpeg')})


citizen, r1, r2 = login('citizen1'), login('responder1'), login('responder2')
ramesh, arati, admin = login('Ramesh'), login('Arati'), login('admin')

# 1. a citizen reports a new incident (no department yet)
r = check('citizen creates incident', requests.post(f'{BASE}/incidents/', headers=citizen, json={
    'title': 'Chest pain', 'description': 'Man has severe chest pain at the bus stop',
    'latitude': 18.5, 'longitude': 73.8}), 201)
iid = r.json()['id']
url = f'{BASE}/incidents/{iid}'

# 2. photos before the case is taken
r = check('reporter uploads a photo', upload(url, citizen), 201)
print('    image url:', r.json()['images'][0]['image'])
check('responder1 sees the unrouted incident but is not involved', upload(url, r1), 403)
check('no token gives 401', requests.post(f'{url}/images/'), 401)

# 3. taking the case
check('citizen cannot take', requests.post(f'{url}/take/', headers=citizen), 403)
check('responder2 takes it', requests.post(f'{url}/take/', headers=r2), 200)
check('responder1 now cannot see it', requests.post(f'{url}/take/', headers=r1), 404)
check('cannot take twice', requests.post(f'{url}/take/', headers=r2), 400)

# 4. adding workers
check('wrong-department worker rejected', requests.post(
    f'{url}/add-workers/', headers=r2, json={'worker_ids': [RAMESH]}), 400)
check('worker cannot add workers', requests.post(
    f'{url}/add-workers/', headers=arati, json={'worker_ids': [ARATI]}), 403)
check('responder2 adds Arati', requests.post(
    f'{url}/add-workers/', headers=r2, json={'worker_ids': [ARATI]}), 200)
check('empty list rejected', requests.post(
    f'{url}/add-workers/', headers=r2, json={'worker_ids': []}), 400)

# 5. more photos
check('Arati (worker on it) uploads', upload(url, arati), 201)
check('Ramesh cannot see it', upload(url, ramesh), 404)
check('a text file renamed .jpg is rejected', upload(url, citizen, FAKE), 400)
check('3rd photo', upload(url, citizen), 201)
check('4th photo is blocked', upload(url, citizen), 400)
r = check('incident shows its images', requests.get(url + '/', headers=citizen), 200)
print('    images on incident:', len(r.json()['images']))

# 6. resolving
check('Ramesh cannot resolve (hidden)', requests.post(f'{url}/resolve/', headers=ramesh), 404)
check('citizen cannot resolve', requests.post(f'{url}/resolve/', headers=citizen), 403)
check('no token gives 401', requests.post(f'{url}/resolve/'), 401)
check('Arati resolves', requests.post(
    f'{url}/resolve/', headers=arati, json={'note': 'Patient taken to hospital'}), 200)
check('cannot resolve twice', requests.post(f'{url}/resolve/', headers=arati), 400)
check('cannot add workers after resolved', requests.post(
    f'{url}/add-workers/', headers=r2, json={'worker_ids': [ARATI]}), 400)
check('no photos after resolved', upload(url, citizen), 400)

# 7. history
r = check('history', requests.get(f'{url}/updates/', headers=r2), 200)
for row in reversed(r.json()):
    print('    ', row['old_status'], '->', row['new_status'], '|', row['updated_by_name'], '|', row['note'])

# 8. sorting
r = check('sort by urgency', requests.get(f'{BASE}/incidents/?sort=urgency', headers=admin), 200)
print('    order:', [(i['title'], i['urgency']) for i in r.json()['results']])