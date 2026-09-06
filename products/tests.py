# =============================================================================
# products/tests.py  --  pytest tests for the catalog API
# =============================================================================
# Interview concepts demonstrated:
#   * Public read vs staff-only write (get_permissions pattern)
#   * DRF pagination: response is {"count": N, "results": [...]}
#   * Filtering (?is_available=true), search (?search=Ball)
#   * Serializer validation: price must be positive
#   * PrimaryKeyRelatedField: category_id resolves the integer to a Category
#   * APIClient.force_authenticate() for staff/admin endpoints
#
# Run with:  .venv/bin/pytest products/ -v

import pytest
from django.contrib.auth import get_user_model

from .models import Category, Product

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures — each test gets a fresh DB row via the `db` marker
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    """Unauthenticated DRF test client (for public endpoint tests)."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def category(db):
    """A single Category — products must belong to one."""
    return Category.objects.create(name="toys")


@pytest.fixture
def product_a(db, category):
    """An available product with stock."""
    return Product.objects.create(name="Ball", price="5.00", stock=10,
                                  category=category, is_available=True)


@pytest.fixture
def product_b(db, category):
    """An unavailable product with zero stock (used for filtering tests)."""
    return Product.objects.create(name="Doll", price="20.00", stock=0,
                                  category=category, is_available=False)


@pytest.fixture
def staff_user(db):
    """A staff user — is_staff=True allows write access to products.
       ProductViewSet.get_permissions() returns IsAdminUser for create/update."""
    return User.objects.create_user(email="admin@example.com", password="pw12345",
                                    role="admin", is_staff=True)


@pytest.fixture
def staff_client(staff_user):
    """Pre-authenticated client with staff permissions."""
    from rest_framework.test import APIClient
    c = APIClient()
    c.force_authenticate(staff_user)
    return c


# ---------------------------------------------------------------------------
# Tests — grouped by the interview concept they demonstrate
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_products_public_read(api_client, product_a, product_b):
    """Anyone (no auth) can list products — demonstrates AllowAny on list.
       DRF pagination wraps results in {"count": N, "results": [...]}."""
    r = api_client.get("/api/products/")
    assert r.status_code == 200
    assert r.data["count"] == 2


@pytest.mark.django_db
def test_products_not_public_write(api_client, category):
    """Unauthenticated users cannot create products — demonstrates that
       the default IsAdminUser permission blocks non-staff users.
       Returns 401 (no credentials) or 403 (credentials but not staff)."""
    r = api_client.post("/api/products/", {
        "name": "Car", "price": "8.00", "stock": 1,
        "category_id": category.id, "is_available": True,
    }, format="json")
    assert r.status_code in (401, 403)


@pytest.mark.django_db
def test_staff_can_write(staff_client, category):
    """Staff users CAN create products — the same IsAdminUser permission
       returns True when user.is_staff is True. Demonstrates per-view
       permission logic via get_permissions()."""
    r = staff_client.post("/api/products/", {
        "name": "Car", "price": "8.00", "stock": 1,
        "category_id": category.id, "is_available": True,
    }, format="json")
    assert r.status_code == 201                             # HTTP 201 Created


@pytest.mark.django_db
def test_price_must_be_positive(staff_client, category):
    """Serializer-level validation: ProductSerializer.validate_price()
       rejects zero or negative prices. This is a common interview question
       about where to put business rules (serializer vs model vs view)."""
    r = staff_client.post("/api/products/", {
        "name": "Car", "price": "-1", "stock": 1,
        "category_id": category.id, "is_available": True,
    }, format="json")
    assert r.status_code == 400


@pytest.mark.django_db
def test_filter_is_available(api_client, product_a, product_b):
    """Custom queryset filtering via ?is_available=false query param.
       ProductViewSet.get_queryset() applies this filter dynamically.
       Demonstrates per-request queryset modification."""
    r = api_client.get("/api/products/?is_available=false")
    assert r.status_code == 200
    assert r.data["count"] == 1
    assert r.data["results"][0]["name"] == "Doll"


@pytest.mark.django_db
def test_search_filter(api_client, product_a, product_b):
    """DRF's SearchFilter backend: ?search=Ball performs a case-insensitive
       contains lookup on the declared search_fields (name, description).
       Demonstrates declarative filtering via filter_backends."""
    r = api_client.get("/api/products/?search=Ball")
    assert r.status_code == 200
    assert r.data["count"] == 1
    assert r.data["results"][0]["name"] == "Ball"
