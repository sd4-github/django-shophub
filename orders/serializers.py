# =============================================================================
# orders/serializers.py  --  DRF serializers for orders (nested items)
# =============================================================================
# Highlights:
#   * Writable nested serializer : OrderCreateSerializer accepts an `items`
#     list and builds Order + OrderItem rows together.
#   * Read-only nested output    : OrderSerializer returns items with product
#     details + computed line_total.
#   * serializers.ListField(child=...)       : a list of nested inputs.
#   * SerializerMethodField                 : compute a field on the fly.
#   * We compute `total` and freeze unit prices at creation (money correctness).

from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Order, OrderItem


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Read-only: how a line appears inside an order's JSON output."""
    product = ProductSerializer(read_only=True)      # fully nested product
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "price", "line_total")

    def get_line_total(self, obj: OrderItem) -> str:
        # SerializerMethodField lets us compute+format values for the response.
        return f"{obj.line_total:.2f}"


class OrderItemCreateSerializer(serializers.Serializer):
    """Input: an anonymous {product_id, quantity} entry (not yet a model row)."""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value: int) -> int:
        if not Product.objects.filter(id=value, is_available=True).exists():
            raise serializers.ValidationError(
                f"Product {value} is not available."
            )
        return value


class OrderCreateSerializer(serializers.Serializer):
    """Accepts {items: [{product_id, quantity}, ...]} and creates an order."""
    items = OrderItemCreateSerializer(many=True)

    def validate_items(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("An order needs at least one item.")
        return value

    def create(self, validated_data):
        from django.db import transaction
        from decimal import Decimal

        user = self.context["request"].user

        with transaction.atomic():
            # ---- create the Order (status defaulted) ----
            order = Order.objects.create(user=user)

            # ---- turn {product_id, quantity} into OrderItem rows ----
            # We look up each product once; build rows; total is computed by
            # summing product.price * quantity using the CURRENT price,
            # then frozen into each OrderItem.price.
            rows = []
            total = Decimal("0.00")
            for item in validated_data["items"]:
                product = Product.objects.select_for_update().get(
                    id=item["product_id"]
                )
                line = product.price * item["quantity"]
                total += line
                # bulk-construct OrderItem objects (saved together below)
                rows.append(OrderItem(
                    order=order,
                    product=product,
                    quantity=item["quantity"],
                    price=product.price,
                ))

            OrderItem.objects.bulk_create(rows)     # one INSERT for all rows
            order.total = total
            order.save(update_fields=["total"])      # persist the frozen total

        return order


class OrderSerializer(serializers.ModelSerializer):
    """Read-only output for an order + its nested items."""
    user_email = serializers.CharField(source="user.email", read_only=True)
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "user_email", "status", "total", "items", "created_at")
