# =============================================================================
# products/serializers.py  --  DRF serializers for Category & Product
# =============================================================================
# Uses nested serializers + validation hooks.
#
#   * read_only_fields : returned but not accepted on input.
#   * NestedSerializer : category appears as an object (not just its id).
#   * Depth alternative: Meta.depth = 1 would auto-nest, but explicit nested
#     serializers give you more control (interviewers like to see this).
#   * We add DEFAULT ordering + search/filter in the view; serializers only
#     describe data shape and validate.

from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description")


class ProductSerializer(serializers.ModelSerializer):
    # Explicit nested category object (category_id still accepted on input).
    category = CategorySerializer(read_only=True)
    # Accept category_id as an integer on create/update:
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True
    )

    class Meta:
        model = Product
        fields = (
            "id", "name", "description", "price", "stock",
            "is_available", "category", "category_id", "created_at",
        )
        read_only_fields = ("created_at",)

    def validate_price(self, value):
        """Business rule: never allow a zero/negative price."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def create(self, validated_data):
        """Override create so `category_id` (a Category instance from
        PrimaryKeyRelatedField) is passed as `category` to the model."""
        category = validated_data.pop("category_id")   # Category instance
        validated_data["category"] = category
        return super().create(validated_data)
