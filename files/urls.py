# =============================================================================
# files/urls.py
# =============================================================================
#   POST /api/files/upload/   -> upload a file (multipart)
#   GET  /api/files/          -> list my uploads

from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path("upload/", views.FileUploadView.as_view(), name="upload"),
    path("", views.FileListView.as_view(), name="list"),
]
