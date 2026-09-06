# =============================================================================
# files/admin.py  --  Django admin for UploadedFile records
# =============================================================================
# Shows uploaded file metadata in the admin so you can audit what was uploaded,
# by whom, and when. Useful for ops teams managing user-uploaded content.

from django.contrib import admin

from .models import UploadedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "owner", "size", "content_type", "uploaded_at")
    list_filter = ("content_type", "uploaded_at")
    search_fields = ("original_name", "owner__email")
