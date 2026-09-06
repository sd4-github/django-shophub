# =============================================================================
# orders/admin.py  --  Django admin for Orders + OrderItems
# =============================================================================
# Interview topics:
#   * @admin.register : registers a ModelAdmin for a model (shortcut)
#   * list_display    : which columns appear in the admin list view
#   * list_filter     : sidebar filters (status, date)
#   * search_fields   : adds a search box (searches by related user email)
#   * readonly_fields : prevents editing total (it's computed/frozen)
#   * inlines         : show OrderItems INSIDE the Order detail page
#     (TabularInline = compact table; StackedInline = one section per item)
#
# Inlines are useful for one-to-many relationships: you edit the parent
# and its children on the same admin page. Very common interview topic.

from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("total",)
    inlines = [OrderItemInline]
