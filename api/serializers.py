from rest_framework import serializers
from catalog.models import Book, Author, Genre, Publisher
from circulation.models import Loan
from accounts.models import User
from repository.models import Document
from events.models import Event


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'full_name']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug', 'description']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'slug', 'website']


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    genre = GenreSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'subtitle', 'isbn', 'isbn13', 'authors', 'publisher',
            'genre', 'publication_date', 'edition', 'language', 'pages',
            'description', 'cover_image', 'total_copies', 'available_copies',
            'location', 'call_number', 'is_featured', 'created_at'
        ]


class LoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Loan
        fields = [
            'id', 'user', 'user_username', 'book', 'book_title', 'copy',
            'checkout_date', 'due_date', 'return_date', 'status',
            'renewed_count', 'max_renewals', 'created_at'
        ]
        read_only_fields = ['user', 'checkout_date', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'membership_type', 'phone_number', 'is_active', 'date_joined'
        ]
        read_only_fields = ['date_joined']


class DocumentSerializer(serializers.ModelSerializer):
    collection_name = serializers.CharField(source='collection.name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'subtitle', 'document_type', 'collection', 'collection_name',
            'author', 'department', 'faculty', 'publication_date', 'year',
            'abstract', 'keywords', 'access_level', 'download_count', 'view_count',
            'submission_date', 'is_featured'
        ]


class EventSerializer(serializers.ModelSerializer):
    registration_count = serializers.IntegerField(source='registrations.count', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'event_type', 'start_date',
            'end_date', 'location', 'venue', 'is_online', 'online_link',
            'capacity', 'requires_registration', 'registration_fee',
            'registration_count', 'is_featured', 'created_at'
        ]

