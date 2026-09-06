# =============================================================================
# files/serializers.py  --  serializers for the files app
# =============================================================================

from rest_framework import serializers

from .models import UploadedFile


class UploadSerializer(serializers.Serializer):
    """Accepts a multipart file upload: {file} (and optional name)."""
    file = serializers.FileField()               # from request.FILES
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate_file(self, value):
        """Basic safety: cap upload size (e.g. 10MB)."""
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File is too large (max 10MB).")
        return value


class UploadedFileSerializer(serializers.ModelSerializer):
    """Read-only representation of an upload, incl. a usable download URL."""
    url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = ("id", "original_name", "size", "content_type", "uploaded_at", "url")
        read_only_fields = fields

    def get_url(self, obj: UploadedFile) -> str | None:
        """Build an absolute URL to the stored file.
           self.context["request"] lets us reuse the current host."""
        request = self.context.get("request")
        if not obj.file:
            return None
        if request is None:
            return obj.file.url
        return request.build_absolute_uri(obj.file.url)
