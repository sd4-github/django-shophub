# =============================================================================
# files/views.py  --  file upload + listing endpoints (pure backend)
# =============================================================================
# DRF APIView style (most explicit) for the upload, to show exactly what a
# multipart upload does:
#   1. Validate with UploadSerializer (size cap).
#   2. Stream to disk via our fileops utility (safe filename + chunked write).
#   3. Record an UploadedFile row with metadata.
#   4. Return the file's public URL.
#
# DEPENDENCY NOTE: Django's FileField storage handles the actual file when you
# set it from an UploadedFile; we ALSO show a manual chunked save via fileops
# to demonstrate raw Python file writing (see python_scripts/04_file_operations.py).

from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.db import transaction

from .fileops import allowed_extension, safe_filename
from .models import UploadedFile
from .serializers import UploadSerializer, UploadedFileSerializer

# Only these extensions may be uploaded (defense against malicious files).
ALLOWED = {".txt", ".md", ".json", ".csv", ".pdf", ".png", ".jpg", ".jpeg"}


class FileUploadView(APIView):
    """POST /api/files/upload/  (multipart/form-data with a `file` field)."""
    # multipart parsing is what lets Django read the file part.
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = UploadSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)

        uploaded = ser.validated_data["file"]
        original = safe_filename(uploaded.name)

        if not allowed_extension(original, ALLOWED):
            return Response(
                {"error": f"File type not allowed. Allowed: {sorted(ALLOWED)}"},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        # 1) MANUAL chunked save (demonstrates raw Python file I/O).
        dest_dir = settings.MEDIA_ROOT / "uploads"
        saved_path = None
        try:
            saved_path = self._manual_save(uploaded, dest_dir, original)
        except OSError as exc:
            return Response({"error": f"Upload failed: {exc}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 2) Record the DB row so we can list/download it.
        record = UploadedFile(
            owner=request.user,
            original_name=original,
            size=uploaded.size,
            content_type=uploaded.content_type or "application/octet-stream",
        )
        # Use Django storage (simpler + serves via MEDIA_URL); the manual save
        # above shows how a raw write works. We set file = the saved relative path.
        record.file.name = str(saved_path.relative_to(settings.MEDIA_ROOT))
        record.save()

        return Response(
            UploadedFileSerializer(record, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def _manual_save(self, uploaded, dest_dir, original):
        """Low-level chunked write of an upload to disk (see fileops)."""
        import os
        os.makedirs(dest_dir, exist_ok=True)
        dest = dest_dir / original
        with open(dest, "wb") as out:
            for chunk in uploaded.chunks():
                out.write(chunk)
        return dest


class FileListView(generics.ListAPIView):
    """GET /api/files/  -> list the authenticated user's uploads."""
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UploadedFile.objects.filter(owner=self.request.user)
