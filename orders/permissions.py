# =============================================================================
# orders/permissions.py  --  a custom DRF object-level permission
# =============================================================================
# DRF permissions interview topics:
#   * Module-level : IsAuthenticated / IsAdminUser / AllowAny.
#   * has_object_permission(self, request, view, obj) lets you decide access
#     PER ROW. Here: owner or staff/admin can act; others can't.

from rest_framework.permissions import BasePermission


class IsOwnerOrStaff(BasePermission):
    """Allow access only to the row's owner, or staff/admin users."""

    # Object-level check (runs after the view fetched the object).
    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        # staff/admin can always access
        if user.is_staff or getattr(user, "role", "") == "admin":
            return True
        # otherwise, only the owner
        return getattr(obj, "user_id", None) == user.id
