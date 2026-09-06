# =============================================================================
# products/urls.py  --  DRF router wires the ViewSets to URLs automatically
# =============================================================================
# Router -> generates these RESTful routes from a ViewSet:
#   GET    /products/            list
#   POST   /products/            create
#   GET    /products/{id}/       retrieve
#   PUT    /products/{id}/       update
#   PATCH  /products/{id}/       partial update
#   DELETE /products/{id}/       destroy

from rest_framework.routers import DefaultRouter

from . import views

app_name = "products"

router = DefaultRouter()
router.register("products", views.ProductViewSet, basename="product")
router.register("categories", views.CategoryViewSet, basename="category")

urlpatterns = router.urls
