

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Set admin site titles to match the institution
admin.site.site_header = "Unimaid Library Administration"
admin.site.site_title = "Unimaid Library Administration"
admin.site.index_title = "Unimaid Library Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("blog/", include("apps.blog.urls", namespace="blog")),
    path("staff/", include("apps.staff.urls", namespace="staff")),
    path("repository/", include("apps.repository.urls", namespace="repository")),
    path("catalog/", include("apps.catalog.urls", namespace="catalog")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
