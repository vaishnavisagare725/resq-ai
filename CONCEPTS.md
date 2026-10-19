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






---

## Day 3: Models and the ORM (Simple Words)

### 1. ORM
- **Python class = table. Field = column. Object = row.**
- I write Python, Django writes the SQL.
- Remember: *Python in, SQL out.*

### 2. Field types
| Field | Stores |
|---|---|
| CharField | short text (title) |
| TextField | long text (description) |
| FloatField | decimals (latitude) |
| DateTimeField | date and time |
- Remember: *Char is short, Text is long.*

### 3. Choices
- A field that only accepts a fixed list (low, medium, high, critical).
- Stops typos and makes a dropdown in the admin.
- Remember: *choices = a menu, not free typing.*

### 4. default, null, blank
- **default** = value used if I give none.
- **null=True** = the database may store empty.
- **blank=True** = the form may be left empty.
- Optional ForeignKey needs both.
- Remember: *null is for the database, blank is for the form.*

### 5. auto_now_add vs auto_now
- **auto_now_add** = set once, when created.
- **auto_now** = updated on every save.
- Remember: *add = birth time, now = last-changed time.*

### 6. ForeignKey
- A link to a row in another table. **One user, many incidents.**
- In MySQL it is a number column: `reporter_id`.
- Remember: *a ForeignKey is a name tag pointing to another table.*

### 7. on_delete
| Option | What happens when the user is deleted |
|---|---|
| CASCADE | their incidents are deleted too |
| SET_NULL | incidents stay, the link becomes empty |
| PROTECT | deletion is refused |
- I use CASCADE for `reporter`, SET_NULL for `assigned_to`.
- Remember: *CASCADE = chain delete, SET_NULL = keep the data.*

### 8. related_name
- Lets me walk backwards: `citizen.reports.all()`.
- Two ForeignKeys to the same table need different related_names.
- Remember: *forward: incident.reporter. Backward: citizen.reports.*

### 9. AUTH_USER_MODEL
- In models, point to the user with `settings.AUTH_USER_MODEL`, never import User directly.
- Remember: *always ask settings who the user is.*

### 10. __str__ and Meta
- **__str__** = how an object looks in the admin and shell.
- **Meta ordering = ['-created_at']** = newest first by default.
- Remember: *__str__ is the name tag, Meta is the sort rule.*

### 11. CRUD in the ORM
| Action | Code |
|---|---|
| Create | `Incident.objects.create(...)` |
| Read | `.get()`, `.filter()`, `.all()` |
| Update | change the field, then `.save()` |
| Delete | `.delete()` |
- Remember: *nothing is saved until .save().*

### 12. get vs filter
- **get()** = exactly one row (error if none or many).
- **filter()** = a list of rows (can be empty).
- Remember: *get = one, filter = many.*

### 13. Useful filters
- `filter(urgency='critical')` = matches
- `exclude(status='resolved')` = everything except
- `description__icontains='fire'` = contains, ignoring capitals
- `urgency__in=['high','critical']` = one of these
- `order_by('-created_at')` = newest first
- Remember: *double underscore = a special condition.*

### 14. QuerySet is lazy
- A QuerySet is a recipe. MySQL is only asked when I read the results.
- `print(qs.query)` shows the real SQL.
- Remember: *recipe first, cooking later.*

### 15. N+1 problem
- 1 query for the list + 1 extra query for every row's related object.
- 100 incidents = 101 queries. Slow.
- Fix: **select_related('reporter')** joins the tables in one query.
- **prefetch_related** is for reverse and many-to-many links.
- My test: bad = 4 queries, good = 1 query.
- Remember: *N+1 = asking one by one. select_related = asking all at once.*

### 16. Aggregation
- `values('urgency').annotate(total=Count('id'))` = GROUP BY in Python.
- The dashboard will use it.
- Remember: *values groups, annotate counts.*

### 17. create_user
- `create_user()` hashes the password. `create()` would store it as plain text.
- Remember: *always create_user for passwords.*

## One-line summary of Day 3
I turned a Python class into the `incidents_incident` table, linked it to users with ForeignKeys, and read and changed the data with Python instead of SQL.

