"""Ask the API: would you accept a login request from my website?

    python scripts\\check_cors.py https://resq-ai-li3q.onrender.com https://MY-WEBSITE.onrender.com
"""
import sys

import requests

if len(sys.argv) != 3:
    sys.exit('Usage: python scripts\\check_cors.py <api address> <website address>')

api, website = (arg.rstrip('/') for arg in sys.argv[1:])
reply = requests.options(
    f'{api}/api/auth/login/',
    headers={
        'Origin': website,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type',
    },
    timeout=90,
)
allowed = reply.headers.get('access-control-allow-origin')
print('status         :', reply.status_code)
print('allowed origin :', allowed)
if allowed == website:
    print('\nOK: the API accepts requests from your website.')
else:
    print('\nFAIL: set CORS_ALLOWED_ORIGINS on the API service to exactly:', website)
    sys.exit(1)