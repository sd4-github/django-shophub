# =============================================================================
# products/views.py  --  DRF ViewSets for products (the "advanced" pattern)
# =============================================================================
# ViewSets combine all CRUD actions (list, retrieve, create, update, delete)
# into one class; a Router maps them to URLs automatically.
#
# Interview topics:
#   * filtering/search/ordering are DRF backends you declare once.
#   * get_permissions() lets you set PER-VIEW permissions (public read,
#     authenticated write). See how products are readable by anyone but only
#     staff/admins can create.
#   * permission_classes default = IsAuthenticated (from settings).

from rest_framework import filters, permissions, viewsets

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list/retrieve for categories (everyone can browse)."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]   # fully public
    # declarative filtering by name (?search=...)
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class ProductViewSet(viewsets.ModelViewSet):
    """Full CRUD for products. Public reads, staff writes."""
    queryset = Product.objects.select_related("category", "created_by").all()
    serializer_class = ProductSerializer

    # Default permission is IsAuthenticated, but we relax READS for everyone.
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        # create/update/destroy require a staff or admin role
        return [permissions.IsAdminUser()]

    # Declarative browsing: ?search, ?ordering, and our own ?is_available=
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Per-request queryset tweaks: filter by is_available query param."""
        qs = super().get_queryset()
        flag = self.request.query_params.get("is_available")
        if flag in ("true", "false"):
            qs = qs.filter(is_available=(flag == "true"))
        return qs

    def perform_create(self, serializer):
        """Auto-bind the authenticated user as the product creator."""
        serializer.save(created_by=self.request.user)
