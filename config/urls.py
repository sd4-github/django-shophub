"""
config/urls.py  --  project-wide URL routing (Django)
--------------------------------------------------------------------------
This is where every HTTP route is wired. Compare with FastAPI routers and
Flask blueprints — Django uses "URLconfs": a list of path()/re_path() rules.
Each app exposes its own urls.py, which we include here.

Also mounted:
  * JWT endpoints (login/refresh) from simplejwt — we use these for auth.
  * drf-spectacular's /api/schema/ (OpenAPI JSON) + /api/docs/ (Swagger UI).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Django built-in admin (kept for ops; the public API is via DRF below)
    path("admin/", admin.site.urls),

    # --- JWT authentication endpoints -----------------------------------
    # POST /api/auth/token/   -> {username/password} -> {access, refresh}
    # POST /api/auth/refresh/ -> {refresh}          -> new {access}
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # --- Our apps --------------------------------------------------------
    path("api/", include("users.urls")),
    path("api/", include("products.urls")),
    path("api/", include("orders.urls")),
    path("api/files/", include("files.urls")),

    # --- OpenAPI docs (drf-spectacular) ---------------------------------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

# Serve uploaded media locally in dev (pure backend: no Cloudinary/S3 here).
# In production you'd serve from S3/CDN and set MEDIA_ROOT accordingly.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

