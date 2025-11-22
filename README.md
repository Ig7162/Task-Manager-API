## Welcome! This is my first ever coding project in github( I did have some help making the ReadMe with other people)




## Task-Manager-API
This is a AI‑assisted task management assisted REST API built with Flask. It provides authentication, tasks CRUD, and lightweight ML to categorize tasks, suggest priority, and estimate effort. My first coding project!

### Table of contents
- [Features](#features)
- [Tech stack](#tech-stack/Languages)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [Run](#run)
- [API reference](#api-reference)
- [Data model](#data-model)
- [Project structure](#project-structure)
- [Development notes](#development-notes)
- [License](#license)

### Features
- **Authentication**: JWT-based register/login
- **Tasks CRUD**: Create, read, update, delete
- **AI analysis**: Category prediction + confidence, priority suggestion, hour estimate
- **Filters & pagination**: Status/priority/category filters, sorting, pages/limits
- **Deadlines & tags**: ISO8601 deadlines; tags stored as list in responses

### Tech stack/Languages
- **Backend**: Flask 2.3.x, Flask‑SQLAlchemy
- **Auth**: Flask‑JWT‑Extended
- **ML**: scikit‑learn (TF‑IDF + MultinomialNB)
- **DB**: SQLite by default (configurable)
- **Security**: Werkzeug password hashing

---

## Quickstart

### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Start the server
```bash
python app.py
```
Server runs at `http://127.0.0.1:5001`.

### 3) Register and login
```bash
# Register
curl -s -X POST http://127.0.0.1:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"strong-password"}'

# Login (this copies the access_token from the response)
curl -s -X POST http://127.0.0.1:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"strong-password"}'

# Set your token (paste from the login response)
export TOKEN="<JWT>"
```

### 4) Create and list tasks
```bash
# Create a task (The AI then runs automatically)
curl -s -X POST http://127.0.0.1:5001/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Fix login bug","description":"Investigate 500 on POST /login"}'

# List the tasks
curl -s http://127.0.0.1:5001/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

---

## Configuration
Environment variables (defaults shown):
```bash
# REQUIRED in production – remember to change this!
export JWT_SECRET_KEY="your-secret-key-change-in-production"

# Optional: override database (defaults to a local SQLite file)
export DATABASE_URL="sqlite:///task_database.db"
```
Notes:
- On first run, the DB/tables are created automatically.
- The first AI service load trains a small model and saves it to `models/task_classifier.pkl`.

---

## Run
```bash
python app.py
```
Base URL: `http://127.0.0.1:5001`

---

## API reference

Use `Authorization: Bearer <JWT>` for protected endpoints.

### Endpoints overview

| Method | Path                         | Description                                | Auth |
|-------:|------------------------------|--------------------------------------------|:----:|
| POST   | `/api/auth/register`         | Register user                               |  ✗   |
| POST   | `/api/auth/login`            | Login, returns JWT                          |  ✗   |
| GET    | `/api/tasks`                 | List tasks (filters/sort/pagination)        |  ✓   |
| POST   | `/api/tasks`                 | Create task (with AI analysis)              |  ✓   |
| GET    | `/api/tasks/<task_id>`       | Get task by id                              |  ✓   |
| PUT    | `/api/tasks/<task_id>`       | Update task                                 |  ✓   |
| DELETE | `/api/tasks/<task_id>`       | Delete task                                 |  ✓   |
| PATCH  | `/api/tasks/<task_id>/status`| Update only status                          |  ✓   |
| POST   | `/api/analyze/task`          | Analyze free-form task text (AI only)       |  ✗   |

Filters for `GET /api/tasks`:
- **status**: `todo` | `in_progress` | `completed`
- **priority**: 1..5
- **category**: `work` | `personal` | `meeting` | `general`
- **sort_by**: `created_at` (default) | `deadline` | `priority`
- **page/limit**: pagination (defaults: 1 / 10)

Authorization header example:
```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5001/api/tasks
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

## Development notes
- Default config is development; server runs on port `5001`.
- JWT access tokens expire after 30 days by default.
- Change `JWT_SECRET_KEY` before deploying.
- The ML classifier is intentionally small and for demo purposes only.
