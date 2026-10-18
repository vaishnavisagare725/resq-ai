# ResQ AI: Day 1 Notes (Simple Words)

## The big picture
Restaurant story:
- **Me at the table = Client** (React)
- **Kitchen = Server** (Django)
- **Storage room = Database** (MySQL)
- **Waiter = API** (carries orders and food)

## 1. Client and Server
- Client **asks**. Server **answers**.
- Server never speaks first.
- Remember: *Customer orders, kitchen cooks.*

## 2. IP, Domain, Port
- **IP** = house address of a computer
- **Domain** = the name instead of the number (google.com)
- **Port** = door number of the house
- My ports: Django 8000, React 5173, MySQL 3306
- Remember: *IP is the house, port is the door.*

## 3. HTTP Request and Response
- **Request** = my letter: what I want + extra info + data
- **Response** = their reply: result number + data
- Remember: *Letter goes, reply comes.*

## 4. HTTP Methods
| Method | Simple meaning |
|---|---|
| GET | Read (show me) |
| POST | Create (add new) |
| PATCH | Change a little |
| PUT | Replace everything |
| DELETE | Remove |
- Remember: *GET looks, the others change.*

## 5. Status Codes
- **2xx** = good (200 OK, 201 Created)
- **4xx** = my mistake (400 bad data, 401 not logged in, 403 not allowed, 404 not found)
- **5xx** = server's mistake (500 crashed)
- Remember: *2 = Yay, 4 = You, 5 = Server.*

## 6. 401 vs 403
- **401** = "Who are you?" (not logged in)
- **403** = "I know you, but you can't do this" (no permission)
- Remember: *401 = no ticket. 403 = ticket is wrong for this room.*

## 7. JSON
- Text format for sharing data. Looks like a Python dictionary.
- `{"title": "Fire", "urgency": "critical"}`
- Why: React and Django speak different languages, JSON is the common language.
- Remember: *JSON = the shared language.*

## 8. API, Endpoint, REST
- **API** = the waiter (URLs that give or take data)
- **Endpoint** = one specific URL (`/api/incidents/`)
- **REST rule** = URL is the thing, method is the action
- `GET /incidents/` = list, `POST /incidents/` = add
- Remember: *Same URL, different method, different action.*

## 9. Stateless
- Server **forgets me** after every request.
- So I show my **token** every time (like showing my ID at every door).
- Remember: *Server has no memory, so carry the token.*

## 10. Virtual Environment (venv)
- A **private toolbox** for one project.
- Stops projects from clashing.
- Check: I see `(venv)` in the terminal.
- Remember: *One project, one toolbox.*

## 11. pip and requirements.txt
- **pip** = app store for Python packages
- **requirements.txt** = shopping list of my packages
- Remember: *pip installs, requirements.txt remembers.*

## 12. My Packages
| Package | One line |
|---|---|
| django | builds the website |
| djangorestframework | makes the API |
| mysqlclient | cable to MySQL |
| django-cors-headers | lets React talk to Django |
| simplejwt | login tokens |
| python-dotenv | reads secrets file |
| requests | calls other websites |

## 13. Git
- **Save game** for my code.
- `git add .` = pick what to save
- `git commit -m "message"` = save it
- `git status` = see what changed
- Remember: *add, commit, status.*

## 14. .gitignore
- **"Do not save" list.**
- Mine: `venv/`, `.env`, `__pycache__/`, `node_modules/`
- Remember: *Secrets and heavy stuff stay home.*

## 15. .env
- **Secret notebook** for passwords.
- Django reads it. Git ignores it.
- No spaces around `=`.
- Remember: *Passwords go in .env, never in code.*

## 16. Database
- **Permanent storage.** Data stays after shutdown.
- My database: `resq_ai` (empty until migrations).
- `utf8mb4` = supports every language and emoji.
- Remember: *Server restarts, database remembers.*

## One-line summary of Day 1
React asks, Django answers, MySQL remembers. They talk in HTTP, share JSON, and I prove who I am with a token.

## Interview answer: what happens when I press Enter on a URL?
1. DNS finds the server's address
2. Browser sends a GET request
3. Server replies with a status code and content
4. Browser shows the page
- Remember: *Find, ask, answer, show.*