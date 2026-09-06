# =============================================================================
# users/serializers.py  --  DRF serializers for the User model
# =============================================================================
# DRF serializers are the Django equivalent of FastAPI's Pydantic schemas /
# Flask's Marshmallow schemas: they validate input and serialize output.
#
# Key concepts:
#   * ModelSerializer auto-generates fields from a model.
#   * write_only=True      : field used for input but never returned in output.
#   * read_only=True       : field shown in output but ignored on input.
#   * validate_<field>()   : per-field validation hooks.
#   * DRF's serializer.save() calls model.save() / calls create()/update().

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user (what the API returns)."""
    class Meta:
        model = User
        fields = ("id", "email", "role", "is_staff", "is_active", "date_joined")
        read_only_fields = fields      # clients can't set these directly


class RegisterSerializer(serializers.ModelSerializer):
    """Input for creating a user. Password is write-only (never returned)."""
    # validate.RelatedField... we just enforce min length via DRF validators.
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("id", "email", "password", "role")
        read_only_fields = ("id",)

    def validate_email(self, value: str) -> str:
        """Per-field hook: reject duplicate emails *before* trying to create."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data: dict) -> User:
        # We must create via the manager so the password is hashed,
        # NOT via User.objects.create (which would store it in plaintext).
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )
