# =============================================================================
# files/models.py  --  an UploadedFile record
# =============================================================================
# Shows how uploaded files are persisted + associated with a User.
#
#   * FileField(upload_to=...) : Django stores the file under MEDIA_ROOT and
#     keeps only the path in this column. No Pillow needed for FileField
#     (Pillow is only required for ImageField).
#   * We snapshot safe client metadata (original_name, size, content_type)
#     alongside, so we can build audit info and the GET download endpoint.

from django.conf import settings
from django.db import models


class UploadedFile(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploads",
    )
    file = models.FileField(upload_to="uploads/%Y/%m/")   # MEDIA_ROOT/...
    original_name = models.CharField(max_length=255)
    size = models.PositiveBigIntegerField(default=0)
    content_type = models.CharField(max_length=120, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-uploaded_at",)

    def __str__(self) -> str:
        return f"{self.original_name} by {self.owner}"
