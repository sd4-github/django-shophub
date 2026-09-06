"""config/celery.py  --  Celery application for the Django project
----------------------------------------------------------------------------
Celery runs background tasks (email, reports, cleanup) using Redis as the
message broker — the same Redis container the other two projects use.

Why Django + Celery (interview):
  * Django's own request/response cycle can't do long-running work gracefully.
  * Celery offloads it to worker processes that pull tasks from a queue,
    retry on failure, and can scale independently.

RUN A WORKER:
  .venv/bin/celery -A config worker --loglevel=info
"""

import os

from celery import Celery

# Tell Celery to read its settings from the Django settings module.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Create the Celery app named "config". broker/backend come from settings.py.
app = Celery("config")

# Pull config like CELERY_BROKER_URL, CELERY_TASK_SERIALIZER from settings.
# namespace="CELERY" means a setting named CELERY_BROKER_URL maps here.
app.config_from_object("django.conf:settings", namespace="CELERY")

# auto-discover tasks in each installed app's `tasks.py` module.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
