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
5. **Why SET_NULL on updated_by but CASCADE on incident?** History should survive a deleted user, but it makes no sense without the incident it belongs to.\



## Day 5: REST API with DRF
- Serializer = translator + validator. read_only_fields = the server decides (urgency, status, reporter, department).
- Nested serializer: workers returned as {id, username, department}.
- ViewSet + Router = list/create/read and auto URLs.
- get_queryset: citizen = own, worker = assigned, responder = own department + unrouted (Q object), admin = all. Real security.
- select_related (ForeignKey JOIN) and prefetch_related (many-to-many, 1 extra query) avoid N+1.
- Basic auth is temporary; JWT on Day 6.
- Day 7: Django's ValidationError from assign_* is NOT turned into a 400 by DRF automatically. The API must catch it.





## Day 6: JWT Authentication (Simple Words)

### 1. Authentication vs authorization
- **Authentication** = who are you? **Authorization** = what may you do?
- Remember: *login first, permission second.*

### 2. Stateless and tokens
- HTTP forgets me after every request, so each request carries proof.
- The proof is a **token**.
- Remember: *the token is my wristband.*

### 3. Session vs token
| | Session | Token (JWT) |
|---|---|---|
| Login remembered on | the server | the client |
| Sent as | cookie | `Authorization: Bearer <token>` |
| Best for | server-rendered sites | React, mobile apps, APIs |
- Remember: *sessions for websites, tokens for APIs.*

### 4. JWT = header.payload.signature
- **Payload** holds `user_id`, `role`, `exp` (expiry).
- **Signature** is made with `SECRET_KEY`. Changing the payload breaks it, so it cannot be forged.
- **Signed, not encrypted**: anyone can read the payload. No secrets inside.
- Remember: *a JWT is a signed ID card: unforgeable, but readable.*

### 5. Access vs refresh token
- **Access** = short (30 min), used on every request.
- **Refresh** = longer (1 day), used only to get a new access token.
- If an access token leaks, it dies soon.
- Remember: *access opens doors, refresh gets a new key.*

### 6. Bearer header
- `Authorization: Bearer <access token>` (a space after Bearer).
- Remember: *Bearer + space + token.*

### 7. Never trust the role inside the token
- The token carries `role` only as a convenience for React.
- The backend loads the user from the **database**, so `request.user.role` is always current.
- Remember: *the database is the truth, the token is a note.*

### 8. Safe registration
- The register serializer has **no role or department field**.
- Extra keys in the request are ignored. New accounts are always **citizens**.
- Responders and workers are created by an admin.
- Remember: *nobody registers themselves as admin.*

### 9. Passwords
- `write_only` = accepted, never returned.
- `create_user` hashes it. The database shows `pbkdf2_sha256$...`.
- `validate_password` applies Django's rules (not too short, not too common, not all numbers).
- Remember: *hash it, never store it plain.*

### 10. /api/auth/me/
- Tells React who is logged in (username, role, department).
- It never takes an id from the URL. It uses `request.user`.
- Remember: *me = the person holding this token.*

### 11. 401 vs 403
- **401** = no valid token ("who are you?").
- **403** = valid token, not allowed.
- Remember: *401 = no ticket, 403 = wrong ticket.*

### 12. A JWT cannot be cancelled early
- Once issued, it is valid until it expires.
- That is why access tokens are short-lived. A blacklist can revoke refresh tokens.
- Remember: *short life = small damage.*

### 13. SECRET_KEY
- It signs every token. A guessable key means forged tokens.
- Use a long random key, keep it in `.env`, and never commit it.
- Remember: *the secret key is the stamp that signs tokens.*

### 14. ModelSerializer copies model rules
- Unique username gave a 400 `A user with that username already exists` with no code from me.
- Remember: *the model's rules travel to the serializer.*

## One-line summaries
- **Day 5:** the API shows each role only its own incidents, departments route the work, and one rule per action keeps the data clean.
- **Day 6:** users register safely, log in for tokens, and send `Bearer` tokens so the server knows who they are on every request.