## Interview answers to practise
1. **What is an ORM?** It maps classes to tables and objects to rows, so I write Python and the framework generates SQL. It is faster to build with and safer against SQL injection, but complex queries can be harder to optimise.
2. **filter vs get?** `get` returns exactly one object and raises an error if there are none or several. `filter` returns a QuerySet that can hold zero or many.
3. **What is the N+1 problem?** One query for a list plus one extra query per row to load a related object. I fix it with `select_related` for ForeignKeys or `prefetch_related` for reverse and many-to-many relations.
4. **What does on_delete do?** It decides what happens to child rows when the parent is deleted: CASCADE deletes them, SET_NULL keeps them with an empty link, PROTECT blocks the delete.
5. **What does lazy mean?** A QuerySet does not hit the database until I iterate, slice, or count it, so I can chain filters cheaply.





---

## Day 4: History, Validation, Indexes (Simple Words)

### 1. History (audit) table
- The main table stores the **present**. The history table stores the **diary**.
- My `IncidentUpdate` table records: which incident, who changed it, old status, new status, and when.
- Emergency systems need this for accountability.
- Remember: *main table = now, history table = diary.*

### 2. Why SET_NULL on updated_by
- If a responder's account is deleted, the history must stay. Only the "who" becomes empty.
- The incident link uses CASCADE, because history without its incident is useless.
- Remember: *a diary outlives the writer's account.*

### 3. Latitude and longitude
- **Latitude** = north-south, range **-90 to 90**.
- **Longitude** = east-west, range **-180 to 180**.
- Pune is about 18.5, 73.8. `latitude=200` is impossible.
- Remember: *latitude is up-down (90), longitude is left-right (180).*

### 4. Validators
- Rules on a field that reject bad values (`MinValueValidator`, `MaxValueValidator`).
- They run in `full_clean()`, admin forms, and DRF serializers.
- They do **not** run on `save()` or `create()`.
- That is why the API serializer must validate input on Day 5.
- Remember: *validators guard the front door, not the back door.*

### 5. Database index
- Like the index at the back of a book.
- Without it, MySQL reads every row. With it, MySQL jumps to the matching rows.
- **Pro:** fast filtering and sorting. **Con:** extra space and slightly slower writes.
- Index columns I filter or sort by: `status`, `urgency`, `created_at`.
- Remember: *index = fast reading, slower writing.*

### 6. Model method and @property
- Put small logic on the model, next to the data.
- `@property is_open` is read like a field: `incident.is_open` (no brackets).
- Remember: *logic lives next to its data.*

### 7. transaction.atomic
- Several database writes that **all succeed or all fail**.
- In `change_status`, the status update and the history row must happen together.
- Remember: *atomic = all or nothing.*

### 8. Admin inline
- Shows related rows (the history) inside the parent's page.
- I made it read-only so nobody edits the history by hand.
- Remember: *one screen tells the whole story.*

### 9. list_select_related
- The admin's version of `select_related`.
- Stops the admin list from running N+1 queries.
- Remember: *same N+1 cure, inside the admin.*

### 10. Admin action
- A bulk operation from the list page (my "Mark selected as resolved").
- It calls `change_status`, so every resolve is written to the history.
- Remember: *one click, many rows, still recorded.*

### 11. Reusing choices
- `IncidentUpdate` uses `Incident.Status.choices`, so both tables share one list of statuses.
- Remember: *define once, reuse everywhere.*

## One-line summary of Day 4
Every status change is now recorded in a history table, bad data is validated, searches are indexed, and the admin shows each incident's story.

## Interview answers to practise
1. **What is a database index?** A data structure that lets the database find rows without scanning the whole table. It speeds up filters and sorting, but costs extra space and makes inserts and updates slightly slower.
2. **Do model validators run on save()?** No. They run on `full_clean()`, in model forms, and in DRF serializers. So API input must be validated in the serializer.
3. **Why a separate history table?** The main row only holds the current state. A history table keeps who changed what and when, which gives accountability and lets me rebuild the timeline.
4. **What does transaction.atomic do?** It groups several database writes so they either all commit or all roll back, so I never end up with a status changed but no history row.
5. **Why SET_NULL on updated_by but CASCADE on incident?** History should survive a deleted user, but it makes no sense without the incident it belongs to.