# =============================================================================
# products/admin.py  --  Django admin for Category & Product
# =============================================================================
# Interview topics:
#   * @admin.register : registers a ModelAdmin for a model (shortcut)
#   * list_display    : which columns appear in the admin list view
#   * list_filter     : sidebar filters (by category, availability)
#   * search_fields   : adds a search box (by product name)
#
# Django admin auto-generates a CRUD UI from your models — very handy for
# ops/management. It's NOT the public API (DRF handles that), but it's
# common in interviews to ask "how would you manage data in production?"

from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name",)
