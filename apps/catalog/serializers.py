from rest_framework import serializers
from .models import Book, Author, Publisher, Genre, BookCopy, Loan, Reservation


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model"""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Author
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "bio",
            "birth_date",
            "death_date",
            "website",
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher model"""

    class Meta:
        model = Publisher
        fields = ["id", "name", "address", "website", "contact_email"]


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model"""

    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "description"]


class BookCopySerializer(serializers.ModelSerializer):
    """Serializer for BookCopy model"""

    class Meta:
        model = BookCopy
        fields = [
            "id",
            "copy_number",
            "barcode",
            "status",
            "condition",
            "location",
            "acquisition_date",
            "purchase_price",
            "is_reference_only",
        ]


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model"""

    authors = AuthorSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    copies = BookCopySerializer(many=True, read_only=True)
    available_copies = serializers.IntegerField(read_only=True)
    total_copies = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "slug",
            "isbn",
            "isbn13",
            "authors",
            "publisher",
            "genres",
            "description",
            "publication_date",
            "edition",
            "pages",
            "language",
            "cover_image",
            "sample_pages",
            "date_added",
            "last_updated",
            "available_copies",
            "total_copies",
        ]
        read_only_fields = ["slug", "date_added", "last_updated"]


class LoanSerializer(serializers.ModelSerializer):
    """Serializer for Loan model"""

    patron_name = serializers.CharField(
        source="patron.user.get_full_name", read_only=True
    )
    book_title = serializers.CharField(source="book_copy.book.title", read_only=True)
    book_copy_number = serializers.CharField(
        source="book_copy.copy_number", read_only=True
    )
    issued_by_name = serializers.CharField(
        source="issued_by.get_full_name", read_only=True
    )
    returned_to_name = serializers.CharField(
        source="returned_to.get_full_name", read_only=True
    )

    class Meta:
        model = Loan
        fields = [
            "id",
            "patron",
            "patron_name",
            "book_copy",
            "book_title",
            "book_copy_number",
            "loan_date",
            "due_date",
            "returned_date",
            "status",
            "fine_amount",
            "fine_paid",
            "issued_by",
            "issued_by_name",
            "returned_to",
            "returned_to_name",
            "notes",
        ]
        read_only_fields = ["patron", "issued_by", "returned_to", "fine_amount"]


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for Reservation model"""

    patron_name = serializers.CharField(
        source="patron.user.get_full_name", read_only=True
    )
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "patron",
            "patron_name",
            "book",
            "book_title",
            "reservation_date",
            "expiry_date",
            "status",
            "ready_date",
            "pickup_deadline",
            "notes",
        ]
        read_only_fields = ["patron"]
