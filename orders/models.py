# =============================================================================
# orders/models.py  --  Order and OrderItem models
# =============================================================================
# Demonstrates the interview-heavy ORM/money/relationship features:
#   * Transactional integrity : one Order + many OrderItems must save atomically
#     (see orders/views.py perform_create -> transaction.atomic).
#   * DecimalField for money  (never FloatField).
#   * ForeignKey on_delete choices: CASCADE / PROTECT / SET_NULL (why each).
#   * `related_name` for reverse lookups.
#   * `prefetch_related` for the N+1 problem on reverse/many relations
#     (see OrderViewSet.get_queryset).

from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    """A customer's order containing one or more OrderItems."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        CANCELLED = "cancelled", "Cancelled"

    # The user who placed this order.
    # on_delete=CASCADE  -> if the user is deleted, delete their orders too.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    # Full price snapshot of the order, computed and frozen at creation time
    # (so later product price changes don't alter a past order).
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.user} - {self.status}"


class OrderItem(models.Model):
    """A single product line within an order."""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "products.Product",
        # PROTECT: do not silently allow deleting a product that was ordered.
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    # Unit price frozen at purchase time (not the product's current price).
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self) -> "Decimal":
        """price * quantity for this line."""
        return self.price * self.quantity

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product} in order #{self.order_id}"
