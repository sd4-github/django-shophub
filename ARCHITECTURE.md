# ShopHub — Architecture & Implementation

## Overview
Django + DRF pure-backend REST API for an e-commerce shop. Built for ~5 YOE interview preparation, progressing from basic (CRUD) through intermediate (auth, permissions) to advanced (N+1, F(), signals, Celery, Redis).

## Tech Stack
- **Framework**: Django 5.2 + Django REST Framework (DRF)
- **Database**: PostgreSQL 16 (port 5432)
- **Cache**: Redis via `django.core.cache` (db/1)
- **Background tasks**: Celery 5.4 (broker = Redis db/2) + django-celery-beat
- **Auth**: JWT via djangorestframework-simplejwt
- **API docs**: drf-spectacular (OpenAPI + Swagger UI)
- **Testing**: pytest-django
- **File uploads**: Django FileField + custom chunked save utility

## Project Structure
```
3_django_shophub/
├── config/                   # Django project settings, URLs, Celery wiring
│   ├── settings.py           # All config: DB, DRF, JWT, cache, Celery, CORS
│   ├── urls.py               # Project-wide URL routing
│   ├── celery.py             # Celery app configuration
│   └── __init__.py           # Exposes celery_app for autodiscovery
├── users/                    # Custom User model (email login)
│   ├── models.py             # AbstractUser + UserManager (email-based)
│   ├── serializers.py        # RegisterSerializer (write-only password)
│   ├── views.py              # RegisterView, MeView
│   └── urls.py               # /api/users/register/, /api/users/me/
├── products/                 # Catalog: Category + Product
│   ├── models.py             # Category, Product (DecimalField for money)
│   ├── serializers.py        # Nested category, category_id writable
│   ├── views.py              # CategoryViewSet (read-only), ProductViewSet
│   └── urls.py               # /api/products/, /api/categories/
├── orders/                   # Advanced: orders + line items
│   ├── models.py             # Order (status choices), OrderItem (line_total)
│   ├── serializers.py        # Writable nested create, bulk_create
│   ├── views.py              # N+1 fix, mark_paid, stats (Redis cache)
│   ├── permissions.py        # IsOwnerOrStaff (object-level permission)
│   ├── signals.py            # pre_delete: restock via F()
│   ├── tasks.py              # Celery task: send_confirmation_email
│   └── urls.py               # /api/orders/, mark_paid, stats
├── files/                    # File upload + Python file operations
│   ├── models.py             # UploadedFile (FileField + metadata)
│   ├── views.py              # FileUploadView, FileListView
│   ├── fileops.py            # Utility: safe filenames, chunked read/write
│   └── urls.py               # /api/files/upload/, /api/files/
├── python_scripts/           # Standalone Python learning scripts
│   ├── 01_basics.py          # Variables, control flow, comprehensions
│   ├── 02_intermediate.py    # Decorators, context managers, closures
│   ├── 03_orm_advanced.py    # Queryset laziness, F(), N+1, transactions
│   └── 04_file_operations.py # File I/O, pathlib, safe filenames, shutil
├── requirements.txt          # Pinned dependencies
├── pytest.ini                # pytest-django configuration
├── .env                      # Environment variables (git-ignored)
├── .gitignore
├── INTERVIEW_TOPICS.md       # Topic → file mapping for interview prep
├── manage.py                 # Django management CLI
└── ARCHITECTURE.md           # This file
```

## Key Design Decisions

### Custom User Model (users/models.py)
Swapped `AUTH_USER_MODEL` on day one — best practice. Email-based login with role field. `UserManager` provides `create_user`/`create_superuser` that hash passwords via `set_password()`.

### Money: DecimalField (products/orders/models.py)
Never `FloatField` for money. `DecimalField(max_digits=10, decimal_places=2)` stores exact values. Order total is frozen at creation time so future price changes don't affect past orders.

### N+1 Problem Solved (orders/views.py, products/views.py)
- `select_related("user")` for forward FK — single JOIN query
- `prefetch_related("items__product")` for reverse FK + forward FK — 3 queries total instead of N+1

### Atomic Stock Handling (orders/views.py)
`transaction.atomic()` + `select_for_update()` locks the order row during payment to prevent double-charging. `F("stock") - quantity` decrements stock in the database atomically (no Python read-write race).

### Signals (orders/signals.py)
`pre_delete` on Order restores product stock via `F()` when an order is cancelled/deleted. Uses `pre_delete` (not `post_delete`) because CASCADE deletes OrderItem rows before `post_delete` fires.

### Custom Permissions (orders/permissions.py)
`IsOwnerOrStaff` — object-level DRF permission. Staff/admin can access any row; regular users can only access their own. Demonstrates `has_object_permission()`.

### File Uploads (files/)
`MultiPartParser` + `SimpleUploadedFile` for chunked disk writes. `safe_filename()` strips directory components to prevent path traversal attacks. Extension whitelist blocks dangerous uploads.

## Interview Topics Covered
See [INTERVIEW_TOPICS.md](INTERVIEW_TOPICS.md) for a complete mapping of interview questions to source files.
