from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"

    def ready(self):
        # Customize User admin after all apps are loaded
        from django.contrib import admin
        from django.contrib.auth.models import User
        from .admin import CustomUserAdmin

        try:
            admin.site.unregister(User)
        except admin.sites.NotRegistered:
            pass

        admin.site.register(User, CustomUserAdmin)
