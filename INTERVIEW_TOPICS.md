# ShopHub — Django: Interview Topics Covered

> Pure-backend Django + DRF API. **Basic → Intermediate → Advanced**, ~5 YOE depth.
> Each row maps a likely **interview question/topic** to the **file(s)** where it's answered in code.
> Relative links are from the project root `3_django_shophub/`.

---

## 1. Python fundamentals
| Topic / question | Where covered |
|------------------|---------------|
| Types, f-strings, control flow, functions | [python_scripts/01_basics.py](python_scripts/01_basics.py) |
| Decorators, context managers, mutable defaults, closures | [python_scripts/02_intermediate.py](python_scripts/02_intermediate.py) |
| ORM & queryset patterns, F expressions, aggregation | [python_scripts/03_orm_advanced.py](python_scripts/03_orm_advanced.py) |
| Python file I/O, safe filenames, streaming reads/writes | [python_scripts/04_file_operations.py](python_scripts/04_file_operations.py) |

## 2. Django framework core
| Topic / question | Where covered |
|------------------|---------------|
| Project structure (`manage.py`, `config/` layout) | [config/settings.py](config/settings.py) |
| Custom User model (email login, `AUTH_USER_MODEL`) | [users/models.py](users/models.py) |
| App registry (`INSTALLED_APPS`), apps (users, products, orders, files) | [config/settings.py](config/settings.py) |
| Database config (Postgres) + migrations workflow | [manage.py](manage.py) |
| Django REST Framework (DRF) setup: JWT auth, pagination, schema | [config/settings.py](config/settings.py) |
| CORS + middleware stack | [config/settings.py](config/settings.py) |
| Signals (`post_save`, `post_delete`) — atomic stock change & restock | [orders/signals.py](orders/signals.py) |
| F() expressions — atomic DB arithmetic (avoid race conditions) | [orders/views.py](orders/views.py), [orders/signals.py](orders/signals.py) |
| `transaction.atomic` + `select_for_update` — correct money/stock handling | [orders/views.py](orders/views.py) |
| Custom DRF permission (object-level): `IsOwnerOrStaff` | [orders/permissions.py](orders/permissions.py) |
| ViewSet + Router (products) + custom @action endpoints | [products/views.py](products/views.py), [orders/views.py](orders/views.py) |
| Filter backends: `SearchFilter`, `OrderingFilter`, `django_filters` | [products/views.py](products/views.py) |
| `prefetch_related` — N+1 problem solved (reverse FK / M2M) | [orders/views.py](orders/views.py) |
| `get_queryset` row-level scoping (user owns their data) | [orders/views.py](orders/views.py) |
| `perform_create` — save with business logic + Celery trigger | [orders/views.py](orders/views.py) |
| DRF generics vs ViewSet + Router patterns | [products/views.py](products/views.py), [orders/views.py](orders/views.py) |
| Custom serializer fields / nested writes (`category_id`) | [products/serializers.py](products/serializers.py) |
| `SerializerMethodField` (computed `line_total`) | [orders/serializers.py](orders/serializers.py) |
| `bulk_create` — one INSERT for many rows | [orders/serializers.py](orders/serializers.py) |
| `FileField` + upload handling (`UploadedFile` model) | [files/models.py](files/models.py), [files/views.py](files/views.py) |
| `form_parser` / `MultiPartParser` + chunked save | [files/views.py](files/views.py) |
| Redis cache (via `django.core.cache`) with 60s TTL | [orders/views.py](orders/views.py) |
| Celery task queue + `@shared_task` (order confirmation email) | [orders/tasks.py](orders/tasks.py), [config/celery.py](config/celery.py) |
| `django_celery_beat` periodic tasks | [config/settings.py](config/settings.py) |
| `drf-spectacular` OpenAPI schema + Swagger UI | [config/settings.py](config/settings.py) |
| URL routing: router registrations + `include()` | [config/urls.py](config/urls.py), [orders/urls.py](orders/urls.py), [products/urls.py](products/urls.py), [users/urls.py](users/urls.py) |
| `@action(detail=True)` & `@action(detail=False)` custom endpoints | [orders/views.py](orders/views.py) |
| ModelAdmin + inlines + `prepopulated_fields` + `list_filter` | [products/admin.py](products/admin.py), [orders/admin.py](orders/admin.py), [users/admin.py](users/admin.py) |

