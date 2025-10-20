## Task-Manager-API
AI‑assisted task management REST API built with Flask. It provides user authentication, CRUD for tasks, lightweight ML‑powered task categorization, priority suggestions, and hour estimates.

### Highlights
- **Authentication**: JWT-based register/login
- **Tasks CRUD**: Create, read, update, delete
- **AI analysis**: Category prediction, confidence score, priority suggestion, hour estimate
- **Filters & pagination**: Status/priority/category filters, sorting, pages/limits
- **Deadlines & tags**: ISO8601 deadlines, comma-separated tags stored as list in responses

### Tech stack
- **Backend**: Flask 2.3.x, Flask‑SQLAlchemy
- **Auth**: Flask‑JWT‑Extended
- **ML**: scikit‑learn (TF‑IDF + MultinomialNB)
- **DB**: SQLite by default (configurable via env var)
- **Security**: Werkzeug password hashing

---

## Getting started

### Prerequisites
- Python 3.10+

### Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration
Set environment variables as needed (defaults shown):

```bash
# REQUIRED in production – change this!
export JWT_SECRET_KEY="your-secret-key-change-in-production"

# Optional: override database (defaults to a local SQLite file)
export DATABASE_URL="sqlite:///task_database.db"
```

Notes:
- On first run, the database and tables are created automatically.
- The first import of the AI service will train a tiny model and save it to `models/task_classifier.pkl` (the `models/` folder is created if missing).

### Run the API
```bash
python app.py
```

Server starts on `http://127.0.0.1:5001`.

---

## API reference

Base URL: `http://127.0.0.1:5001`

Auth: Use `Authorization: Bearer <JWT>` for protected endpoints.

### Auth

- POST `/api/auth/register` — Create user
  - Body:
    ```json
    { "email": "user@example.com", "password": "strong-password" }
    ```
  - 201 Created:
    ```json
    {
      "message": "User created successfully",
      "user": { "id": "...", "email": "user@example.com", "created_at": "..." }
    }
    ```

- POST `/api/auth/login` — Obtain JWT
  - Body:
    ```json
    { "email": "user@example.com", "password": "strong-password" }
    ```
  - 200 OK:
    ```json
    {
      "message": "Login successful",
      "access_token": "<JWT>",
      "user": { "id": "...", "email": "user@example.com" }
    }
    ```

### Tasks (JWT required)

- GET `/api/tasks` — List tasks (with filters, sorting, pagination)
  - Query params (optional):
    - `status` in [`todo`, `in_progress`, `completed`]
    - `priority` in [1..5]
    - `category` (e.g., `work`, `personal`, `meeting`, `general`)
    - `sort_by` in [`created_at` (default), `deadline`, `priority`]
    - `page` (default 1), `limit` (default 10)
  - 200 OK:
    ```json
    {
      "tasks": [ { "id": "...", "title": "...", "status": "todo" } ],
      "total": 1,
      "page": 1,
      "pages": 1
    }
    ```

- POST `/api/tasks` — Create a task (runs AI analysis)
  - Body (minimum):
    ```json
    { "title": "Fix login bug", "description": "Investigate 500 on POST /login" }
    ```
  - 201 Created:
    ```json
    {
      "message": "Task created successfully",
      "task": {
        "id": "...",
        "title": "Fix login bug",
        "description": "Investigate 500 on POST /login",
        "category": "work",
        "priority": 5,
        "estimated_hours": 2.0,
        "deadline": null,
        "status": "todo",
        "tags": [],
        "created_at": "...",
        "updated_at": "..."
      },
      "ai_analysis": {
        "category": "work",
        "category_confidence": 0.9,
        "priority": 5,
        "estimated_hours": 2.0
      }
    }
    ```

- GET `/api/tasks/<task_id>` — Get a task

- PUT `/api/tasks/<task_id>` — Update a task
  - Updatable fields: `title`, `description`, `priority`, `status`, `deadline` (ISO8601), `tags` (array of strings)

- DELETE `/api/tasks/<task_id>` — Delete a task

- PATCH `/api/tasks/<task_id>/status` — Update only the status
  - Body: `{ "status": "in_progress" }`

### AI analysis (public)

- POST `/api/analyze/task` — Analyze free-form task text
  - Body:
    ```json
    { "title": "Review PR for feature X", "description": "Look for edge cases" }
    ```
  - 200 OK:
    ```json
    {
      "title": "Review PR for feature X",
      "predicted_category": "work",
      "category_confidence": 0.78,
      "predicted_priority": 3,
      "estimated_hours": 2.0
    }
    ```

Authorization header example:
```bash
curl -H "Authorization: Bearer <JWT>" http://127.0.0.1:5001/api/tasks
```

Common error responses:
```json
{ "error": "Email and password required" }
{ "error": "Title is required" }
{ "error": "Task not found" }
```

---

## Data model

### User
- `id`: string (UUID)
- `email`: string (unique)
- `password_hash`: string
- `created_at`: ISO8601 datetime

### Task
- `id`: string (UUID)
- `user_id`: string (UUID)
- `title`: string (required)
- `description`: string|null
- `category`: string (`work`|`personal`|`meeting`|`general`)
- `priority`: integer (1–5, default 3)
- `estimated_hours`: number|null
- `deadline`: ISO8601 datetime|null
- `status`: `todo`|`in_progress`|`completed`
- `tags`: array of strings
- `created_at` / `updated_at`: ISO8601 datetime

---

## Development notes
- Default config is development; server runs on port `5001`.
- JWT access tokens expire after 30 days by default.
- Change `JWT_SECRET_KEY` before deploying.
- The ML classifier is intentionally small and for demo purposes only.

---

## Project structure
```text
.
├── app.py                # Flask app factory + entrypoint
├── auth_routes.py        # /api/auth endpoints (register/login)
├── task_routes.py        # /api/tasks endpoints (CRUD + AI)
├── ai_routes.py          # /api/analyze endpoints (public AI analysis)
├── ai_service.py         # TF‑IDF + Naive Bayes pipeline
├── models.py             # SQLAlchemy models (User, Task)
├── config.py             # Config classes (Dev/Prod)
├── requirements.txt      # Python dependencies
└── README.md
```

---

## License
Add your preferred license text or file (e.g., MIT) here.