## Interview answers to practise
1. **Why override get_queryset?** It decides which rows each user may see. Without it, any logged-in citizen could read everyone's reports.
2. **select_related vs prefetch_related?** `select_related` uses a JOIN for ForeignKeys. `prefetch_related` runs one extra query for many-to-many or reverse relations. Both avoid N+1.
3. **Why 404 for a hidden incident?** A 403 would confirm it exists. The queryset hides it, so the API says not found.
4. **Why one method for assigning workers?** The admin, the shell, and the API all need the same rule, and `workers.add()` or `save()` would skip it. The method checks first, then writes inside a transaction.
5. **Session vs token authentication?** Sessions keep the login on the server and use cookies, which suits server-rendered sites. Tokens are sent in a header and suit React and mobile apps.
6. **What is a JWT?** Three parts: header, payload, and a signature made with the secret key. It is signed, not encrypted, so anyone can read it, but nobody can change it without the key.
7. **Why access and refresh tokens?** The access token is short-lived, so a leak causes little harm. The refresh token is used only to get new access tokens.
8. **Why must register ignore role?** Otherwise anyone could register as an admin. The serializer doesn't include role, so new accounts are always citizens.
9. **401 vs 403?** 401 means not authenticated. 403 means authenticated but not allowed.




---

## Day 7: Permissions, Actions, Images (Simple Words)

