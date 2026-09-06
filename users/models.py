# =============================================================================
# users/models.py  --  custom User model (email login)
# =============================================================================
# WHY A CUSTOM USER MODEL? (top Django interview answer)
#   * Best/strongest Django practice: set AUTH_USER_MODEL on day one, because
#     swapping the user model AFTER your first migration is painful.
#   * It lets us log in with EMAIL instead of username, and add fields.
#
# How email login works:
#   * USERNAME_FIELD='email' tells authentication to treat email as the unique
#     identifier used at login.
#   * REQUIRED_FIELDS=[] means createsuperuser only asks for email+password.
#   * We subclass BaseUserManager to provide create_user/create_superuser that
#     normalise the email (downcasing) and set the password via set_password.

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager so createsuperuser works with our email-based User."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        # Normalise: lowercase the domain part of the email.
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)          # hashes the password (PBKDF2)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Our custom user: email-based login + a simple role field."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        STAFF = "staff", "Staff"
        ADMIN = "admin", "Admin"

    # 'email' replaces 'username' as the login field.
    username = None                              # remove the username field
    email = models.EmailField("email address", unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    # Meta + manager wiring.
    objects = UserManager()
    USERNAME_FIELD = "email"                     # what is used to authenticate
    REQUIRED_FIELDS = []                         # only email+password needed

    def __str__(self) -> str:
        return self.email
