from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self) -> None:
        """Register signal receivers when the app is loaded.
           Must not do DB work here (migrations may not have run yet)."""
        import orders.signals  # noqa: F401