## 3. Advanced Django topics
| Topic / question | Where covered |
|------------------|---------------|
| `prefetch_related` vs `select_related` (N+1 root cause + fix) | [orders/views.py](orders/views.py) [python_scripts/03_orm_advanced.py](python_scripts/03_orm_advanced.py) |
| `F()` expressions — atomic DB update, avoids race conditions | [orders/views.py](orders/views.py) [orders/signals.py](orders/signals.py) [python_scripts/03_orm_advanced.py](python_scripts/03_orm_advanced.py) |
| `transaction.atomic` — all-or-nothing writes | [orders/views.py](orders/views.py) |
| `select_for_update` — row-level locking under atomic | [orders/views.py](orders/views.py) |
| `bulk_create` — minimize INSERT count | [orders/serializers.py](orders/serializers.py) |
| `defer()` / `only()` — skip expensive columns | [python_scripts/03_orm_advanced.py](python_scripts/03_orm_advanced.py) |
| Django signals (`post_save`, `post_delete`) + `F()` for side effects | [orders/signals.py](orders/signals.py) |
| Custom DRF object-level permissions (`has_object_permission`) | [orders/permissions.py](orders/permissions.py) |
| `@action` — extend ViewSet with custom routes (/mark_paid, /stats) | [orders/views.py](orders/views.py) |
| Redis caching via `django.core.cache.cache` / `cache.set/get` | [orders/views.py](orders/views.py) |
| Celery + `broker = Redis`; `@shared_task` for email / background work | [orders/tasks.py](orders/tasks.py), [config/celery.py](config/celery.py) |
| `django-celery-beat` for scheduled tasks via admin | [config/settings.py](config/settings.py) |
| File upload endpoint (multipart, safe filename, chunked write) + Download URL | [files/views.py](files/views.py), [files/fileops.py](files/fileops.py), [files/urls.py](files/urls.py) |
| `select_related` inside signals (avoiding N+1 in hot paths) | [orders/signals.py](orders/signals.py) |
| `transaction.atomic` guard against double-payment / double-decrement | [orders/views.py](orders/views.py) |

## 4. File operations (standalone Python module)
| Topic / question | Where covered |
|------------------|---------------|
| `open()` modes, context managers | [python_scripts/04_file_operations.py](python_scripts/04_file_operations.py) |
| Safe filenames (`os.path.basename`) + extension whitelist | [files/fileops.py](files/fileops.py) |
| Read/write/append, read in chunks (streaming) | [python_scripts/04_file_operations.py](python_scripts/04_file_operations.py) |
| `pathlib.Path` — modern path handling | [python_scripts/04_file_operations.py](python_scripts/04_file_operations.py) |
| `shutil.move` / `copy`, `tempfile` | [python_scripts/04_file_operations.py](python_scripts/04_file_operations.py) |

## 5. Deployment & ops
| Topic / question | Where covered |
|------------------|---------------|
| `.env` + `python-dotenv` for config | [config/settings.py](config/settings.py) |
| MEDIA_ROOT / MEDIA_URL for uploads | [config/settings.py](config/settings.py) |
| `manage.py check` + `manage.py migrate` workflow | [manage.py](manage.py) |
| `manage.py test` / pytest-django test runner | [pytest.ini](pytest.ini) |
| JWT auth flow: `/api/auth/token/` + `/api/auth/refresh/` | [config/urls.py](config/urls.py) |
| OpenAPI schema: `/api/schema/` + Swagger UI: `/api/docs/` | [config/urls.py](config/urls.py) |

---

### How to explore
Start with `python_scripts/01_basics.py`, then `config/settings.py` (the wiring diagram), then per-feature apps (users → auth, products → catalog, orders → full CRUD + advanced, files → upload). Every file is heavily commented with **why**, not just *what*.