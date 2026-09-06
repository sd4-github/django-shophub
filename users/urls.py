# =============================================================================
# users/urls.py  --  routes for the users app
# =============================================================================

from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("users/register/", views.RegisterView.as_view(), name="register"),
    path("users/me/", views.MeView.as_view(), name="me"),
]
