"""Check the database connection from my laptop, step by step, without Django.

Set the same variables that Django uses (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD,
DB_NAME, DB_SSL_CA), then run:   python scripts\\check_db.py
"""
import os
import sys

import MySQLdb

host = os.environ.get('DB_HOST')
port = int(os.environ.get('DB_PORT', '3306'))
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')
name = os.environ.get('DB_NAME')
ca = os.environ.get('DB_SSL_CA')

missing = [key for key, value in (('DB_HOST', host), ('DB_USER', user),
                                  ('DB_PASSWORD', password), ('DB_NAME', name)) if not value]
if missing:
    sys.exit(f'These variables are not set: {", ".join(missing)}')

print(f'host     : {host}')
print(f'port     : {port}')
print(f'user     : {user!r}')
print(f'database : {name!r}')
print(f'password : {len(password)} characters')
print(f'           starts with AVNS_      = {password.startswith("AVNS_")}')
print(f'           spaces at the ends     = {password != password.strip()}')
print(f'           non-ASCII characters   = {sum(ord(c) > 127 for c in password)}')

options = dict(host=host, port=port, user=user, password=password, database=name, connect_timeout=15)
if ca:
    print(f'CA file  : {ca}')
    print(f'           exists = {os.path.exists(ca)}')
    if not os.path.exists(ca):
        sys.exit('\nThe CA file path is wrong. Fix DB_SSL_CA first: nothing else can work without TLS.')
    options['ssl'] = {'ca': ca}
else:
    print('CA file  : (not set, so the connection will NOT be encrypted)')

HINTS = {
    1045: 'Wrong user or password, OR the server requires TLS and this connection had none.',
    2003: 'Cannot reach the server: wrong host or port, or the service is powered off.',
    2026: 'A TLS problem: the CA file is not the right one for this service.',
    1049: 'The database name does not exist.',
}

try:
    connection = MySQLdb.connect(**options)
except MySQLdb.OperationalError as error:
    code = error.args[0]
    print(f'\nFAILED: {error}')
    print(f'Hint  : {HINTS.get(code, "Look the code up in the MySQL error list.")}')
    sys.exit(1)

cursor = connection.cursor()
cursor.execute('SELECT VERSION()')
print(f'\nserver version : {cursor.fetchone()[0]}')
cursor.execute("SHOW STATUS LIKE 'Ssl_cipher'")
cipher = cursor.fetchone()[1]
print(f'TLS cipher     : {cipher or "(none: this connection is NOT encrypted)"}')
cursor.execute('SELECT @@character_set_database')
print(f'character set  : {cursor.fetchone()[0]}')
connection.close()
print('\nConnection OK')