from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('genre/<slug:slug>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('search/', views.BookSearchView.as_view(), name='book_search'),
]

