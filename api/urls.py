from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet, basename='book')
router.register(r'loans', views.LoanViewSet, basename='loan')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'events', views.EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]

