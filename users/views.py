# =============================================================================
# users/views.py  --  registration + current-user endpoints (DRF)
# =============================================================================
# We show TWO DRF view styles (both appear in interviews):
#   * APIView         : most explicit; you write get/post each as a method.
#   * generics.*      : pre-built mixins (CreateAPIView etc.) for CRUD.
#   * ViewSet + router: maximal sugar (used in products/orders apps).

from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/users/register/  -> create an account, return public user."""
    # Allow ANYONE to register (no auth required), but never leak password.
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    # CreateAPIView already saves and returns 201; we just return the created
    # user object (serializer.instance is set after save).


class MeView(generics.RetrieveAPIView):
    """GET /api/users/me/  -> return the currently authenticated user."""
    # Require authentication (default JWT IsAuthenticated since we did not
    # override permission_classes).
    serializer_class = UserSerializer

    def get_object(self):
        # `self.request.user` is the authenticated user injected by DRF's
        # authentication classes from the JWT (or session).
        return self.request.user
