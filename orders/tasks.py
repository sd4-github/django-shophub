# =============================================================================
# orders/tasks.py  --  Celery tasks for the orders app
# =============================================================================
# Celery auto-discovers this file (config/celery.py autodiscover_tasks()).
# A task runs on a worker asynchronously; here we simulate sending an order
# confirmation email. Durable + retryable (unlike in-process background work).
#
# RUN A WORKER:  .venv/bin/celery -A config worker --loglevel=info
#
# If you want to auto-retry on failure, catch the exception and call
# `self.retry(countdown=...)` using the bound-task form (@app.task(bind=True)).

from celery import shared_task

from config.celery import app


@app.task(name="orders.send_confirmation_email")
def send_confirmation_email(order_id: int, email: str) -> dict:
    """Simulate emailing a confirmation for a freshly placed order."""
    # In production: SMTP call, PDF invoice, etc.
    print(f"[celery] sending order confirmation for order #{order_id} to {email}")
    return {"order_id": order_id, "to": email, "status": "queued"}
