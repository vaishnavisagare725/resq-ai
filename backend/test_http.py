import requests

r = requests.get("https://jsonplaceholder.typicode.com/posts/1")
print(r.status_code)
print(r.json())

r2 = requests.get("https://jsonplaceholder.typicode.com/posts/99999")
print(r2.status_code)