### 1. Two levels of permission
- **has_permission** = may this KIND of user use this endpoint? (a citizen can't take a case)
- **has_object_permission** = is it MY incident? (only the assigned responder manages workers)
- Remember: *has_permission is the door, has_object_permission is the room.*

### 2. The order DRF checks things
1. Token valid? No = **401**
2. Right role (`has_permission`)? No = **403**
3. Can I even see this incident (`get_queryset`)? No = **404**
4. Is it mine (`has_object_permission`)? No = **403**
- Remember: *401, 403, 404, 403: who, what kind, visible, mine.*

### 3. Custom actions (@action)
- One endpoint per business step: `take`, `add-workers`, `remove-workers`, `resolve`, `images`, `updates`.
- Better than one generic PATCH, because each step has its own rules and a PATCH lets clients set any field.
- Remember: *one button, one endpoint, one rule.*

### 4. Input serializers
- Validate request bodies that are not models: `{"worker_ids": [4]}`.
- Empty lists and non-numbers are rejected with a 400.
- Remember: *validate every request body.*

### 5. Reuse the model methods
- The API calls `assign_responder`, `assign_workers`, `change_status`, the same ones the admin and shell use.
- One rule and one history diary for everyone.
- Remember: *one rule, one door.*

### 6. Exception handler
- Django's `ValidationError` would be a 500 in DRF. One handler turns it into a clean 400.
- Remember: *handle the error once, in one place.*

### 7. _fresh()
- Reload the incident after a change so the response shows the new workers, images, and status.
- Remember: *reload before you reply.*

### 8. Locked when resolved
- `_ensure_open()` blocks taking, adding or removing workers, and photos after an incident is resolved.
- Remember: *resolved means finished.*

### 9. Sorting by urgency
- Text sorting gives the wrong order (alphabetical). `annotate` + `Case/When` gives each urgency a rank.
- `?sort=urgency` puts critical first.
- Remember: *rank it, don't alphabetise it.*

### 10. Filters
- `?status=`, `?urgency=`, `?department=`, `?q=fire` (search text).
- Remember: *the URL carries the filters.*

### 11. CORS
- The browser blocks React (port 5173) from calling Django (port 8000) unless Django allows it.
- Remember: *different port = different origin = needs permission.*

### 12. Images: files are not in MySQL
- The database stores the **path**. The file lives in `media/`.
- `MEDIA_ROOT` = where files are saved. `MEDIA_URL` = the URL prefix.
- Remember: *database holds the address, the folder holds the picture.*

### 13. ImageField and Pillow
- `ImageField` uses Pillow to check the upload is really an image.
- A text file renamed `.jpg` is rejected.
- Remember: *check the content, not the name.*

### 14. multipart/form-data
- Files can't go in JSON. The request is multipart, and the form field is named `image`.
- Remember: *JSON for data, multipart for files.*

### 15. Safe uploads
- Random `uuid` file names stop overwrites and guessable URLs. Never use the client's file name.
- Limits: 5 MB each, 3 per incident. The server sets `incident` and `uploaded_by`.
- Remember: *never trust the client's file or its name.*

### 16. Limits to mention in an interview
- Image URLs are public by link (random names, but not private).
- Files stay on disk when a row is deleted.
- Hosting disks are temporary, so production needs cloud storage.
- Photos can carry GPS data, which is a privacy concern.
- Remember: *it works, and I know where it is weak.*

## One-line summary of Day 7
The API now runs the whole emergency workflow (take, add workers, photos, resolve) with the right person allowed at each step, and every change is recorded.

## Interview answers to practise
1. **has_permission vs has_object_permission?** The first decides whether this kind of user may use the endpoint at all. The second decides whether they may act on this specific object.
2. **Why 404 and not 403 for a hidden incident?** `get_object` searches inside `get_queryset`, so a hidden incident is simply not found. A 403 would confirm it exists.
3. **Why custom @actions and not PATCH?** Each workflow step has its own rules, history entry, and allowed users. A generic PATCH lets the client set any field.
4. **How do you turn a Django ValidationError into a 400?** A custom exception handler registered in `REST_FRAMEWORK['EXCEPTION_HANDLER']`.
5. **Where is an uploaded image stored?** In the `media` folder on disk. The database stores only the file path.
6. **How do you stop a fake image?** `ImageField` verifies the content with Pillow, and the serializer checks the size.







---

## Day 8: AI Triage (Simple Words)

### 1. Service layer
- The AI logic lives in its own file, `ai_service.py`. The view only calls `predict()`.
- I can replace the AI later without touching the API.
- Remember: *views ask, the service answers.*

### 2. Pure function
- `predict(title, description)` takes text and returns a dictionary. It imports nothing from Django and touches no database.
- Easy to test, easy to replace.
- Remember: *same input, same output, no side effects.*

### 3. Rule-based AI vs machine learning
| | Rule-based (mine) | Machine learning |
|---|---|---|
| Decides by | keyword rules I wrote | patterns learned from labelled examples |
| Explains itself | yes, it lists the matched words | hard |
| Needs data | no | yes, hundreds of labelled reports |
| New wording | poor | better |
- I started with rules because I had no data and I want explainable decisions.
- Remember: *start with rules I can explain, upgrade when I have data.*

### 4. Weighted scoring
- Every category keyword has a weight (`collided` = 3, `injured` = 1). The highest total wins. A tie uses a priority order.
- "Two bikes collided, one injured" is an accident (3), not medical (1).
- Remember: *strong words count more.*

### 5. Whole-word matching
- The regex `\b` marks a word boundary, so `fire` does not match `fireplace` and `burn` does not match `burning`.
- Remember: *match words, not letters.*

### 6. Negation
- A phrase is skipped when `no`, `not`, `without`, `never`, `false`, or `no one is` comes right before it. ("No fire, just toast" is not a fire.)
- It is deliberately narrow: "not sure, but there is smoke" still counts.
- Remember: *a missed emergency is worse than a false alarm.*

### 7. Raisers
- A child, an elderly person, or "many people" raises a medium or high report by one level.
- Remember: *vulnerable people move the urgency up.*

### 8. Explainability
- The AI saves why in `ai_reason`: "urgency critical from: fire, trapped".
- Remember: *the AI shows its work.*

### 9. needs_review
- True when the AI found nothing useful (category `other`). Those reports have no department, so every responder sees them.
- Remember: *when the AI is unsure, a human decides.*

### 10. The server decides, the client doesn't
- `perform_create` sets urgency, category, department, `ai_reason`, and `needs_review` from the AI.
- A citizen who sends `"urgency": "critical"` is ignored, because those serializer fields are read-only.
- Remember: *the client can't pick its own priority.*

### 11. Human in the loop: /triage/
- The AI suggests. A responder corrects urgency or category. The department is re-routed and the change goes into the history diary.
- **CanTriage:** responders and admins only. An untaken incident can be triaged by any responder who sees it. A taken one only by its owner or an admin.
- A taken incident's department can't change.
- Remember: *the AI suggests, the human decides.*

### 12. Check first, then write
- `triage()` validates everything, then writes inside `transaction.atomic()`. A rejected request changes nothing.
- Remember: *a failed attempt leaves no mess.*

### 13. False negative vs false positive
- False negative: a real emergency judged low. Dangerous.
- False positive: a harmless report judged high. Costs time.
- The rules lean towards raising urgency.
- Remember: *when in doubt, raise it or send it to a human.*

### 14. Unit tests
- A table of 16 example reports with the expected result, run with `python manage.py test incidents`.
- `SimpleTestCase` needs no database. `subTest` names the failing example.
- Remember: *every rule change must keep the examples green.*

### 15. Management command
- `python manage.py ai_backfill` re-checks old data. It never overrides human choices.
- Remember: *a command is a script that knows my project.*

### 16. Limits (be honest in an interview)
- English only. A Marathi report goes to the review queue.
- Keywords miss new wording and spelling mistakes.
- One category per report (a crash with an unconscious victim needs two teams).
- No accuracy figure yet, because there is no real labelled data. A real system measures precision and recall.
- Remember: *it works, and I know exactly where it is weak.*

## One-line summary of Day 8
New reports are triaged by an explainable rule engine that sets urgency, category, and department, and responders can correct it, with every correction recorded.

## Interview answers to practise
1. **Why a service layer?** The AI logic is isolated, testable, and replaceable, and the API doesn't change when the AI does.
2. **Why rules before ML?** I had no labelled data, rules are explainable and testable, and the same function interface lets me swap in a trained model later.
3. **How does it handle "no fire"?** It skips a phrase preceded by a negation word. The rule is narrow on purpose, so a real emergency isn't missed.
4. **False negatives vs false positives?** In an emergency system a missed emergency is worse, so the rules lean towards raising urgency and sending unclear reports to humans.
5. **Why can't a citizen set their own urgency?** The AI fields are read-only on the serializer, and `perform_create` sets them on the server.
6. **Why a triage endpoint?** AI should assist, not decide. A responder can correct it, and the correction is recorded in the history.
7. **How would you evaluate the AI?** Collect labelled reports, then measure precision and recall per urgency level, with extra weight on recall for critical.





---

## Day 9: React Frontend (Simple Words)

### 1. SPA and Vite
- A single-page app loads once, then React redraws parts and calls the API. No full reloads.
- **Vite** = the dev server (instant refresh) and the bundler for production.
- Remember: *load once, then talk to the API.*

### 2. npm, package.json, node_modules
- `package.json` = the shopping list of JS packages. `node_modules/` = the downloaded packages (huge, in .gitignore).
- Anyone recreates it with `npm install`.
- Remember: *commit package.json, never node_modules.*

### 3. Component, JSX, props, state
- A component is a function that returns what to draw. JSX is HTML-looking code inside JavaScript.
- **Props** come in (read-only). **State** (`useState`) lives inside, and changing it redraws.
- Remember: *props come in, state lives inside.*

### 4. useEffect
- Runs after a render, e.g. fetch data when the page opens. The dependency array says when to re-run.
- Cleanup + a `cancelled` flag stop a slow answer from updating a page I already left.
- StrictMode runs effects twice in development, so I may see two requests. Production does not.
- Remember: *effects talk to the outside world.*

### 5. Controlled form
- Each input's value lives in state, and `onChange` updates it.
- Remember: *React always knows what is typed.*

### 6. React Router
- `<Routes>/<Route>` map URLs to pages. `<NavLink>` navigates. `<Navigate>` redirects. `useLocation` says where I am.
- Remember: *URL in, component out.*

### 7. Axios instance and interceptors
- One shared client with the base URL.
- **Request interceptor:** adds `Authorization: Bearer <token>` to every call.
- **Response interceptor:** on 401 it asks `/auth/refresh/` for a new access token, retries the original call once, and logs out if the refresh fails.
- A shared `refreshing` promise makes several simultaneous 401s trigger only one refresh.
- Remember: *the interceptor renews the token so the user never notices.*

### 8. Context API
- `AuthProvider` holds the user. `useAuth()` reads it anywhere, with no prop drilling.
- Remember: *provider holds it, hook reads it.*

### 9. Loading state
- With a stored token I must ask `/auth/me/` who it is. Until then show "Loading" and do not redirect.
- Remember: *don't redirect before I know who the user is.*

### 10. Protected route
- Redirects visitors who aren't logged in or have the wrong role.
- It is a **convenience, not security**. The real rules live in Django permissions.
- Remember: *React hides buttons, Django enforces rules.*

### 11. Where to store the JWT
- localStorage: simple, but injected JavaScript (XSS) could read it.
- In memory: safer, lost on refresh.
- httpOnly cookie: JavaScript can't read it, but needs CSRF protection.
- My MVP uses localStorage with a 30-minute access token.
- Remember: *short-lived access tokens limit the damage.*

### 12. Vite environment variables
- Names start with `VITE_`. They are baked into the public bundle, so never put secrets there.
- Remember: *VITE_ means public.*

### 13. CORS (again)
- The browser enforces it, and the server permits it. Django allows `http://localhost:5173`.
- Remember: *the browser asks, the server says yes.*

### 14. Debugging with DevTools
- Network tab: request headers, status, response. Application tab: Local Storage.
- Test the renewal by setting `access` to `broken` and refreshing.
- Remember: *the Network tab shows the truth.*

## One-line summary of Day 9
A React app now registers and logs users in, sends the JWT on every call, renews it automatically, and shows each role its own menu and its own incidents from the Django API.

## Interview answers to practise
1. **Props vs state?** Props are inputs passed from a parent and are read-only. State is data a component owns, and changing it re-renders.
2. **What does the dependency array in useEffect do?** It lists the values the effect depends on. The effect re-runs only when one changes, and an empty array means run once after the first render.
3. **How does your token refresh work?** A response interceptor catches a 401, calls the refresh endpoint once, stores the new access token, retries the original request, and logs out if the refresh fails.
4. **Is a ProtectedRoute secure?** No. It only improves the experience. Anyone can change browser code, so the API enforces permissions.
5. **Where do you store a JWT and what are the risks?** localStorage, which XSS could read. The alternatives are memory or an httpOnly cookie with CSRF protection. I limit the damage with a 30-minute access token.
6. **What is CORS?** A browser rule that blocks a page from calling another origin unless that server allows it. Django allows the React origin.

- "LF will be replaced by CRLF" is a Windows line-ending notice, not an error. Check git status for the real file list.
- Vite's package.json and package-lock.json are committed. node_modules is not, because anyone recreates it with npm install.





---

## Day 10: Citizen Pages (Simple Words)

### 1. Geolocation API
- `navigator.geolocation.getCurrentPosition(success, failure, options)` asks the browser for my position, after the user gives permission.
- Works only on `https://` or `localhost`. Always give a fallback: typing the coordinates.
- Error codes: 1 denied, 2 unavailable, 3 timeout.
- Remember: *ask permission, and always have a fallback.*

### 2. FormData vs JSON
- JSON carries text. Files need `multipart/form-data`, which `FormData` builds.
- Don't set Content-Type myself, because the browser adds the boundary.
- Remember: *JSON for data, FormData for files.*

### 3. Two requests: create, then upload
- First `POST /incidents/` (JSON). Then one `POST /incidents/<id>/images/` per photo.
- Photos upload one at a time.
- Remember: *the report first, the photos second.*

### 4. Partial failure
- If the report is saved but a photo fails, say "report received, 1 photo not uploaded" and offer Retry.
- Never throw the saved report away.
- Remember: *the important part succeeded, so keep it and retry the rest.*

### 5. Client-side validation is only UX
- The browser checks title, length, and coordinate ranges for instant feedback.
- The server validates everything again, because anyone can bypass the browser.
- Remember: *the browser is polite, the server is the guard.*

### 6. Object URLs
- `URL.createObjectURL(file)` makes a temporary preview address. `URL.revokeObjectURL` frees the memory.
- I revoke them in an effect cleanup.
- Remember: *every object URL needs a revoke.*

### 7. Custom hook: useFetch
- A reusable function that wraps state and effects, and exposes `data`, `error`, `status`, `loading`, `reload`.
- Each answer is stored with the key of the request that made it, so a stale answer is ignored.
- Remember: *a hook packages logic I would otherwise copy.*

### 8. Pagination in the UI
- DRF returns `count`, `next`, `previous`, `results` (20 per page). The page lives in state and goes into the request as `?page=2`.
- A new filter resets the page to 1.
- Remember: *change the filter, go back to page 1.*

### 9. 404 means "not found or no access"
- Opening someone else's report returns 404 from `get_queryset`. The page says so without confirming it exists.
- Remember: *the UI shows what the backend decides.*

### 10. Controlled form with one state object
- One `form` object and one `update` handler that uses `name`.
- Remember: *one state, one handler, many fields.*

### 11. The AI result screen
- After submit, the citizen sees the urgency, category, department, and the AI's reason, or "a responder will review it".
- Remember: *show the AI's work to the user too.*

### 12. Accessibility basics
- Every input has a label, every image has alt text, and icon buttons have `aria-label`.
- Remember: *build it so everyone can use it.*

### 13. A safety notice
- The report page tells people to call the emergency number first. The app helps responders prioritise, and doesn't replace the call.
- Remember: *software supports an emergency, it doesn't replace one.*

### 14. Privacy detail
- Photos can carry GPS data and are public by link. Citizens can also see the history notes of their own report.
- Remember: *every feature has a privacy question.*

## One-line summary of Day 10
A citizen can report an emergency with their location and photos, see how the AI judged it, and follow every report in a paged list and a detail page with photos and history.

## Interview answers to practise
1. **How do you upload a file with a form?** Build a `FormData`, append the file under the field name the server expects, and POST it. The browser sets the multipart boundary, so I don't set Content-Type.
2. **What if the report saves but a photo fails?** I keep the report, tell the user which photos failed, and offer to retry only those.
3. **How does geolocation work, and what can go wrong?** The browser asks for permission, then returns coordinates. It can be denied, unavailable, or time out, and it needs HTTPS or localhost, so I offer manual entry.
4. **What is a custom hook?** A function starting with `use` that packages state and effects. My `useFetch` loads data and ignores stale answers.
5. **Why validate in both browser and server?** The browser gives instant feedback, but only the server can be trusted.
6. **How do you avoid memory leaks with image previews?** `URL.createObjectURL` allocates memory, so I call `revokeObjectURL` in an effect cleanup.








---

## Day 11: Responder Dashboard (Simple Words)

### 1. Polling
- The browser asks again every 15 seconds. Simple and works everywhere. WebSockets or SSE push instantly but are more work.
- I skip polling when the tab is hidden (`document.hidden`).
- Remember: *polling is asking again and again, and it is good enough for an MVP.*

### 2. Stale-while-revalidate
- While a list reloads, keep showing the old data, so the screen never blinks empty.
- If a refresh fails, keep the last good data and show an error banner.
- Remember: *show something old while fetching something new.*

### 3. Race condition and row lock
- Two responders click Take at the same moment. Without protection both succeed and one silently overwrites the other.
- `select_for_update()` inside `transaction.atomic()` locks the row. The second request waits, sees "already taken", and gets a 400.
- The server decides who won, never the screen.
- Remember: *lock the row, then check, then write.*

### 4. Conditional aggregation
- `Count('id', filter=Q(status='open'))` counts several things in one query.
- The summary endpoint gives all five card numbers with one database call.
- Remember: *one query, many counts.*

### 5. The summary endpoint uses the same role rules
- `_visible()` is shared by the list and the summary, so a responder's cards match their list.
- Remember: *one rule in one place.*

### 6. Workers endpoint
- A responder gets only their own department's workers. An admin can filter. Citizens and workers get 403.
- `pagination_class = None`, because a picker needs a short plain list.
- Remember: *the picker only offers who the rules allow.*

### 7. UI permissions vs real permissions
- The page hides buttons the user can't use. The API still refuses if someone sends the request anyway.
- Remember: *the UI is convenience, the API is the guard.*

### 8. Custom hooks I wrote
- `useFetch` loads data, ignores stale answers, exposes `data`, `error`, `status`, `loading`, `updatedAt`, `reload`.
- `useAction` wraps an action with `busy` and `error`, so buttons don't repeat try/catch.
- Remember: *a hook packages logic I would otherwise copy.*

### 9. Router state: a flash message
- `navigate('/dashboard', { state: { flash: '...' } })` carries a one-time message to the next page.
- Remember: *router state travels with the navigation.*

### 10. Queue design
- Tabs (Open, In progress, Resolved, All), sort by urgency, clickable cards, a "needs review" marker.
- Every filter change goes back to page 1.
- Remember: *critical first, and unclear cases flagged.*

### 11. Re-routing after triage
- If triage moves an unrouted incident to another department, the responder can no longer see it. The app sends them back to the dashboard with a notice.
- Remember: *explain it when something disappears.*

### 12. Limits to mention in an interview
- Polling has up to 15 seconds of delay, and a real system would use WebSockets or SSE.
- A worker is not checked for being busy elsewhere.
- Cards count only what the role can see, by design.
- Remember: *it works, and I know the next step.*

## One-line summary of Day 11
A responder sees a live, urgency-sorted queue, takes cases without double-assignment, corrects the AI, assigns workers from their own department, and resolves, with every step in the history.

## Interview answers to practise
1. **How do you stop two responders taking the same incident?** I lock the row with `select_for_update()` inside a transaction, re-check `assigned_to`, and only then assign. The second request gets a 400.
2. **Why polling and not WebSockets?** Polling is simple and enough for an MVP. The cost is up to 15 seconds of delay. I'd move to WebSockets or server-sent events for instant updates.
3. **How do the summary cards get five numbers with one query?** Conditional aggregation: `Count('id', filter=Q(...))` per card, in one `aggregate()` call.
4. **What is stale-while-revalidate?** Keep showing the previous data while the new request is in flight, and keep it if the refresh fails.
5. **Why hide the Take button and also check on the server?** Hiding it improves the experience. The server check is the real security.
6. **Why does the cards' count match the list?** Both use the same `_visible()` role filter.