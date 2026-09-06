# =============================================================================
# orders/tests.py  --  pytest tests for the advanced orders flows
# =============================================================================
# Interview concepts demonstrated:
#   * Writable nested serializer: POST {items: [...]} creates Order + OrderItems
#   * bulk_create: one INSERT for many OrderItem rows
#   * Frozen total: order.total is computed once and never changes
#   * Row-level scoping: users can only see their own orders
#   * transaction.atomic + select_for_update: prevents double-payment
#   * F() expression: atomic stock decrement (no race condition)
#   * Django signals: pre_delete restocks products when an order is cancelled
#   * @action endpoints: mark_paid, stats (beyond standard CRUD)
#
# Run with:  .venv/bin/pytest orders/ -v

import pytest
from django.contrib.auth import get_user_model
from decimal import Decimal

from products.models import Category, Product
from orders.models import Order, OrderItem

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures — isolated per test (each test gets its own DB transaction)
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user(db):
    """The buyer who will place orders."""
    return User.objects.create_user(email="buyer@example.com", password="pw12345")


@pytest.fixture
def other_user(db):
    """A different user — used to test row-level isolation."""
    return User.objects.create_user(email="other@example.com", password="pw12345")


@pytest.fixture
def category(db):
    return Category.objects.create(name="gadgets")


@pytest.fixture
def product(db, category):
    """A product with 5 units in stock — tests decrement stock via F()."""
    return Product.objects.create(name="Widget", price="10.00", stock=5,
                                  category=category, is_available=True)


@pytest.fixture
def authed_client(user):
    """Pre-authenticated DRF client — simulates a logged-in user without
       minting a real JWT token (force_authenticate bypasses auth checks)."""
    from rest_framework.test import APIClient
    c = APIClient()
    c.force_authenticate(user)
    return c


# ---------------------------------------------------------------------------
# Tests — each demonstrates a specific interview concept
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_create_order_bulk_and_total(authed_client, product):
    """Writable nested serializer: POST {items: [{product_id, quantity}]}
       creates an Order + OrderItem rows inside transaction.atomic.
       Key points:
       - bulk_create: one INSERT for all items (not N separate inserts)
       - total is frozen: computed from product.price * quantity at creation
       - Price snapshot: OrderItem.price stores the price AT TIME OF PURCHASE,
         so future product price changes don't alter past orders."""
    r = authed_client.post("/api/orders/", {
        "items": [{"product_id": product.id, "quantity": 2}]
    }, format="json")
    assert r.status_code == 201
    assert "id" in r.data                                   # response includes order id
    order = Order.objects.get(pk=r.data["id"])
    assert order.total == Decimal("20.00")                  # 10.00 * 2, frozen
    assert order.items.count() == 1
    assert order.items.first().price == Decimal("10.00")    # frozen unit price


@pytest.mark.django_db
def test_order_row_scoping(user, other_user, authed_client, product):
    """Row-level isolation: a regular user can ONLY see their own orders.
       OrderViewSet.get_queryset() filters by user=user for non-staff users.
       This is a critical security pattern — users must never see each other's
       orders, even by guessing IDs."""
    Order.objects.create(user=other_user)                   # other user's order (invisible)
    authed_client.post(
        "/api/orders/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    r = authed_client.get("/api/orders/")
    assert r.status_code == 200
    assert r.data["count"] == 1                             # only 1 order visible
    assert r.data["results"][0]["user_email"] == "buyer@example.com"


@pytest.mark.django_db
def test_mark_paid_decrements_stock(authed_client, product):
    """@action mark_paid demonstrates:
       1. transaction.atomic: all-or-nothing (if stock decrement fails, status
          change is also rolled back)
       2. select_for_update: locks the row so two concurrent payments can't
          both pass the status check (prevents double-charging)
       3. F() expression: stock is decremented IN THE DATABASE (atomic UPDATE
          stock = stock - N), avoiding race conditions where two requests
          both read the same stale stock value."""
    r = authed_client.post(
        "/api/orders/",
        {"items": [{"product_id": product.id, "quantity": 2}]},
        format="json",
    )
    assert r.status_code == 201
    order_id = r.data["id"]
    resp = authed_client.post(f"/api/orders/{order_id}/mark_paid/")
    assert resp.status_code == 200
    product.refresh_from_db()                               # re-read from DB
    assert product.stock == 3                               # 5 - 2 = 3 (via F())
    order = Order.objects.get(pk=order_id)
    assert order.status == Order.Status.PAID


@pytest.mark.django_db
def test_delete_order_restocks(authed_client, product):
    """Django signal: pre_delete on Order triggers restock_on_order_delete.
       The signal iterates OrderItems and uses F() to atomically increment
       each product's stock. pre_delete is used (not post_delete) because
       CASCADE deletes OrderItem rows BEFORE post_delete fires.
       Interview tip: signals decouple side effects (restock) from the
       delete action, but you must think carefully about execution order."""
    order = Order.objects.create(user=User.objects.get(email="buyer@example.com"))
    OrderItem.objects.create(order=order, product=product, quantity=2, price="10.00")
    authed_client.delete(f"/api/orders/{order.id}/")
    product.refresh_from_db()
    assert product.stock == 7                               # 5 + 2 = 7 (restocked)
