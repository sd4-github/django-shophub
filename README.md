# ShopHub

A **Django + DRF** e-commerce REST API built for backend interview preparation (~5 YOE depth). Covers Django fundamentals through advanced patterns like N+1 optimization, F() expressions, signals, JWT auth, Celery tasks, and Redis caching.

[GitHub](https://github.com/sd4-github/django-shophub)

## What It Does

- **Register & login** with JWT auth (access + refresh tokens)
- **Browse products** with search, filtering, and ordering
- **Place orders** with atomic stock management and race condition prevention
- **Upload files** with safe filename handling
- **Advanced features**: signals for stock restoration, Redis-cached stats, background order emails

## Tech Stack

| Layer | Tech |
|-------|------|
| Framework | [Django](https://www.djangoproject.com/) 5.2 + DRF 3.15 |
| Database | PostgreSQL |
| Auth | JWT (simplejwt) |
| Caching | Redis |
| Background Tasks | Celery + Redis |
| Filtering | django-filter |
| API Docs | drf-spectacular (OpenAPI + Swagger) |
| Testing | pytest + pytest-django |

## Project Structure

```
config/                  # Django project settings, URLs, WSGI
├── settings.py
├── urls.py
└── celery.py
users/                   # Custom User model (email login, roles)
products/                # Product catalog + categories
orders/                  # Order management with atomic operations
files/                   # File uploads with safe handling
manage.py
```

## Quick Start

```bash
# Prerequisites: PostgreSQL + Redis running locally

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start the dev server
python manage.py runserver
```

API available at [http://127.0.0.1:8000](http://127.0.0.1:8000) | Swagger docs at [/api/docs/](http://127.0.0.1:8000/api/docs/)

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/token/` | No | Get JWT tokens |
| `POST` | `/api/auth/refresh/` | No | Refresh access token |
| `POST` | `/api/users/register/` | No | Register user |
| `GET` | `/api/users/me/` | Yes | Current user profile |
| `GET/POST` | `/api/products/` | No/Staff | List/create products |
| `GET/PUT/DELETE` | `/api/products/{id}/` | No/Staff | Product detail |
| `GET` | `/api/categories/` | No | List categories |
| `GET/POST` | `/api/orders/` | Yes | List/create orders |
| `GET/PATCH/DELETE` | `/api/orders/{id}/` | Yes* | Order detail |
| `POST` | `/api/orders/{id}/mark_paid/` | Yes* | Mark order paid |
| `GET` | `/api/orders/stats/` | Yes | Cached order stats |
| `POST` | `/api/files/upload/` | Yes | Upload file |
| `GET` | `/api/files/` | Yes | List user files |

*Owner or staff only

## Interview Topics Covered

- Custom User model, AUTH_USER_MODEL swap
- Django signals (pre_delete for stock restoration)
- ORM optimization: select_related, prefetch_related, F() expressions
- transaction.atomic + select_for_update for race conditions
- DRF ViewSets, Routers, nested serializers
- JWT auth with token rotation and blacklisting
- Celery background tasks with Redis
- Redis caching via Django cache framework
- Safe file handling, path traversal prevention
- OpenAPI schema generation

See [INTERVIEW_TOPICS.md](INTERVIEW_TOPICS.md) for the full topic-to-file mapping.

## More Projects

- [TakkarCV](https://github.com/sd4-github/takkarcv)
- [Keycloak RBAC Django Auth](https://github.com/sd4-github/keycloak-rbac-django-auth)
- [Bulk Contract Processing](https://github.com/sd4-github/bulk-contract-processing)
- [Contract Processing](https://github.com/sd4-github/contract-processing)

## Built With

All projects in this collection are built using [OpenCode](https://opencode.ai) free models — DeepSeek V4 Flash, Big Pickle, Mimo V2.5, and more.
