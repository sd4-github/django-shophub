# =============================================================================
# config/__init__.py  --  exposes the Celery app for the project
# =============================================================================
# Importing the Celery app here ensures `celery -A config` and `manage.py`
# share the SAME Celery instance. This is the standard Django+Celery setup
# (from the Celery 4+ integration docs).

from .celery import app as celery_app

__all__ = ("celery_app",)
