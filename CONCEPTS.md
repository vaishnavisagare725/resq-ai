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





## Day 2: Django project + MySQL

### 1. Framework
- A ready-made house frame. Login, database access, and admin already exist, and I add my rooms.
- Remember: *Django gives the frame, I build the rooms.*

### 2. Project vs App
- **Project** = the whole website (`config/`).
- **App** = one feature (`accounts`, `incidents`).
- Remember: *project is the building, apps are the rooms.*

### 3. MVT pattern
- **Model** = data (tables). **View** = logic (what happens on a request). **Template** = HTML.
- In ResQ AI, React replaces the Template, so Django only returns JSON.
- Remember: *Model stores, View decides, Template shows.*

### 4. manage.py and settings.py
- **manage.py** = my command remote (`runserver`, `migrate`, `createsuperuser`).
- **settings.py** = control panel (apps, database, security).
- Remember: *manage.py gives orders, settings.py holds the rules.*

### 5. INSTALLED_APPS
- Django only knows the features listed here.
- Forgetting to add an app here is the most common beginner bug.
- Remember: *not in the list, not in the project.*

### 6. Middleware
- Code that every request passes through, like airport security.
- `CorsMiddleware` goes first so it can add CORS permission headers.
- Remember: *every request walks through the checkpoints.*

### 7. CORS
- The browser blocks React (port 5173) from calling Django (port 8000) unless Django allows it.
- Fix: `CORS_ALLOWED_ORIGINS = ['http://localhost:5173']`.
- Remember: *different port = different origin = needs permission.*

### 8. Database connection in settings
- ENGINE = which database type. NAME, USER, PASSWORD = which database and who I am.
- HOST and PORT = address of MySQL (this computer, 3306).
- All secrets come from `.env` through `os.getenv`.
- Remember: *settings say where, .env says the password.*

### 9. ORM
- I write Python classes, Django writes the SQL.
- Class = table, field = column, object = row.
- Remember: *Python in, SQL out.*

### 10. Migrations
- **makemigrations** = write the plan. **migrate** = build it in MySQL.
- Migration files are version control for my database structure.
- Remember: *makemigrations plans, migrate builds.*

### 11. Custom User model
- `AbstractUser` = Django's ready-made user. I inherit it and add `role` and `phone`.
- `AUTH_USER_MODEL = 'accounts.User'` must be set BEFORE the first migrate.
- Changing it later breaks the database.
- Remember: *choose the user model first, before building tables.*

### 12. Roles
- My own `role` field: citizen, responder, admin. My API permissions will check it.
- `is_superuser` = Django's "can do everything in admin" flag.
- `is_staff` = can log in to `/admin/`.
- Remember: *role is mine, is_superuser is Django's.*

### 13. Primary key
- Each row's unique ID number. Django adds `id` automatically.
- `BigAutoField` holds far more rows than `AutoField`.
- Set `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`.
- Remember: *primary key = a row's ID card.*

### 14. Admin panel
- Free dashboard at `/admin/` to view and edit data.
- `createsuperuser` makes the first admin account.
- I registered my User in `admin.py` so `role` and `phone` show up.
- Remember: *admin = free control room for my data.*

### 15. Version compatibility (my real bug)
- Error: `MySQL 8.4 or later is required (found 8.0.44)`.
- Cause: Django 6.1 needs MySQL 8.4+, mine was 8.0.
- Fix: `pip install "Django>=5.2,<5.3"`, then update `requirements.txt`.
- **LTS** = Long Term Support, a version that gets security fixes for years.
- Remember: *read the LAST line of an error first.*

### 16. Warning vs error
- **Warning** = works, but fix it. **Error** = stopped.
- Remember: *a warning is a yellow light, an error is a red light.*

## One-line summary of Day 2
Django (project + apps) now talks to MySQL through settings, my custom User table exists, and I can log in to the admin and manage users with roles.

## Interview answers to practise
1. **Project vs app?** The project is the whole site and its settings. An app is one reusable feature, like accounts or incidents.
2. **makemigrations vs migrate?** makemigrations writes migration files describing model changes. migrate applies them to the database.
3. **Why a custom user model at the start?** Django can't swap the user model cleanly after the first migration, and I wanted a `role` field.
4. **What does middleware do?** It processes every request and response, for security, sessions, authentication, and CORS.