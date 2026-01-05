from django.urls import path
from . import views

app_name = 'repository'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('collection/<slug:slug>/', views.CollectionDetailView.as_view(), name='collection_detail'),
    path('search/', views.DocumentSearchView.as_view(), name='document_search'),
]

