"""
URL configuration for unimaid_library project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('catalog/', include('catalog.urls')),
    path('circulation/', include('circulation.urls')),
    path('repository/', include('repository.urls')),
    path('blog/', include('blog.urls')),
    path('events/', include('events.urls')),
    path('analytics/', include('analytics.urls')),
    path('api/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Ramat Library Administration"
admin.site.site_title = "Ramat Library Admin"
admin.site.index_title = "Welcome to Ramat Library Administration"
