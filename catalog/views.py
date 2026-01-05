from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Book, Genre, Author


class BookListView(ListView):
    model = Book
    template_name = 'catalog/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Book.objects.filter(is_active=True).select_related('publisher', 'genre').prefetch_related('authors')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(isbn__icontains=search_query) |
                Q(authors__first_name__icontains=search_query) |
                Q(authors__last_name__icontains=search_query) |
                Q(description__icontains=search_query)
            ).distinct()
        
        # Filter by genre
        genre_slug = self.request.GET.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'
    
    def get_queryset(self):
        return Book.objects.filter(is_active=True).select_related('publisher', 'genre').prefetch_related('authors', 'copies')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_copies'] = self.object.copies.filter(status='available')
        return context


class GenreDetailView(DetailView):
    model = Genre
    template_name = 'catalog/genre_detail.html'
    context_object_name = 'genre'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(genre=self.object, is_active=True)
        return context


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.filter(is_active=True)
        return context


class BookSearchView(ListView):
    model = Book
    template_name = 'catalog/book_search.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Book.objects.filter(
                Q(title__icontains=query) |
                Q(isbn__icontains=query) |
                Q(authors__first_name__icontains=query) |
                Q(authors__last_name__icontains=query) |
                Q(description__icontains=query)
            ).distinct().filter(is_active=True)
        return Book.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
