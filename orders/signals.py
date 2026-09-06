# =============================================================================
# orders/signals.py  --  Django signals (decouple events from actions)
# =============================================================================
# Signals let one part of the app react to actions elsewhere WITHOUT the
# caller importing it — a decoupling pattern. Common in interviews.
#
# Here: when an Order is DELETED/cancelled, we RESTORE the product stock that
# was decremented when the order was placed. This fires once per delete, so it
# is correct and idempotent — a clean way to show signals.
#
# F() expressions (interview topic):
#   * F("stock") + N  -> the UPDATE runs IN THE DATABASE, not in Python.
#   * Avoids a race: two requests updating the same stock would otherwise
#     read-and-write a stale value. F() makes the arithmetic atomic.
#
# NOTE on N+1: inside a signal, iterating `instance.items.all()` issues one
# query per item. In a hot path you would prefetch once:
#   items = instance.items.prefetch_related("product").all()

from django.db.models import F
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Order, OrderItem


@receiver(pre_delete, sender=Order)
def restock_on_order_delete(sender, instance: Order, **kwargs):
    """Restore product stock BEFORE the order (and its cascade-deleted items)
       is removed from the DB. Using pre_delete because post_delete fires
       AFTER CASCADE has already removed the OrderItem rows."""
    items = OrderItem.objects.select_related("product").filter(order_id=instance.id)
    for item in items:
        item.product.stock = F("stock") + item.quantity
        item.product.save(update_fields=["stock"])
