# =============================================================================
# orders/views.py  --  OrderViewSet (the "everything in one class" pattern)
# =============================================================================
# This file is where most interview-advanced topics come together:
#   * N+1 problem solved with prefetch_related (many-to-many / reverse FK).
#   * Object-level permission via IsOwnerOrStaff.
#   * transaction.atomic + select_for_update for correct money/stock handling.
#   * F() expressions for atomic stock decrement.
#   * @action endpoints (paid / stats) beyond standard CRUD.
#   * Redis caching of a stats result.
#   * Celery task queued on order creation.

from decimal import Decimal

from django.core.cache import cache
from django.db import transaction
from django.db.models import F, Count, Sum
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsOwnerOrStaff
from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
)
from .tasks import send_confirmation_email


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD + custom @action endpoints for orders."""
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrStaff]

    # ------- serializer selection (create uses the writable nested one) ----
    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    # ------- queryset: N+1 SOLVED + row scoping -----------------------------
    def get_queryset(self):
        """Return orders, prefetched to avoid the classic N+1 query problem.
           `items` is a reverse-FK and `items__product` is a forward FK, so we
           use prefetch_related (many side) — one query for items + one for
           products, instead of one query PER order/per item."""
        qs = self.queryset.select_related("user").prefetch_related(
            "items__product"
        )
        # Non-staff users can ONLY see their own orders (row-level isolation).
        user = self.request.user
        if not (user.is_staff or getattr(user, "role", "") == "admin"):
            qs = qs.filter(user=user)
        return qs

    # ------- create + fire a Celery task -----------------------------------
    def create(self, request, *args, **kwargs):
        """Override to return OrderSerializer (with id + nested items) instead
        of OrderCreateSerializer which has no id field."""
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        order = write_serializer.save()
        read_serializer = OrderSerializer(order, context={"request": request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        order = serializer.save()
        send_confirmation_email.delay(order.id, order.user.email)

    # ------- custom @action: mark an order as paid --------------------------
    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        """Set a pending order to PAID and atomically decrement stock.
           Demonstrates transaction.atomic + select_for_update + F()."""
        order = self.get_object()                     # applies IsOwnerOrStaff

        with transaction.atomic():
            # Re-read the order locked for update so two concurrent payments
            # can't both pass the status check (prevents double charging).
            locked = (
                Order.objects.select_for_update().get(pk=order.pk)
            )
            if locked.status != Order.Status.PENDING:
                return Response(
                    {"error": "Only pending orders can be marked paid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Decrement each item's stock safely in the DB (atomic, no race).
            for item in locked.items.select_related("product"):
                item.product.stock = F("stock") - item.quantity
                item.product.save(update_fields=["stock"])

            locked.status = Order.Status.PAID
            locked.save(update_fields=["status", "updated_at"])

        return Response(OrderSerializer(locked).data)

    # ------- custom @action: cached aggregate stats -------------------------
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Return aggregate order stats, cached in Redis for 60s.
           Demonstrates Django's cache framework (backed by Redis here)."""
        KEY = "shophub:order_stats"
        cached = cache.get(KEY)
        if cached is not None:
            return Response({"source": "cache", "data": cached})

        # ... pretend this is an expensive aggregation ...
        aggregate = Order.objects.aggregate(
            total_orders=Count("id"),
            total_revenue=Sum("total", default=Decimal("0.00")),
        )
        cache.set(KEY, aggregate, 60)                 # seconds
        return Response({"source": "fresh", "data": aggregate})
