# =============================================================================
# orders/urls.py  --  DRF router for orders
# =============================================================================
# The router turns OrderViewSet into these routes:
#   GET    /orders/             list (own orders unless staff)
#   POST   /orders/             create (with nested items)
#   GET    /orders/{id}/        retrieve
#   PATCH  /orders/{id}/        partial update
#   DELETE /orders/{id}/        destroy (restocks via signal)
#   POST   /orders/{id}/mark_paid/   (from the @action)
#   GET    /orders/stats/             (from the @action)

from rest_framework.routers import DefaultRouter

from . import views

app_name = "orders"

router = DefaultRouter()
router.register("orders", views.OrderViewSet, basename="order")

urlpatterns = router.urls
