# =============================================================================
# products/models.py  --  Category and Product models
# =============================================================================
# Django ORM models: a class = a table, attributes = columns. Django generates
# the SQL, migrations, and the admin for us.
#
# Interview notes:
#   * ImageField requires Pillow; we use a CharField URL to stay dependency-free.
#   * DecimalField(precision) is correct for money (never FloatField).
#   * indexes (db_index=True) speed up lookups on that column.
#   * `related_name` names the reverse ManyToOne access (category.products).

from django.conf import settings
from django.db import models


class Category(models.Model):
    """Products belong to exactly one category."""
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)          # default ordering for list queries

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """A sellable item."""
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # money = Decimal
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    # relationship: a Category has many Products
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,          # refuse to delete a category with products
        related_name="products",           # gives category.products.all()
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,         # keep product if user is deleted
        null=True,
        related_name="products",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.name} (${self.price})"
