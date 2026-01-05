from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from catalog.models import Book
from circulation.models import Loan
from accounts.models import User
from repository.models import Document
from events.models import Event
from .serializers import BookSerializer, LoanSerializer, UserSerializer, DocumentSerializer, EventSerializer


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.filter(is_active=True)
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'publisher']
    search_fields = ['title', 'isbn', 'authors__first_name', 'authors__last_name', 'description']
    ordering_fields = ['title', 'created_at', 'publication_date']
    ordering = ['-created_at']


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'user']
    ordering_fields = ['checkout_date', 'due_date']
    ordering = ['-checkout_date']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['membership_type']
    search_fields = ['username', 'email', 'first_name', 'last_name']


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.filter(is_active=True, is_approved=True)
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'collection', 'department', 'year']
    search_fields = ['title', 'author', 'abstract', 'keywords']
    ordering_fields = ['submission_date', 'title']
    ordering = ['-submission_date']


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.filter(is_published=True, is_cancelled=False)
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'title']
    ordering = ['start_date']
